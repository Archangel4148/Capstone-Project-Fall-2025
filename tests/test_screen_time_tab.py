


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
    # Check that get_application_usage returns the correct apps
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
    # Check that delete_after_date removes apps older than the given date
    api = ScreenTimeAPI()

    api.add_entry(AppTimestamp("/bin/app", 100))
    api.add_entry(AppTimestamp("/bin/app", 200))

    api.delete_after_date(150)

    apps = api.get_application_usage()
    app = apps[0]

    assert app.num_timestamps() == 1 * app.SKIP_RATE

def test_remove_app(temp_db):
    # Check that remove_app removes the app from the DB
    api = ScreenTimeAPI()

    api.add_entry(AppTimestamp("/bin/app1", 100))
    api.add_entry(AppTimestamp("/bin/app2", 200))

    api.remove_app("/bin/app1")

    apps = api.get_application_usage()
    assert len(apps) == 1
    assert apps[0].get_path() == "/bin/app2"

def test_app_add_timestamp_calls_db_every_skip(mocker):
    # Check that add_timestamp only adds to the DB once per skip
    api_mock = mocker.patch("api.screen_time.ScreenTimeAPI.add_entry")

    app = App("Test", "/bin/app")

    for i in range(App.SKIP_RATE):
        app.add_timestamp(i)

    # Only one DB insert should happen
    api_mock.assert_called_once()

def test_num_timestamps_with_history():
    # Check that num_timestamps returns the correct number of timestamps
    app = App("Test", "/bin/app", timestamps=[10, 20, 30])
    assert app.num_timestamps(end_time=15) == 2 * app.SKIP_RATE

def test_toggle_app_tracking(qtbot, mocker):
    # Check that toggle_app_tracking starts and stops the timer
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    tab.timer = MagicMock()
    tab.timer.isActive.return_value = False

    tab.toggle_app_tracking()
    tab.timer.start.assert_called_once()

    tab.timer.isActive.return_value = True
    tab.toggle_app_tracking()
    tab.timer.stop.assert_called_once()

def test_log_application(qtbot, mocker, temp_db):
    # Check that log_application adds the app to the DB
    mocker.patch("tabs.screen_time_tab.get_active_window", return_value="/bin/app")
    mocker.patch("time.time", return_value=1000)

    mocker.patch("api.screen_time._app_skip_tracker", 60)  # Puts it on the edge of incrementing

    tab = ScreenTimeTab(parent_tab_widget=MagicMock())
    tab.api = ScreenTimeAPI()

    tab.log_application()

    apps = tab.api.get_application_usage()
    assert len(apps) == 1
    assert apps[0].num_timestamps() >= 1 * apps[0].SKIP_RATE

def test_set_history_sec_invalid_text_returns_early(qtbot):
    # Check that set_history_sec returns early if the text is invalid
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    tab.ui.screen_time_history = MagicMock()
    tab.ui.screen_time_history.text.return_value = "not-a-number"

    tab.update_time_actual = MagicMock()
    tab.update_time_percent = MagicMock()

    original_history = tab._history_sec

    tab.set_history_sec()

    # No changes, no updates
    assert tab._history_sec == original_history
    tab.update_time_actual.assert_not_called()
    tab.update_time_percent.assert_not_called()

def test_set_history_sec_same_value_no_op(qtbot):
    # Check that set_history_sec does nothing if the value is the same
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    tab.update_time_actual = MagicMock()
    tab.update_time_percent = MagicMock()

    tab._history_sec = 1234

    tab.set_history_sec(1234)

    tab.update_time_actual.assert_not_called()
    tab.update_time_percent.assert_not_called()

def test_init_sets_rows_for_existing_apps(qtbot, mocker):
    # Check that init sets rows for existing apps
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
    # Check that set_history_sec uses the max size if the input is negative
    tab = ScreenTimeTab(parent_tab_widget=MagicMock())

    tab.ui.screen_time_history = MagicMock()
    tab.ui.screen_time_history.text.return_value = "-5"

    tab.set_history_sec()

    assert tab._history_sec == tab.DELETE_AFTER_SEC

def test_add_timestamps_calls_add_timestamp(mocker):
    # Check that add_timestamps calls add_timestamp for each timestamp
    app = App("Test", "/bin/app")
    mock_add = mocker.patch.object(app, "add_timestamp")

    timestamps = [100, 200, 300]
    app.add_timestamps(timestamps)

    assert mock_add.call_count == len(timestamps)
    mock_add.assert_any_call(100)
    mock_add.assert_any_call(200)
    mock_add.assert_any_call(300)
