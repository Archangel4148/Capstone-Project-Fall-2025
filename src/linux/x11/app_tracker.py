import chardet
import os
import psutil
import subprocess

def get_active_window_linux_x11() -> str:
    # doesn't support wayland since there isn't a consistent method for doing so that's also supported by multiple compositors.
    proc = subprocess.Popen(["xdotool", "getactivewindow"], stdout=subprocess.PIPE).stdout.read()
    encoding = chardet.detect(proc)["encoding"]
    proc = str(proc, encoding=encoding).strip()

    proc = subprocess.Popen(["xdotool", "getwindowpid", proc], stdout=subprocess.PIPE).stdout.read()
    encoding = chardet.detect(proc)["encoding"]
    pid = str(proc, encoding=encoding).strip()
    pid = int(pid)

    path = psutil.Process(pid).exe()
    return os.path.realpath(path)

def get_exe_name_linux(exe_path: str) -> str:
    pass
