import time

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QTableWidgetItem, QTabWidget

from api.screen_time import App, AppTimestamp, ScreenTimeAPI
from tabs.base_tab import BaseNudgyTab
from ui.screen_time_tab_init import Ui_screen_time_tab
from system.active_window import get_active_window
from system.exe_names import get_exe_names

class ScreenTimeTab(BaseNudgyTab):
    UI_OBJECT = Ui_screen_time_tab
    TAB_LABEL = "Screen Time"
    DECIMAL_RESOLUTION = 1
    NAME_COL, PATH_COL, TIME_ACTUAL_COL, TIME_PERCENT_COL = range(4)
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
        self._total_time_sec: int = 0

        for u in self._usage:
            self._total_time_sec += len(u.get_timestamps()) * self.REFRESH_RATE_SEC

        for a in self._usage:
            self.set_row(a)

    def get_app(self, path: str) -> App:
        for a in self._usage:
            if a.get_path() == path:
                return a

        self._usage.append(App(get_exe_names([path])[path], path))
        return self._usage[-1]

    def get_row(self, path: str) -> int:
        rows = self.ui.screen_time_table_widget.findItems(
            path,
            Qt.MatchExactly
        )

        if len(rows) == 0:
            row = self.ui.screen_time_table_widget.rowCount()
            self.ui.screen_time_table_widget.insertRow(row)

            self.ui.screen_time_table_widget.setItem(row, self.NAME_COL, QTableWidgetItem())
            self.ui.screen_time_table_widget.setItem(row, self.PATH_COL, QTableWidgetItem())
            self.ui.screen_time_table_widget.setItem(row, self.TIME_ACTUAL_COL, QTableWidgetItem())
            self.ui.screen_time_table_widget.setItem(row, self.TIME_PERCENT_COL, QTableWidgetItem())

            return row

        return rows[0].row()

    def set_row(self, app: App) -> None:
        self.ui.screen_time_table_widget.setSortingEnabled(False)

        row = self.get_row(app.get_path())

        name = app.get_name()
        path = app.get_path()
        time_mins = (len(app.get_timestamps()) * self.REFRESH_RATE_SEC) / 60
        time_mins = str(round(time_mins, self.DECIMAL_RESOLUTION))
        time_percent = len(app.get_timestamps()) * 100 / self._total_time_sec
        time_percent = str(round(time_percent, self.DECIMAL_RESOLUTION))

        self.ui.screen_time_table_widget.item(row, 0).setText(name)
        self.ui.screen_time_table_widget.item(row, 1).setText(path)
        self.ui.screen_time_table_widget.item(row, 2).setText(time_mins)
        self.ui.screen_time_table_widget.item(row, 3).setText(time_percent)

        self.ui.screen_time_table_widget.setSortingEnabled(True)

    def toggle_app_tracking(self) -> None:
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start()

    def log_application(self) -> None:
        app_timestamp = AppTimestamp(get_active_window(), int(time.time()))

        app = self.get_app(app_timestamp.path)
        app.add_timestamp(app_timestamp.query_timestamp)
        self.set_row(app)
