from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QTabWidget, QLabel, QPushButton, QWidget, QHBoxLayout

from api.timer import TimerTabAPI
from tabs.base_tab import BaseNudgyTab
from ui.timer_tab_init import Ui_timer_tab

from api.timer import Timer


class TimerTab(BaseNudgyTab):
    UI_OBJECT = Ui_timer_tab
    TAB_LABEL = "Timer"

    TIMER_STEP_MS = 10  # 0.01 second accuracy

    DEFAULT_TIMER = Timer("", 0, is_main_timer=True)

    def __init__(self, parent_tab_widget: QTabWidget):
        super().__init__(parent_tab_widget)

        # Create the API endpoint
        self.api = TimerTabAPI()

        # Create the QTimer
        self.timer_obj = QTimer(self)
        self.timer_obj.setInterval(self.TIMER_STEP_MS)
        self.timer_obj.timeout.connect(self.timer_tick)

        # State variables
        self.active_timer = None
        self.timer_value = None
        self.timer_running = None
        self.timer_paused = None

        # Load timers from the database
        if not self.load_timers():
            # If no timers were loaded, set the default timer
            self.set_main_timer(self.DEFAULT_TIMER)

        # Make UI connections
        self.ui.start_time_line_edit.editingFinished.connect(self.timer_duration_edited)
        self.ui.start_stop_button.pressed.connect(self.start_stop_timer)
        self.ui.pause_resume_button.pressed.connect(self.pause_resume_timer)
        self.ui.save_button.pressed.connect(self.save_timer)

        
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
            self.timer_obj.stop()
            self.reset_timer()
            self.ui.start_stop_button.setText("Start")
            self.ui.pause_resume_button.setText("Pause")
            self.ui.pause_resume_button.setEnabled(False)
        else:
            # Start the timer
            self.timer_running = True
            self.timer_obj.start()
            self.ui.start_stop_button.setText("Stop")
            self.ui.pause_resume_button.setEnabled(True)

    def pause_resume_timer(self):
        if self.timer_paused:
            # Resume the timer
            self.timer_paused = False
            self.timer_obj.start()
            self.ui.pause_resume_button.setText("Pause")
        else:
            # Pause the timer
            self.timer_paused = True
            self.timer_obj.stop()
            self.ui.pause_resume_button.setText("Resume")

    def timer_duration_edited(self):
        new_text = self.ui.start_time_line_edit.text()
        try:
            # Use the input value (rounded to 2 decimals)
            new_value = round(float(new_text), 2)
            self.ui.start_time_line_edit.setText(str(new_value))
            self.active_timer.duration_sec = new_value

            self.reset_timer()

        except ValueError:
            # If the input is invalid, just reset the line edit to the previous value
            self.ui.start_time_line_edit.setText(str(self.active_timer.duration_sec))
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
        self.timer_obj.stop()
        # Wait 1 second before resetting the timer (aesthetic)
        QTimer.singleShot(1000, self.reset_timer)

    def reset_timer(self):
        # Reset the timer to its original state
        self.timer_running = False
        self.timer_value = self.active_timer.duration_sec
        self.update_display()

    def set_main_timer(self, timer_obj: Timer):
        self.timer_obj.stop()
        self.timer_running: bool = False
        self.timer_paused: bool = False
        self.active_timer = timer_obj
        self.active_timer.is_main_timer = True
        self.api.set_timer_as_active(self.active_timer)
        self.timer_value = timer_obj.duration_sec
        self.ui.start_time_line_edit.setText(str(round(self.timer_value, 2)))
        self.ui.timer_name_edit.setText(self.active_timer.name)
        self.update_display()

    def _add_timer_to_scroll_area(self, timer: Timer):
        # Container widget for a single timer
        row_widget = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(4, 2, 4, 2)
        row_layout.setSpacing(10)
        row_widget.setLayout(row_layout)

        # Labels
        name_label = QLabel(timer.name)
        duration_label = QLabel(f"{timer.duration_sec:.2f}s")

        # Buttons
        load_button = QPushButton("Load")
        load_button.setFixedWidth(50)
        delete_button = QPushButton("Delete")
        delete_button.setFixedWidth(50)
        row_layout.addWidget(name_label)
        row_layout.addWidget(duration_label)
        row_layout.addStretch()
        row_layout.addWidget(load_button)
        row_layout.addWidget(delete_button)

        self.ui.saved_timers_layout.insertWidget(0, row_widget)

        def on_load_clicked():
            self.set_main_timer(timer)

        def on_delete_clicked():
            # Remove from database
            self.api.delete_timer(timer)
            # Remove from UI
            row_widget.setParent(None)

        # Connect button callbacks
        load_button.clicked.connect(on_load_clicked)
        delete_button.clicked.connect(on_delete_clicked)

    def save_timer(self):
        """Save the current active timer to the database"""
        self.active_timer.name = self.ui.timer_name_edit.text()
        # Don't add duplicate timers
        if not self.api.check_timer_in_db(self.active_timer):
            self.api.add_timer(self.active_timer)
            self._add_timer_to_scroll_area(self.active_timer)


    def load_timers(self) -> bool:
        """
        Load all timers from the database into the saved timers display
        (Returns True if any timers were loaded, otherwise False)
        """
        all_timers = self.api.get_all_timers()
        for timer in all_timers:
            self._add_timer_to_scroll_area(timer)
            if timer.is_main_timer:
                self.set_main_timer(timer)
        
        return bool(all_timers)