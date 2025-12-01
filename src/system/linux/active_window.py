import logging
import os

def get_active_window() -> str:
    match os.environ["XDG_SESSION_TYPE"]:
        case "x11":
            import system.linux.x11.active_window as active_window

        case _:
            logging.error(f"Unsupported operating system: {sys.platform}")

    return active_window.get_active_window()
