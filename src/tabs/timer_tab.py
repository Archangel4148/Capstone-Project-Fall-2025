import dataclasses
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QTabWidget

from api.database_service import DatabaseService
from tabs.base_tab import BaseNudgyTab
from ui.timer_tab_init import Ui_timer_tab


class TimerTab(BaseNudgyTab):
    UI_OBJECT = Ui_timer_tab
    TAB_LABEL = "Timer"

    TIMER_STEP_MS = 10  # 0.01 second accuracy

    def __init__(self, parent_tab_widget: QTabWidget, default_start_time: float = 0.0):
        super().__init__(parent_tab_widget)

        # Create the API endpoint
        self.api = TimerTabAPI()

        # Default initial display value
        self.timer_value = self.start_time = default_start_time
        self.ui.start_time_line_edit.setText(str(round(default_start_time, 2)))
        self.update_display()

        # State flags for button tracking
        self.timer_running: bool = False
        self.timer_paused: bool = False

        # Create the timer
        self.timer = QTimer(self)
        self.timer.setInterval(self.TIMER_STEP_MS)
        self.timer.timeout.connect(self.timer_tick)

        # Make UI connections
        self.ui.start_time_line_edit.editingFinished.connect(self.start_time_edited)
        self.ui.start_stop_button.pressed.connect(self.start_stop_timer)
        self.ui.pause_resume_button.pressed.connect(self.pause_resume_timer)

    @staticmethod
    def format_time(seconds: float) -> str:
        # Format the time as MM:SS.HH
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        hundredths = int((seconds * 100) % 100)
        return f"{minutes:02d}:{secs:02d}.{hundredths:02d}"

    def update_display(self):
        # Update the timer display with the text formatted time
        self.ui.timer_label.setText(self.format_time(self.timer_value))

    def start_stop_timer(self):
        if self.timer_running:
            # Stop the timer and reset
            self.timer_running = False
            self.timer.stop()
            self.timer_value = self.start_time
            self.update_display()
            self.ui.start_stop_button.setText("Start")
            self.ui.pause_resume_button.setText("Pause")
            self.ui.pause_resume_button.setEnabled(False)
        else:
            # Start the timer
            self.timer_running = True
            self.timer.start()
            self.ui.start_stop_button.setText("Stop")
            self.ui.pause_resume_button.setEnabled(True)

    def pause_resume_timer(self):
        if self.timer_paused:
            # Resume the timer
            self.timer_paused = False
            self.timer.start()
            self.ui.pause_resume_button.setText("Pause")
        else:
            # Pause the timer
            self.timer_paused = True
            self.timer.stop()
            self.ui.pause_resume_button.setText("Resume")

    def start_time_edited(self):
        new_text = self.ui.start_time_line_edit.text()
        try:
            # Use the input value (rounded to 2 decimals)
            new_value = round(float(new_text), 2)
            self.timer_value = self.start_time = new_value
            self.ui.start_time_line_edit.setText(str(new_value))

            # Update the label with the new start time
            self.update_display()
        except ValueError:
            # If the input is invalid, just reset the line edit to the previous value
            self.ui.start_time_line_edit.setText(str(self.start_time))
            return

    def timer_tick(self):
        # Decrease the value by the timer step
        dt = self.TIMER_STEP_MS / 1000
        self.timer_value -= dt

        # Handle the timer finishing
        if self.timer_value <= 0.0:
            self.timer_value = 0.0
            self.update_display()
            self.timer_finished()
        else:
            self.update_display()

    def timer_finished(self):
        print("TIMER FINISHED")
        self.timer.stop()
        # Wait 1 second before resetting the timer (aesthetic)
        QTimer.singleShot(1000, self.reset_timer)

    def reset_timer(self):
        # Reset the timer to its original state
        self.timer_value = self.start_time
        self.update_display()
        self.start_stop_timer()

@dataclasses.dataclass
class Timer:
    duration_sec: float

class TimerTabAPI:
    def get_all_timers(self) -> list[Timer]:
        # Select all rows from the database
        rows = DatabaseService.select(table_name="timer", columns=None, conditions=None)
        # Build the Timer objects
        timers = [Timer(*row) for row in rows]
        return timers


    def delete_timer(self, selected_timer: Timer):
        # Delete the selected timer from the database
        DatabaseService.delete(table_name="timer", conditions=[("timer_id", "=", selected_timer.duration_sec)])

    def add_timer(self, timer: Timer):
        # Add the provided Timer to the database
        DatabaseService.insert(table_name="timer", values={"duration": timer.duration_sec})
