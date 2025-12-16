from api.database_service import DatabaseService
import dataclasses

@dataclasses.dataclass

class To_Do_Item:
    taskID: int
    description: str
    due_date: str
    include_calendar_item: bool = False

class ToDoListAPI:
    def get_all_items(self) -> list[To_Do_Item]:
        # Select all rows from the database
        rows = DatabaseService.select(table_name="to_do_list", columns=None, conditions=None)
        # Build the To_Do_Item objects
        items = [To_Do_Item(*row) for row in rows]
        return items


    def delete_item(self, selected_item: To_Do_Item) -> None:
        # Delete the selected to do list item from the database
        DatabaseService.delete(table_name="to_do_list", conditions=[("description", "=", selected_item.description)])

    def add_item(self, item: To_Do_Item) -> None:
        # Add the provided item to the database
        DatabaseService.insert(table_name="to_do_list", values={"description": item.description, "due_date" : item.due_date, "include_calendar_item" : item.include_calendar_item})
        if item.include_calendar_item:
            DatabaseService.insert(table_name="calendar", values=self.get_calendar_init_format(item))

    def get_calendar_init_format(self, item: To_Do_Item):
        return {
            "calendar_item_id": item.taskID,
            "datetime": item.due_date,
            "event_name": item.description.split()[0].title(),
            "event_description": item.description,
            "duration": 1,
            "include_to_do_task": False,
            "has_reminder": False,
        }