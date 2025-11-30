import configparser
import glob
import os
import re

class _MatchExeToDesktop():
    def __init__(self, exe_path: str) -> None:
        self._exe_path = exe_path
        self._result = os.path.basename(exe_path)

    def _result_found(self) -> bool:
        return self._exe_path == self._result

    def _search_desktop_file(self, file_path: str) -> None:
        config = configparser.ConfigParser()
        config.read(file_path)

        exec = ""
        try:
            exec = config.get("Desktop Entry", "Exec", raw=True).split()
        except configparser.NoOptionError:
            pass

        if self._exe_path in exec or os.path.basename(self._exe_path) in exec:
            self._result = config.get("Desktop Entry", "Name", raw=True)

    def _search_desktop_files(self, dir: str) -> None:
        for f in glob.glob(f"{dir}/**", recursive=True):
            if not re.match(".*\\.desktop$", f):
                continue

            self._search_desktop_file(f)

            if self._result_found():
                break

    def main(self) -> str:
        for d in os.environ["XDG_DATA_DIRS"].split(":"):
            d = f"{d}/applications"

            self._search_desktop_files(d)

            if self._result_found():
                break

        return self._result

def get_exe_name(exe_path: str) -> str:
    return _MatchExeToDesktop(exe_path).main()
