from PyQt5.QtWidgets import QTabWidget
from tabs.base_tab import BaseNudgyTab

from api.calendar import CalendarAPI, CalendarItem
from ui.calendar_tab_init import Ui_calendar_tab

class CalendarTab(BaseNudgyTab):
    UI_OBJECT = Ui_calendar_tab
    TAB_LABEL = "Calendar"

    def __init__(self, parent_tab_widget: QTabWidget):
        super().__init__(parent_tab_widget)

        # Create the API endpoint
        self.api = CalendarAPI()

        self.ui.calendar_widget.selectionChanged.connect(self.update_selection)

    def update_selection(self):
        date = self.ui.calendar_widget.selectedDate().toString("yyyy-MM-dd")
        self.ui.date_label.setText(date)
        self.ui.event_list.clear()
        for item in self.api.get_events_for_day(date):
            event_display_string = f"{item.event_name} ({item.duration} minutes)\n{item.event_description}\n"
            self.ui.event_list.addItem(event_display_string)

    def add_calendar_item(self, calendar_item: CalendarItem):
        # Don't add duplicate items
        if self.api.check_item_in_calendar(calendar_item):
            return
        self.api.add_item(calendar_item)
