import os
import psutil
import win32api
import win32gui
import win32process

def get_active_window_windows_nt() -> str:
    proc = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(proc)

    path = psutil.Process(pid).exe()
    return os.path.realpath(path)

def get_exe_name_windows_nt(exe_path: str) -> str:
    try:
        language, codepage = win32api.GetFileVersionInfo(exe_path, "\\VarFileInfo\\Translation")[0]
        language = hex(language)[2:].rjust(4, "0")
        codepage = hex(codepage)[2:].rjust(4, "0")

        sub_block = f"\\StringFileInfo\\{language}{codepage}\\FileDescription"
        description = win32api.GetFileVersionInfo(exe_path, sub_block)
    except:
        description = os.path.basename(exe_path)

    return description
