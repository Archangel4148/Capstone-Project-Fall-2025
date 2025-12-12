import time

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QTableWidgetItem, QTabWidget

from api.screen_time import AppTimestamp, ScreenTimeAPI
from tabs.base_tab import BaseNudgyTab
from ui.screen_time_tab_init import Ui_screen_time_tab
from system.active_window import get_active_window
from system.exe_names import get_exe_names


class ScreenTimeTab(BaseNudgyTab):
    UI_OBJECT = Ui_screen_time_tab
    TAB_LABEL = "Screen Time"

    REFRESH_RATE_SEC = 5
    REFRESH_RATE_MS = REFRESH_RATE_SEC * 1000

    def __init__(self, parent_tab_widget: QTabWidget) -> None:
        super().__init__(parent_tab_widget)

        # Create the API endpoint
        self.api = ScreenTimeAPI()

        # Make UI connections
        self.ui.update_screen_time_button.pressed.connect(self.toggle_app_tracking)
        self.timer = QTimer(self)
        self.timer.setInterval(self.REFRESH_RATE_MS)
        self.timer.timeout.connect(self.log_application)

        self.ui.screen_time_table_widget.setItem(0, 0, QTableWidgetItem())

        self._usage = ScreenTimeAPI().get_application_usage()

        for a in self._usage:
            self.add_row(a)

    def add_row(self, exe: AppTimestamp) -> None:
        app_name = get_exe_names([exe.path])

        row = self.ui.screen_time_table_widget.rowCount()
        self.ui.screen_time_table_widget.insertRow(row)
        self.ui.screen_time_table_widget.setItem(row, 0, QTableWidgetItem(app_name[exe.path]))
        self.ui.screen_time_table_widget.setItem(row, 1, QTableWidgetItem(str(exe.query_timestamp)))

    def toggle_app_tracking(self) -> None:
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start()

    def log_application(self) -> None:
        app = AppTimestamp(get_active_window(), int(time.time()))
        self.api.add_entry(app)
        self.add_row(app)
