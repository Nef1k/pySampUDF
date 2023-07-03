from __future__ import annotations

import struct
from pathlib import Path
from time import sleep
from typing import List

import psutil
import win32api
import win32con
import win32process
import win32event
from winnt import NULL, MEM_RELEASE, MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE

from samp.exceptions import InvalidArgumentError
from samp.utils import put_uint, put_int, put_uchar, put_ushort


class Pointer:
    def __init__(self, addr):
        self.addr = addr


class GtaInstance:
    PROCESS_NAME = 'gta_sa.exe'
    ENCODING = 'cp1251'
    STR_READ_CHUNK_SIZE = 32

    def __init__(self, process: psutil.Process):
        self.process = process
        self.gta_handle = None
        self.samp_address = None

        self._slots_count = 10
        self._slot_size = 1024
        self._alloc_size = (self._slots_count + 1) * self._slot_size

        self._memory_start_ptr = None
        self._arg_pointers = []
        self._thread_entry_point = None

    @classmethod
    def discover_instances(cls) -> List[GtaInstance]:
        gta_procs = []
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.name() == cls.PROCESS_NAME:
                gta_procs.append(proc)
        return [
            cls(psutil.Process(proc.pid))
            for proc in gta_procs
        ]

    def open(self):
        if not self.process:
            raise ValueError('PID is invalid')

        self.gta_handle = win32api.OpenProcess(
            win32con.PROCESS_ALL_ACCESS, False, self.process.pid,
        )
        self.samp_address = self.get_module_base_address('samp.dll')
        self._init_aux_memory()

    def close(self):
        if not self.gta_handle:
            return

        self._free_aux_memory()
        self.samp_address = None
        win32api.CloseHandle(self.gta_handle)
        self.gta_handle = None

    def _init_aux_memory(self):

        self._memory_start_ptr = win32process.VirtualAllocEx(
            self.gta_handle, NULL, self._alloc_size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)

        for i in range(0, self._slots_count):
            self._arg_pointers.append(self._memory_start_ptr + self._slot_size * i)
        self._thread_entry_point = self._memory_start_ptr + self._slots_count * self._slot_size

    def _free_aux_memory(self):
        win32process.VirtualFreeEx(self.gta_handle, self._memory_start_ptr, 0, MEM_RELEASE)
        self._memory_start_ptr = None
        self._arg_pointers = []
        self._thread_entry_point = None

    def read_mem(self, address, length) -> bytes:
        if not self.gta_handle:
            raise ValueError(f'Cannot read value at addr {address}: process not opened')

        return win32process.ReadProcessMemory(self.gta_handle, address, length)

    def write_mem(self, address, buffer: bytes):
        return win32process.WriteProcessMemory(self.gta_handle, address, buffer)

    def read_float(self, address) -> float:
        res = self.read_mem(address, 4)
        return struct.unpack('f', res)[0]

    def read_int32(self, address) -> int:
        res = self.read_mem(address, 4)
        return int.from_bytes(res, byteorder='little', signed=True)

    def read_dword(self, address) -> int:
        res = self.read_mem(address, 4)
        return int.from_bytes(res, 'little')

    def read_string(self, address, max_length: int = 250) -> str:
        chars_processed = 0
        current_chunk = 0
        result = bytearray()
        while chars_processed <= max_length:
            chunk = self.read_mem(address + current_chunk * self.STR_READ_CHUNK_SIZE, self.STR_READ_CHUNK_SIZE)
            eol = False
            for b in chunk:
                if b == 0x00:
                    eol = True
                    break

                result.append(b)
            if eol:
                break

            current_chunk += 1
            chars_processed += self.STR_READ_CHUNK_SIZE

        return bytes(result).decode(self.ENCODING)

    def write_string(self, address, string: str):
        b = string.encode(self.ENCODING)
        if b[-1] != 0x00:
            b = b + b'\0'
        return self.write_mem(address, b)

    def get_module_base_address(self, module_name: str):
        module_handles = win32process.EnumProcessModulesEx(
            self.gta_handle, win32process.LIST_MODULES_ALL)
        for module_handle in module_handles:
            name = win32process.GetModuleFileNameEx(self.gta_handle, module_handle)
            module_path = Path(name)
            if module_path.name == module_name:
                return module_handle

        return None

    def call_with_params(self, func_addr, args: list, cleanup_stack: bool = True, wait_timeout: int = 0):
        args_number = len(args)
        buffer_length = args_number * 5 + 5 + 1  # 5 * push + call + ret
        if cleanup_stack:
            buffer_length += 3  # add esp, <byte> = 3 bytes

        inject_data = bytearray(0 for _ in range(0, buffer_length))
        str_param_idx = 0
        for i, arg in enumerate(reversed(args)):
            if isinstance(arg, Pointer):
                push_arg = arg.addr
            elif isinstance(arg, str):
                if str_param_idx > len(self._arg_pointers):
                    raise InvalidArgumentError(f'Not enough argument slots allocated. Argument idx: {str_param_idx}')

                push_arg = self._arg_pointers[str_param_idx]
                self.write_string(self._arg_pointers[str_param_idx], arg)
                str_param_idx += 1
            elif isinstance(arg, int):
                push_arg = arg
            else:
                raise InvalidArgumentError(f'Argument of type {type(arg).__name__} is not supported')

            put_uchar(0x68, inject_data, i * 5)  # PUSH
            put_uint(push_arg, inject_data, i * 5 + 1)

        func_offset = func_addr - (self._thread_entry_point + args_number * 5 + 5)
        put_uchar(0xE8, inject_data, args_number * 5)  # CALL
        put_int(func_offset, inject_data, args_number * 5 + 1)

        if cleanup_stack:
            put_ushort(0xC483, inject_data, args_number * 5 + 5)  # ADD esp
            put_uchar(args_number * 4, inject_data, args_number * 5 + 7)

            put_uchar(0xC3, inject_data, args_number * 5 + 8)  # RET
        else:
            put_uchar(0xC3, inject_data, args_number * 5 + 5)  # RET

        self.write_mem(self._thread_entry_point, bytes(inject_data))

        thread_handle, thread_id = win32process.CreateRemoteThread(
            self.gta_handle, None, 0, self._thread_entry_point, 0, 0)

        win32event.WaitForSingleObject(thread_handle, 0)
        sleep(0.1)

        win32api.CloseHandle(thread_handle)

        return inject_data
