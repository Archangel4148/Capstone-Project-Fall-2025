import chardet
import os
import psutil
import subprocess

def get_active_window() -> str:
    # doesn't support wayland since there isn't a consistent method for doing so that's also supported by multiple compositors.
    # doesn't support flatpak since it runs in a protected environment.
    proc = subprocess.Popen(["xdotool", "getactivewindow"], stdout=subprocess.PIPE).stdout.read()
    encoding = chardet.detect(proc)["encoding"]
    proc = str(proc, encoding=encoding).strip()

    proc = subprocess.Popen(["xdotool", "getwindowpid", proc], stdout=subprocess.PIPE).stdout.read()
    encoding = chardet.detect(proc)["encoding"]
    pid = str(proc, encoding=encoding).strip()
    pid = int(pid)

    path = ""
    try:
        path = psutil.Process(pid).exe()
        path = os.path.realpath(path)
    except psutil.AccessDenied:
        pass

    return path
