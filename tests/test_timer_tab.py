import pytest
from unittest.mock import MagicMock
from tabs.timer_tab import TimerTab
from api.timer import Timer, TimerTabAPI
from api.database_service import DatabaseService


def test_format_time():
    assert TimerTab.format_time(62.34) == "01:02.34"
    assert TimerTab.format_time(0) == "00:00.00"


def test_blink_label_toggles_colors(qtbot):
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.timer_label = MagicMock()
    tab.blink_state = False

    tab._blink_label()
    assert tab.blink_state is True
    tab._blink_label()
    assert tab.blink_state is False


def test_reset_timer_sets_state(qtbot, mocker):
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.start_stop_button = MagicMock()
    tab.ui.pause_resume_button = MagicMock()
    tab.ui.timer_label = MagicMock()

    tab.active_timer = Timer("Test", 10, True)
    tab.timer_running = True
    tab.timer_value = 5

    # Add a mock stop_alarm_callback and mock blink_timer.stop
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
    api = TimerTabAPI()
    t = Timer("MyTimer", 10, True)

    api.add_timer(t)
    found = api.check_timer_in_db(t)

    assert found is True
    timers = api.get_all_timers()
    assert any(timer.name == "MyTimer" for timer in timers)


def test_timer_finished_triggers(mocker, qtbot):
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
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.start_time_line_edit = MagicMock()
    tab.active_timer = Timer("Test", 5, True)

    tab.ui.start_time_line_edit.text.return_value = "12.34"
    tab.timer_duration_edited()
    assert tab.active_timer.duration_sec == 12.34

    # Invalid input
    tab.ui.start_time_line_edit.text.return_value = "notanumber"
    tab.timer_duration_edited()
    # Should remain unchanged
    assert tab.active_timer.duration_sec == 12.34


def test_add_timer_calls_callbacks(qtbot, ):
    tab = TimerTab(parent_tab_widget=MagicMock())
    
    # Build a mock layout to check buttons
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

    load_button.clicked.emit()
    tab.set_main_timer.assert_called_with(t)

    delete_button.clicked.emit()
    tab.api.delete_timer.assert_called_with(t)

def test_start_stop_timer_starts_and_stops(qtbot, temp_db):
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

    # Alarm stopping
    tab.stop_alarm_callback = MagicMock()
    tab.start_stop_timer()
    assert tab.stop_alarm_callback is None

def test_pause_resume_timer(qtbot, temp_db):
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.pause_resume_button = MagicMock()
    tab.timer_obj = MagicMock()

    tab.timer_paused = False
    tab.pause_resume_timer()
    assert tab.timer_paused is True
    tab.ui.pause_resume_button.setText.assert_called_with("Resume")

    tab.pause_resume_timer()
    assert tab.timer_paused is False
    tab.ui.pause_resume_button.setText.assert_called_with("Pause")

def test_timer_tick(qtbot, temp_db, mocker):
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.timer_label = MagicMock()
    tab.timer_obj = MagicMock()

    mock_play = mocker.patch("tabs.timer_tab.play_looping_sound")

    # Test a finishing timer
    tab.set_main_timer(Timer("Test", 0.01, True))
    tab.timer_running = True
    tab.timer_obj.stop = MagicMock()
    tab.timer_tick()
    mock_play.assert_called_once()
    assert tab.timer_value == 0

    # Test a normal decrement (no finish)
    tab.set_main_timer(Timer("Test", 0.02, True))
    tab.timer_running = True
    tab.timer_obj.stop = MagicMock()
    tab.timer_tick()
    assert tab.timer_value == 0.02 - (tab.TIMER_STEP_MS / 1000)


def test_save_timer_adds_new_timer(qtbot, temp_db):
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.timer_name_edit = MagicMock()
    tab.ui.saved_timers_layout = MagicMock()
    tab.active_timer = Timer("NewTimer", 1, True)

    tab.ui.timer_name_edit.text.return_value = "NewTimer"

    # Force check_timer_in_db to return False so it saves
    tab.api.check_timer_in_db = MagicMock(return_value=False)
    tab.api.add_timer = MagicMock()
    tab._add_timer_to_scroll_area = MagicMock()

    tab.save_timer()
    tab.api.add_timer.assert_called_once_with(tab.active_timer)
    tab._add_timer_to_scroll_area.assert_called_once_with(tab.active_timer)

def test_save_timer_skips_duplicate(qtbot, temp_db):
    tab = TimerTab(parent_tab_widget=MagicMock())
    tab.ui.timer_name_edit = MagicMock()
    tab.active_timer = Timer("DupTimer", 1, True)

    tab.ui.timer_name_edit.text.return_value = "DupTimer"

    tab.api.check_timer_in_db = MagicMock(return_value=True)
    tab.api.add_timer = MagicMock()
    tab._add_timer_to_scroll_area = MagicMock()

    tab.save_timer()
    tab.api.add_timer.assert_not_called()
    tab._add_timer_to_scroll_area.assert_not_called()