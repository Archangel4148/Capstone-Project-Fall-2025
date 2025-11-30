import os
import psutil
import win32gui
import win32process

def get_active_window() -> str:
    proc = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(proc)

    path = psutil.Process(pid).exe()
    return os.path.realpath(path)
