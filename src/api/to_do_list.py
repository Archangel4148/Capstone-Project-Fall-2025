from api.database_service import DatabaseService
import dataclasses

@dataclasses.dataclass

class To_Do_Item:
    description: str
    due_date: str
    include_calendar_item: bool

class ToDoListAPI:
    def get_all_items(self) -> list[To_Do_Item]:
        # Select all rows from the database
        rows = DatabaseService.select(table_name="to_do_list", columns=None, conditions=None)
        # Build the To_Do_Item objects
        items = [To_Do_Item(*row) for row in rows]
        return items


    def delete_item(self, selected_item: To_Do_Item) -> None:
        # Delete the selected to do list item from the database
        DatabaseService.delete(table_name="to_do_list", conditions=[("to_do_item_id", "=", selected_item.description)])

    def add_item(self, item: To_Do_Item) -> None:
        # Add the provided item to the database
        DatabaseService.insert(table_name="to_do_list", values={"description": item.description, "due_date" : item.due_date, "include_calendar" : item.include_calendar_item})
