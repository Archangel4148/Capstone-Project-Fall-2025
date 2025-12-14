import sys
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
    DELETE_AFTER_DAYS = 30
    DELETE_AFTER_SEC = DELETE_AFTER_DAYS * 24 * 60 * 60
    DELETE_AFTER_DATE = int(time.time() - DELETE_AFTER_SEC)
    NAME_COL, PATH_COL, TIME_ACTUAL_COL, TIME_PERCENT_COL = range(4)
    REFRESH_RATE_SEC = 5
    REFRESH_RATE_MS = REFRESH_RATE_SEC * 1000

    def __init__(self, parent_tab_widget: QTabWidget) -> None:
        super().__init__(parent_tab_widget)

        self._total_time_sec: int = 0
        self._history_sec: int = sys.maxsize

        # Create the API endpoint
        self.api = ScreenTimeAPI()

        # Make UI connections
        self.ui.update_screen_time_button.pressed.connect(self.toggle_app_tracking)
        self.ui.screen_time_history.editingFinished.connect(self.set_history_sec)
        self.timer = QTimer(self)
        self.timer.setInterval(self.REFRESH_RATE_MS)
        self.timer.timeout.connect(self.log_application)

        # Load data
        self.api.delete_after_date(self.DELETE_AFTER_DATE)
        self._apps = ScreenTimeAPI().get_application_usage()

        for a in self._apps:
            self._total_time_sec += len(a.get_timestamps()) * self.REFRESH_RATE_SEC

        for a in self._apps:
            self.set_row(a)

    def get_app(self, path: str) -> App:
        for a in self._apps:
            if a.get_path() == path:
                return a

        self._apps.append(App(get_exe_names([path])[path], path))
        return self._apps[-1]

    def get_history_sec(self) -> int:
        return int(time.time() - self._history_sec)

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

    def set_history_sec(self) -> None:
        history_hrs = self.ui.screen_time_history.text()

        if history_hrs == self._history_sec:
            return

        self._history_sec = int(float(history_hrs) * 60 * 60)

        self._total_time_sec = 0
        for a in self._apps:
            self._total_time_sec += len(a.get_timestamps(self.get_history_sec())) * self.REFRESH_RATE_SEC

        self.update_time_actual()
        self.update_time_percent()

    def set_row(self, app: App) -> None:
        self.ui.screen_time_table_widget.setSortingEnabled(False)

        row = self.get_row(app.get_path())

        name = app.get_name()
        path = app.get_path()

        self.ui.screen_time_table_widget.item(row, self.NAME_COL).setText(name)
        self.ui.screen_time_table_widget.item(row, self.PATH_COL).setText(path)

        self.update_time_actual(False)
        self.update_time_percent(False)

        self.ui.screen_time_table_widget.setSortingEnabled(True)

    def update_time_actual(self, enable_sorting_after: bool=True) -> None:
        self.ui.screen_time_table_widget.setSortingEnabled(False)

        rows = self.ui.screen_time_table_widget.rowCount()
        for r in range(rows):
            path = self.ui.screen_time_table_widget.item(r, self.PATH_COL).text()
            app = self.get_app(path)

            time_hrs = (len(app.get_timestamps(self.get_history_sec())) * self.REFRESH_RATE_SEC) / (60 * 60)
            time_mins = (time_hrs - int(time_hrs)) * 60
            time_sec = (time_mins - int(time_mins)) * 60

            time_hrs = str(int(time_hrs)).rjust(2, "0")
            time_mins = str(int(time_mins)).rjust(2, "0")
            time_sec = str(int(time_sec)).rjust(2, "0")

            time_actual = f"{time_hrs}:{time_mins}:{time_sec}"

            self.ui.screen_time_table_widget.item(r, self.TIME_ACTUAL_COL).setText(time_actual)

        self.ui.screen_time_table_widget.setSortingEnabled(enable_sorting_after)

    def update_time_percent(self, enable_sorting_after: bool=True) -> None:
        self.ui.screen_time_table_widget.setSortingEnabled(False)

        rows = self.ui.screen_time_table_widget.rowCount()
        for r in range(rows):
            path = self.ui.screen_time_table_widget.item(r, self.PATH_COL).text()
            app = self.get_app(path)

            time_percent = 0
            try:
                time_percent = (len(app.get_timestamps(self.get_history_sec())) * self.REFRESH_RATE_SEC * 100) / self._total_time_sec
            except ZeroDivisionError:
                pass
            time_percent = str(round(time_percent, self.DECIMAL_RESOLUTION))
            time_percent = str(time_percent).rjust(len("100") + self.DECIMAL_RESOLUTION + 1, "0")

            self.ui.screen_time_table_widget.item(r, self.TIME_PERCENT_COL).setText(time_percent)

        self.ui.screen_time_table_widget.setSortingEnabled(enable_sorting_after)

    def toggle_app_tracking(self) -> None:
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start()

    def log_application(self) -> None:
        self._total_time_sec += self.REFRESH_RATE_SEC

        app_timestamp = AppTimestamp(get_active_window(), int(time.time()))
        app = self.get_app(app_timestamp.path)
        app.add_timestamp(app_timestamp.query_timestamp)

        self.set_row(app)
