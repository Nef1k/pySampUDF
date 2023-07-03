from ctypes import windll, wintypes


def virtual_protect_ex():
    VirtualProtectEx = windll.kernel32.VirtualProtectEx  # noqa
    VirtualProtectEx.argtypes = (
        wintypes.HANDLE,  # HANDLE hProcess
        wintypes.LPVOID,  # lpAddress
        wintypes.SIZE,    # dwSize
        wintypes.DWORD,   # flNewProtect
        wintypes.PDWORD,  # lpflOldProtect
    )
    VirtualProtectEx.restype = wintypes.BOOL
    print(VirtualProtectEx)
