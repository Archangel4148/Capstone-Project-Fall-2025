from api.database_service import DatabaseService
import dataclasses

@dataclasses.dataclass
class Timer:
    name: str
    duration_sec: float
    is_main_timer: bool

class TimerTabAPI:
    def get_all_timers(self) -> list[Timer]:
        # Select all rows from the database
        rows = DatabaseService.select(table_name="timer", columns=None, conditions=None)
        # Build the Timer objects
        timers = [Timer(*row) for row in rows]
        return timers

    def check_timer_in_db(self, timer: Timer) -> bool:
        """Returns True if the provided Timer is present in the database, otherwise returns False"""
        matches = DatabaseService.select(
            table_name="timer",
            columns=None,
            conditions=[
                ("name", "=", timer.name),
                ("duration", "=", timer.duration_sec)
            ]
        )
        return len(matches) > 0

    def delete_timer(self, selected_timer: Timer) -> None:
        # Delete the selected timer from the database
        DatabaseService.delete(table_name="timer", conditions=[("name", "=", selected_timer.name), ("duration", "=", selected_timer.duration_sec)])

    def add_timer(self, timer: Timer) -> None:
        # Add the provided Timer to the database, and update is_main_timer for all other timers if necessary
        if timer.is_main_timer:
            DatabaseService.update(
                table_name="timer",
                values={"is_main_timer": False},
                conditions=None  # Check all timers
            )
        DatabaseService.insert(table_name="timer", values={"name": timer.name, "duration": timer.duration_sec, "is_main_timer": timer.is_main_timer})

    def set_timer_as_active(self, timer: Timer):
        # Deselect all other active timers
        DatabaseService.update(
            table_name="timer",
            values={"is_main_timer": False},
            conditions=None  # Check all timers
        )
        DatabaseService.update(
            table_name="timer",
            values={"is_main_timer": True},
            conditions=[("name", "=", timer.name), ("duration", "=", timer.duration_sec)]
        )