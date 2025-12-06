from api.database_service import DatabaseService
import dataclasses

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

    def delete_timer(self, selected_timer: Timer) -> None:
        # Delete the selected timer from the database
        DatabaseService.delete(table_name="timer", conditions=[("timer_id", "=", selected_timer.duration_sec)])

    def add_timer(self, timer: Timer) -> None:
        # Add the provided Timer to the database
        DatabaseService.insert(table_name="timer", values={"duration": timer.duration_sec})
