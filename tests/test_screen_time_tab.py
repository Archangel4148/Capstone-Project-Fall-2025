


import sys
from unittest.mock import MagicMock

import pytest
from api import screen_time
from api.database_service import DatabaseService
from api.screen_time import App, AppTimestamp, ScreenTimeAPI
from tabs.screen_time_tab import ScreenTimeTab

@pytest.fixture(autouse=True)
def reset_apps():
    # Reset the DB and the app_skip_tracker
    screen_time._app_skip_tracker = 1
    DatabaseService.delete(
        table_name="screen_time",
        conditions=None
    )


def test_get_application_usage(temp_db):
    api = ScreenTimeAPI()

    api.add_entry(AppTimestamp("/bin/app1", 100))
    api.add_entry(AppTimestamp("/bin/app1", 101))
    api.add_entry(AppTimestamp("/bin/app2", 200))

    apps = api.get_application_usage()

    paths = {a.get_path() for a in apps}
    assert paths == {"/bin/app1", "/bin/app2"}

    app1 = next(a for a in apps if a.get_path() == "/bin/app1")
    assert app1.num_timestamps() == 2 * app1.SKIP_RATE

def test_delete_after_date(temp_db):
    api = ScreenTimeAPI()

    api.add_entry(AppTimestamp("/bin/app", 100))
    api.add_entry(AppTimestamp("/bin/app", 200))

    api.delete_after_date(150)

    apps = api.get_application_usage()
    app = apps[0]

    assert app.num_timestamps() == 1 * app.SKIP_RATE

def test_delete_after_date(temp_db):
    api = ScreenTimeAPI()

    api.add_entry(AppTimestamp("/bin/app", 100))
    api.add_entry(AppTimestamp("/bin/app", 200))

    api.delete_after_date(150)

    apps = api.get_application_usage()
    app = apps[0]

    assert app.num_timestamps() == 1 * app.SKIP_RATE

def test_remove_app(temp_db):
    api = ScreenTimeAPI()

    api.add_entry(AppTimestamp("/bin/app1", 100))
    api.add_entry(AppTimestamp("/bin/app2", 200))

    api.remove_app("/bin/app1")

    apps = api.get_application_usage()
    assert len(apps) == 1
    assert apps[0].get_path() == "/bin/app2"

def test_app_add_timestamp_calls_db_every_skip(mocker):
    api_mock = mocker.patch("api.screen_time.ScreenTimeAPI.add_entry")

    app = App("Test", "/bin/app")

    for i in range(App.SKIP_RATE):
        app.add_timestamp(i)

    # Only one DB insert should happen
    api_mock.assert_called_once()

def test_num_timestamps_with_history():
    app = App("Test", "/bin/app", timestamps=[10, 20, 30])

    assert app.num_timestamps(end_time=15) == 2 * app.SKIP_RATE

def test_toggle_app_tracking(qtbot, mocker):
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    tab.timer = MagicMock()
    tab.timer.isActive.return_value = False

    tab.toggle_app_tracking()
    tab.timer.start.assert_called_once()

    tab.timer.isActive.return_value = True
    tab.toggle_app_tracking()
    tab.timer.stop.assert_called_once()

def test_log_application(qtbot, mocker, temp_db):
    mocker.patch("tabs.screen_time_tab.get_active_window", return_value="/bin/app")
    mocker.patch("time.time", return_value=1000)

    mocker.patch("api.screen_time._app_skip_tracker", 60)  # Puts it on the edge of incrementing

    tab = ScreenTimeTab(parent_tab_widget=MagicMock())
    tab.api = ScreenTimeAPI()

    tab.log_application()

    apps = tab.api.get_application_usage()
    assert len(apps) == 1
    assert apps[0].num_timestamps() >= 1 * apps[0].SKIP_RATE

def test_set_history_sec_from_ui_text(qtbot, mocker):
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    tab.ui.screen_time_history = MagicMock()
    tab.update_time_actual = MagicMock()
    tab.update_time_percent = MagicMock()

    # Fake apps
    app1 = MagicMock()
    app1.num_timestamps.return_value = 2

    app2 = MagicMock()
    app2.num_timestamps.return_value = 3

    tab._apps = [app1, app2]

    # Empty string: sys.maxsize
    tab.ui.screen_time_history.text.return_value = ""
    tab.set_history_sec(0)

    assert tab._history_sec == sys.maxsize
    assert tab._total_time_sec == (2 + 3) * tab.REFRESH_RATE_SEC
    tab.update_time_actual.assert_called_once()
    tab.update_time_percent.assert_called_once()

def test_set_history_sec_invalid_text_returns_early(qtbot):
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    tab.ui.screen_time_history = MagicMock()
    tab.ui.screen_time_history.text.return_value = "not-a-number"

    tab.update_time_actual = MagicMock()
    tab.update_time_percent = MagicMock()

    original_history = tab._history_sec

    tab.set_history_sec(0)

    # No changes, no updates
    assert tab._history_sec == original_history
    tab.update_time_actual.assert_not_called()
    tab.update_time_percent.assert_not_called()

def test_set_history_sec_same_value_no_op(qtbot):
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    tab.update_time_actual = MagicMock()
    tab.update_time_percent = MagicMock()

    tab._history_sec = 1234

    tab.set_history_sec(1234)

    tab.update_time_actual.assert_not_called()
    tab.update_time_percent.assert_not_called()

def test_init_sets_rows_for_existing_apps(qtbot, mocker):
    app = App("TestApp", "/bin/test", timestamps=[100, 200])

    mocker.patch(
        "tabs.screen_time_tab.ScreenTimeAPI.get_application_usage",
        return_value=[app],
    )

    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    # set_row should have populated at least one row
    assert tab.ui.screen_time_table_widget.rowCount() == 1

def test_get_row_returns_existing_row(qtbot):
    # Check that get_row returns the same row for the same path
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())
    path = "/bin/app"

    # First call creates the row
    row1 = tab.get_row(path)
    tab.ui.screen_time_table_widget.item(row1, tab.PATH_COL).setText(path)
    
    # Should return the same row
    row2 = tab.get_row(path)
    assert row1 == row2

def test_set_history_sec_negative_input_uses_maxsize(qtbot):
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    tab.ui.screen_time_history.setText("-5")
    tab.set_history_sec(0)

    assert tab._history_sec == sys.maxsize

def test_set_history_sec_accumulates_total_time(qtbot):
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    app = App("Test", "/bin/test", timestamps=[100, 200])
    tab._apps = [app]

    tab.set_history_sec(sys.maxsize)

    assert tab._total_time_sec > 0
