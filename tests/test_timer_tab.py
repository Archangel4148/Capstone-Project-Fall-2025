import pytest
from unittest.mock import MagicMock
from tabs.timer_tab import TimerTab
from api.timer import Timer, TimerTabAPI
from api.database_service import DatabaseService


def test_format_time():
    # Check formatting for times
    assert TimerTab.format_time(62.34) == "01:02.34"
    assert TimerTab.format_time(0) == "00:00.00"


def test_blink_label_toggles_colors(qtbot):
    # Check if the blink state updates properly with _blink_label
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.timer_label = MagicMock()
    tab.blink_state = False

    tab._blink_label()
    assert tab.blink_state is True
    tab._blink_label()
    assert tab.blink_state is False


def test_reset_timer_sets_state(qtbot, mocker):
    # Check if resetting the timer resets the button text and stops the alarm
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.start_stop_button = MagicMock()
    tab.ui.pause_resume_button = MagicMock()
    tab.ui.timer_label = MagicMock()

    tab.active_timer = Timer("Test", 10, True)
    tab.timer_running = True
    tab.timer_value = 5

    mock_callback = mocker.Mock()
    tab.stop_alarm_callback = mock_callback
    tab.blink_timer = mocker.Mock()

    tab.reset_timer()

    assert tab.timer_running is False
    assert tab.timer_value == 10
    tab.ui.start_stop_button.setText.assert_called_with("Start")
    tab.ui.pause_resume_button.setText.assert_called_with("Pause")

    mock_callback.assert_called_once()
    assert tab.stop_alarm_callback is None

    # It should stop blinking and set the color to black
    tab.blink_timer.stop.assert_called_once()
    tab.ui.timer_label.setStyleSheet.assert_called_with("color: black;")


def test_add_and_check_timer_in_db():
    # Check if api.add_timer() successfully adds the timer to the DB
    api = TimerTabAPI()
    t = Timer("MyTimer", 10, True)

    api.add_timer(t)
    found = api.check_timer_in_db(t)

    assert found is True
    timers = api.get_all_timers()
    assert any(timer.name == "MyTimer" for timer in timers)


def test_timer_finished_triggers(mocker, qtbot):
    # Test that the alarm triggers on timer finish
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.start_stop_button = MagicMock()
    tab.ui.pause_resume_button = MagicMock()
    tab.ui.timer_label = MagicMock()

    mock_sound = mocker.patch("tabs.timer_tab.play_looping_sound")

    tab.active_timer = Timer("Alarm", 1, True)
    tab.timer_value = 0
    tab.timer_finished()

    mock_sound.assert_called_once()


def test_timer_duration_edited_valid_and_invalid(qtbot):
    # Check that editing the text successfully updates values, and that invalid inputs are ignored
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.start_time_line_edit = MagicMock()
    tab.active_timer = Timer("Test", 5, True)

    # Valid input
    tab.ui.start_time_line_edit.text.return_value = "12.34"
    tab.timer_duration_edited()
    assert tab.active_timer.duration_sec == 12.34

    # Invalid input
    tab.ui.start_time_line_edit.text.return_value = "notanumber"
    tab.timer_duration_edited()
    assert tab.active_timer.duration_sec == 12.34


def test_add_timer_calls_callbacks(qtbot, ):
    # Check that the buttons all successfully trigger timer adding/loading
    tab = TimerTab(parent_tab_widget=MagicMock())
    
    # Mock layout to check buttons
    from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton
    layout_widget = QWidget()
    layout = QVBoxLayout(layout_widget)
    tab.ui.saved_timers_layout = layout

    tab.set_main_timer = MagicMock()
    tab.api.delete_timer = MagicMock()

    t = Timer("Temp", 1, False)
    tab._add_timer_to_scroll_area(t)

    row_widget = layout.itemAt(0).widget()
    load_button = row_widget.findChildren(QPushButton)[0]
    delete_button = row_widget.findChildren(QPushButton)[1]

    # Press the Load button
    load_button.clicked.emit()
    tab.set_main_timer.assert_called_with(t)

    # Press the Delete button
    delete_button.clicked.emit()
    tab.api.delete_timer.assert_called_with(t)

