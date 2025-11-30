import sys

def get_exe_names(exe_paths: list[str]) -> dict[str, str]:
    match sys.platform:
        case "linux":
            import system.linux.exe_names as exe_names

        case "win32":
            import system.win.exe_names as exe_names

    return exe_names.get_exe_names(exe_paths)
