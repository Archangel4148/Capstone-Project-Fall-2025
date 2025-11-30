import os
import win32api

def get_exe_name(exe_path: str) -> str:
    try:
        language, codepage = win32api.GetFileVersionInfo(exe_path, "\\VarFileInfo\\Translation")[0]
        language = hex(language)[2:].rjust(4, "0")
        codepage = hex(codepage)[2:].rjust(4, "0")

        sub_block = f"\\StringFileInfo\\{language}{codepage}\\FileDescription"
        description = win32api.GetFileVersionInfo(exe_path, sub_block)
    except:
        description = os.path.basename(exe_path)

    return description
