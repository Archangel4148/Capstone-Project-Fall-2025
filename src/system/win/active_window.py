import os
import psutil
import win32gui
import win32process

def get_active_window() -> str:
    proc = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(proc)

    path = ""
    try:
        path = psutil.Process(pid).exe()
    except ValueError:
        pass

    return os.path.realpath(path)
