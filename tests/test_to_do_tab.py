
import pytest
from api.to_do_list import ToDoListAPI, To_Do_Item
from unittest.mock import MagicMock
from api.database_service import DatabaseService
from tabs.to_do_list_tab import ToDoListTab

@pytest.fixture
def clean_todo_table(temp_db):
    # Delete all to-do items in the DB (for clean testing)
    DatabaseService.delete(
        table_name="to_do_list",
        conditions=None
    )

def make_todo_item(
    task_id=1,
    desc="Task",
    due="2025-01-01",
    include=False,
):
    return To_Do_Item(
        taskID=task_id,
        description=desc,
        due_date=due,
        include_calendar_item=include,
    )


def test_add_and_get_all_items(temp_db, clean_todo_table):
    # Check that adding an item and getting all items works
    api = ToDoListAPI()
    item = To_Do_Item(1, "Homework", "2025-01-01", False)

    api.add_item(item)
    items = api.get_all_items()

    assert len(items) == 1
    assert items[0].description == "Homework"


def test_delete_item(temp_db, clean_todo_table):
    # Check that deleting an item removes it from the DB
    api = ToDoListAPI()
    item = To_Do_Item(1, "Chores", "2025-01-02", False)

    api.add_item(item)
    api.delete_item(item)

    items = api.get_all_items()
    assert items == []

def test_tab_loads_saved_items(temp_db, qtbot, clean_todo_table):
    # Check that creating a new ToDoListTab loads items from the DB
    api = ToDoListAPI()
    api.add_item(To_Do_Item(1, "Test Task", "2025-01-01", False))

    tab = ToDoListTab(parent_tab_widget=MagicMock())

    assert tab.ui.listWidget.count() == 1
    assert "Test Task" in tab.ui.listWidget.item(0).text()

def test_add_item_adds_to_db_and_ui(temp_db, qtbot, mocker):
    # Check that tab.addItem() adds to the list widget
    tab = ToDoListTab(parent_tab_widget=MagicMock())

    tab.ui.task_description_line_edit = MagicMock()
    tab.ui.due_date_time_edit = MagicMock()
    tab.ui.include_calendar_item_check_box = MagicMock()
    tab.ui.listWidget = MagicMock()

    tab.ui.task_description_line_edit.text.return_value = "New Task"
    tab.ui.due_date_time_edit.text.return_value = "2025-02-01"
    tab.ui.include_calendar_item_check_box.isChecked.return_value = True
    tab.ui.listWidget.count.return_value = 0

    api_mock = mocker.patch("tabs.to_do_list_tab.ToDoListAPI")
    api_instance = api_mock.return_value

    tab.addItem()

    api_instance.add_item.assert_called_once()
    tab.ui.listWidget.addItem.assert_called_once()

def test_delete_item_removes_from_db_and_ui(temp_db, qtbot, mocker):
    # Check that deleting an item removes it from the UI and deletes from the DB
    tab = ToDoListTab(parent_tab_widget=MagicMock())

    tab.ui.listWidget = MagicMock()
    tab.ui.listWidget.currentRow.return_value = 0

    item_mock = MagicMock()
    item_mock.text.return_value = "Task To Delete Due: 2025-01-01"
    tab.ui.listWidget.item.return_value = item_mock

    api_mock = mocker.patch("tabs.to_do_list_tab.ToDoListAPI")
    api_instance = api_mock.return_value

    tab.deleteItem()

    api_instance.delete_item.assert_called_once()
    tab.ui.listWidget.takeItem.assert_called_once_with(0)

