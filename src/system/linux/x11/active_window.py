import chardet
import os
import psutil
import subprocess

def get_active_window() -> str:
    # doesn't support wayland since there isn't a consistent method for doing so that's also supported by multiple compositors.
    # doesn't support flatpak since it runs in a protected environment.
    proc = subprocess.Popen(["xdotool", "getactivewindow"], stdout=subprocess.PIPE).stdout.read()
    encoding = chardet.detect(proc)["encoding"]
    try:
        proc = str(proc, encoding=encoding).strip()
    except TypeError:
        return ""

    proc = subprocess.Popen(["xdotool", "getwindowpid", proc], stdout=subprocess.PIPE).stdout.read()
    encoding = chardet.detect(proc)["encoding"]
    try:
        pid = str(proc, encoding=encoding).strip()
    except TypeError:
        return ""

    pid = int(pid)

    try:
        path = psutil.Process(pid).exe()
    except psutil.AccessDenied:
        return ""

    path = os.path.realpath(path)

    return path
