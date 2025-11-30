import chardet
import configparser
import glob
import os
import psutil
import re
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

class MatchExeToDesktop():
    def __init__(self, exe_path: str) -> None:
        self._exe_path = exe_path
        self._result = os.path.basename(exe_path)

    def _search_desktop_file(self, file_path: str) -> bool:
        pass

    def _search_desktop_files(self, dir: str) -> None:
        for f in glob.glob(f"{dir}/**", recursive=True):
            if not re.match("*\\.desktop"):
                continue

    def main(self) -> None:
        for d in os.environ["XDG_DATA_DIRS"].split(":"):
            d = f"{d}/applications"

            self._search_desktop_files(d)
