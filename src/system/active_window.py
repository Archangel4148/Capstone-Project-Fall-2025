import sys

def get_active_window() -> str:
    match sys.platform:
        case "linux":
            import system.linux.active_window as active_window

        case "win32":
            import system.win.active_window as active_window

    return active_window.get_active_window()
