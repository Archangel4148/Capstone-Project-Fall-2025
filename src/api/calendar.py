import dataclasses

from src.api.database_service import DatabaseService


@dataclasses.dataclass
class CalendarItem:
    calendar_item_id: int
    datetime: str
    event_name: str
    event_description: str
    duration: int
    include_to_do_task: bool
    has_reminder: bool


class CalendarAPI:
    def get_all_items(self) -> list[CalendarItem]:
        # Select all rows from the database
        rows = DatabaseService.select(table_name="calendar", columns=None, conditions=None)
        # Build the CalendarItem objects
        items = [CalendarItem(*row) for row in rows]
        return items

    def delete_item(self, selected_item: CalendarItem) -> None:
        # Delete the selected calendar item from the database
        DatabaseService.delete(table_name="calendar", conditions=[("calendar_item_id", "=", selected_item.calendar_item_id)])

    def add_item(self, item: CalendarItem) -> None:
        # Add the provided item to the database
        DatabaseService.insert(table_name="calendar", values={"datetime": item.datetime, "event_name" : item.event_name, "event_description" : item.event_description, "duration" : item.duration, "include_to_do_task" : item.include_to_do_task, "has_reminder" : item.has_reminder})
