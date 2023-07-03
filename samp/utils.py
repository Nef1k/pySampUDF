from functools import partial
from typing import Iterable, Union


def num_put(number: int, buffer: bytearray, offset: int = 0, *, length: int = 4, signed: bool = True):
    bs = number.to_bytes(length, 'little', signed=signed)
    for idx, b in enumerate(bs):
        buffer[idx + offset] = b


put_uint = partial(num_put, length=4, signed=False)
put_int = partial(num_put, length=4, signed=True)
put_uchar = partial(num_put, length=1, signed=False)
put_char = partial(num_put, length=1, signed=True)
put_ushort = partial(num_put, length=2, signed=False)
put_short = partial(num_put, length=2, signed=True)


def b2s(b) -> str:
    s = hex(b)
    s = s.replace('0x', '')
    if len(s) < 2:
        s = f'0{s}'

    return s


def safe_bytes(bs: Union[bytes, bytearray], encoding: str = 'utf-8') -> str:
    s = []
    for b in bs:
        if b == 0:
            s.append('.')
            continue

        try:
            s.append(bytes([b]).decode(encoding))
        except UnicodeDecodeError:
            s.append(bytes(0xE2).decode('utf-8'))

    return ''.join(s)


def dump_bytes(bs: Iterable, *, bytes_per_line: int = 16):
    current_line = bytearray()
    for idx, b in enumerate(bs):
        if idx % bytes_per_line == 0:
            print('', end='')

        print(f'{b2s(b)} ', end='')
        current_line.append(b)

        if idx % bytes_per_line == bytes_per_line - 1:
            print(f'')
            current_line = bytearray()
    print()
