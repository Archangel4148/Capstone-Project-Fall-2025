import pytest
from api.calendar import CalendarAPI, CalendarItem

from unittest.mock import MagicMock
from PyQt5.QtCore import QDate

from api.database_service import DatabaseService
from tabs.calendar_tab import CalendarTab

@pytest.fixture
def clean_calendar_table(temp_db):
    # Delete all calendar items in the DB (for clean testing)
    DatabaseService.delete(
        table_name="calendar",
        conditions=None
    )

def make_item(id=1, name="Meeting", date="2025-01-01"):
    # Just an example item for testing
    return CalendarItem(
        calendar_item_id=id,
        datetime=f"{date} 09:00",
        event_name=name,
        event_description="Discuss stuff",
        duration=60,
        include_to_do_task=False,
        has_reminder=False,
    )


def test_update_selection_populates_ui(qtbot, mocker):
    # Check if a selection change updates the UI
    tab = CalendarTab(parent_tab_widget=MagicMock())

    tab.ui.calendar_widget = MagicMock()
    tab.ui.date_label = MagicMock()
    tab.ui.event_list = MagicMock()
    qdate = QDate(2025, 1, 1)
    tab.ui.calendar_widget.selectedDate.return_value = qdate

    item = make_item()
    tab.api.get_events_for_day = MagicMock(return_value=[item])

    # Update the selection and check that everything updated
    tab.update_selection()
    tab.ui.date_label.setText.assert_called_with("2025-01-01")
    tab.ui.event_list.clear.assert_called_once()
    tab.ui.event_list.addItem.assert_called_once()

    added_text = tab.ui.event_list.addItem.call_args[0][0]
    assert "Meeting" in added_text
    assert "60 minutes" in added_text


def test_update_selection_with_no_events(qtbot):
    tab = CalendarTab(parent_tab_widget=MagicMock())

    tab.ui.calendar_widget = MagicMock()
    tab.ui.date_label = MagicMock()
    tab.ui.event_list = MagicMock()

    tab.ui.calendar_widget.selectedDate.return_value = QDate(2025, 1, 1)
    tab.api.get_events_for_day = MagicMock(return_value=[])

    tab.update_selection()

    tab.ui.event_list.clear.assert_called_once()


def test_add_calendar_item_calls_api(qtbot):
    tab = CalendarTab(parent_tab_widget=MagicMock())
    item = make_item()

    tab.api.check_item_in_calendar = MagicMock(return_value=False)
    tab.api.add_item = MagicMock()

    tab.add_calendar_item(item)

    tab.api.add_item.assert_called_once_with(item)


def test_add_calendar_item_skips_duplicate(qtbot):
    tab = CalendarTab(parent_tab_widget=MagicMock())
    item = make_item()

    tab.api.check_item_in_calendar = MagicMock(return_value=True)
    tab.api.add_item = MagicMock()

    tab.add_calendar_item(item)

    tab.api.add_item.assert_not_called()


def test_add_and_check_calendar_item(temp_db):
    api = CalendarAPI()
    item = make_item()

    api.add_item(item)

    assert api.check_item_in_calendar(item) is True


def test_add_duplicate_calendar_item_is_ignored(temp_db, clean_calendar_table):
    api = CalendarAPI()
    item = make_item()

    api.add_item(item)
    api.add_item(item)  # should be ignored

    items = api.get_all_items()
    assert len(items) == 1


def test_get_all_items(temp_db, clean_calendar_table):
    api = CalendarAPI()
    item1 = make_item(id=2, name="A")
    item2 = make_item(id=3, name="B")

    print(item1)
    print(item2)
    api.add_item(item1)
    api.add_item(item2)

    items = api.get_all_items()
    print(items)
    names = [i.event_name for i in items]

    assert "A" in names
    assert "B" in names


def test_get_events_for_day_filters_correctly(temp_db, clean_calendar_table):
    api = CalendarAPI()

    initial_len = len(api.get_events_for_day("2025-02-01"))

    item_today = make_item(4, date="2025-02-01")
    item_other = make_item(5, date="2025-02-02")

    api.add_item(item_today)
    api.add_item(item_other)

    events = api.get_events_for_day("2025-02-01")

    assert len(events) - initial_len == 1
    assert events[-1].calendar_item_id == 4


def test_delete_calendar_item(temp_db, clean_calendar_table):
    api = CalendarAPI()
    item = make_item()

    api.add_item(item)
    assert api.check_item_in_calendar(item) is True

    api.delete_item(item)

    assert api.check_item_in_calendar(item) is False