def test_start_stop_timer_starts_and_stops(qtbot, temp_db):
    # Test that start/stop timer actually starts/stops the timer
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.start_stop_button = MagicMock()
    tab.ui.pause_resume_button = MagicMock()

    # Make a timer
    tab.active_timer = Timer("Test", 1, True)
    tab.timer_value = 1
    tab.timer_running = False

    # Start the timer
    tab.start_stop_timer()
    assert tab.timer_running is True
    tab.ui.start_stop_button.setText.assert_called_with("Stop")

    # Stop the timer
    tab.start_stop_timer()
    assert tab.timer_running is False
    tab.ui.start_stop_button.setText.assert_called_with("Start")

    # Make sure the alarm was canceled
    tab.stop_alarm_callback = MagicMock()
    tab.start_stop_timer()
    assert tab.stop_alarm_callback is None

def test_pause_resume_timer(qtbot, temp_db):
    # Test that pause/resume actually pauses/resumes the timer
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.pause_resume_button = MagicMock()
    tab.timer_obj = MagicMock()

    # Pause
    tab.timer_paused = False
    tab.pause_resume_timer()
    assert tab.timer_paused is True
    tab.ui.pause_resume_button.setText.assert_called_with("Resume")

    # Resume
    tab.pause_resume_timer()
    assert tab.timer_paused is False
    tab.ui.pause_resume_button.setText.assert_called_with("Pause")

def test_timer_tick(qtbot, temp_db, mocker):
    # Test that the timer behaves on a tick (either decrementing or finishing)
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.timer_label = MagicMock()
    tab.timer_obj = MagicMock()

    mock_play = mocker.patch("tabs.timer_tab.play_looping_sound")

    # Timer finish
    tab.set_main_timer(Timer("Test", 0.01, True))
    tab.timer_running = True
    tab.timer_obj.stop = MagicMock()
    tab.timer_tick()
    mock_play.assert_called_once()
    assert tab.timer_value == 0

    # Normal tick (no finish)
    tab.set_main_timer(Timer("Test", 0.02, True))
    tab.timer_running = True
    tab.timer_obj.stop = MagicMock()
    tab.timer_tick()
    assert tab.timer_value == 0.02 - (tab.TIMER_STEP_MS / 1000)


def test_save_timer_adds_new_timer(qtbot, temp_db):
    # Check that save_timer adds the timer to the DB
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.timer_name_edit = MagicMock()
    tab.ui.saved_timers_layout = MagicMock()
    tab.active_timer = Timer("NewTimer", 1, True)

    tab.ui.timer_name_edit.text.return_value = "NewTimer"

    tab.api.check_timer_in_db = MagicMock(return_value=False)
    tab.api.add_timer = MagicMock()
    tab._add_timer_to_scroll_area = MagicMock()

    # Save the timer and check
    tab.save_timer()
    tab.api.add_timer.assert_called_once_with(tab.active_timer)
    tab._add_timer_to_scroll_area.assert_called_once_with(tab.active_timer)

def test_save_timer_skips_duplicate(qtbot, temp_db):
    # Test that saving a duplicate timer does not add to the DB
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.timer_name_edit = MagicMock()
    tab.active_timer = Timer("DupTimer", 1, True)

    tab.ui.timer_name_edit.text.return_value = "DupTimer"

    tab.api.check_timer_in_db = MagicMock(return_value=True)
    tab.api.add_timer = MagicMock()
    tab._add_timer_to_scroll_area = MagicMock()

    # Make sure the duplicate wasn't added in the API
    tab.save_timer()
    tab.api.add_timer.assert_not_called()
    tab._add_timer_to_scroll_area.assert_not_called()

def test_delete_timer_removes_from_db(temp_db):
    # Check that delete_timer actually removes from the DB
    api = TimerTabAPI()
    t = Timer("DeleteMe", 5, False)

    # Add a timer and make sure it's really there
    api.add_timer(t)
    assert api.check_timer_in_db(t) is True

    # Delete the timer, and make sure it's gone
    api.delete_timer(t)
    assert api.check_timer_in_db(t) is False

    all_timers = api.get_all_timers()
    assert all(timer.name != "DeleteMe" for timer in all_timers)
