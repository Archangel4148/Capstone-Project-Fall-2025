#!/usr/bin/env python3
from PyQt5.QtWidgets import QWidget, QApplication

from api.database_service import DatabaseService
from tabs.calendar_tab import CalendarTab
from tabs.screen_time_tab import ScreenTimeTab
from tabs.timer_tab import TimerTab
from tabs.to_do_list_tab import ToDoListTab
from ui.main_window_init import Ui_main_window
# import chardet
import os
import psutil
import subprocess
import win32gui
import win32process

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

def get_active_window_windows_nt() -> str:
    proc = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(proc)

    path = psutil.Process(pid).exe()
    return os.path.realpath(path)

class MainWindow(QWidget):
    def __init__(self, default_start_time: float = 0.0):
        super().__init__()
        self.ui = Ui_main_window()
        self.ui.setupUi(self)

        # Set up the database
        DatabaseService.initialize()

        # Create the tabs
        self.screen_time_tab = ScreenTimeTab(self.ui.pages_tab_widget)
        self.calendar_tab = CalendarTab(self.ui.pages_tab_widget)
        self.to_do_list_tab = ToDoListTab(self.ui.pages_tab_widget)
        self.timer_tab = TimerTab(self.ui.pages_tab_widget, default_start_time)

if __name__ == '__main__':
    # Create the application (required)
    # app = QApplication([])

    # Create and show the main window
    # main_window = MainWindow(default_start_time=90)
    # main_window.show()

    # Execute the app (required)
    # app.exec_()
    print(get_active_window_windows_nt())
