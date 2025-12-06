import os
import win32api

def _get_exe_name(exe_path: str) -> str:
    try:
        language, codepage = win32api.GetFileVersionInfo(exe_path, "\\VarFileInfo\\Translation")[0]
        language = hex(language)[2:].rjust(4, "0")
        codepage = hex(codepage)[2:].rjust(4, "0")

        sub_block = f"\\StringFileInfo\\{language}{codepage}\\FileDescription"
        exe_name = win32api.GetFileVersionInfo(exe_path, sub_block)
    except:
        exe_name = os.path.basename(exe_path)

    return exe_name

def get_exe_names(exe_paths: list[str]) -> dict[str, str]:
    results = dict()

    for e in exe_paths:
        results[e] = _get_exe_name(e)

    return results
