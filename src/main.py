#!/usr/bin/env python3
from PyQt5.QtWidgets import QWidget, QApplication

from api.database_service import DatabaseService
from tabs.calendar_tab import CalendarTab
from tabs.screen_time_tab import ScreenTimeTab
from tabs.timer_tab import TimerTab
from tabs.to_do_list_tab import ToDoListTab
from ui.main_window_init import Ui_main_window


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
    app = QApplication([])

    # Create and show the main window
    main_window = MainWindow(default_start_time=90)
    main_window.show()

    # Execute the app (required)
    app.exec_()
