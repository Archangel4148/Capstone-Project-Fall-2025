import configparser
import glob
import os
import re

class _MatchExeToDesktop():
    def __init__(self, exe_paths: str) -> None:
        self._exe_paths = exe_paths
        self._results = dict()

        for e in exe_paths:
            self._results[e] = os.path.basename(e)

    def _results_found(self) -> bool:
        return len(self._exe_paths) <= 0

    def _search_desktop_file(self, file_path: str) -> None:
        config = configparser.ConfigParser()
        config.read(file_path)

        exec = ""
        try:
            exec = config.get("Desktop Entry", "Exec", raw=True).split()
        except configparser.NoOptionError:
            pass

        i = 0
        while i < len(self._exe_paths):
            e = self._exe_paths[i]

            if e in exec or os.path.basename(e) in exec:
                self._results[e] = config.get("Desktop Entry", "Name", raw=True)
                self._exe_paths.pop(i)
                continue

            i += 1

    def _search_desktop_files(self, dir: str) -> None:
        for f in glob.glob(f"{dir}/**", recursive=True):
            if not re.match(".*\\.desktop$", f):
                continue

            self._search_desktop_file(f)

            if self._results_found():
                break

    def main(self) -> dict[str, str]:
        for d in os.environ["XDG_DATA_DIRS"].split(":"):
            d = f"{d}/applications"

            self._search_desktop_files(d)

            if self._results_found():
                break

        return self._results

def get_exe_names(exe_paths: list[str]) -> dict[str, str]:
    return _MatchExeToDesktop(exe_paths).main()
