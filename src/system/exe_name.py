import sys

def get_exe_name(exe_path: str) -> str:
    match sys.platform:
        case "linux":
            import system.linux.exe_name as exe_name

        case "win32":
            import system.win.exe_name as exe_name

    return exe_name.get_exe_name(exe_path)
