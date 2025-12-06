from tabs.base_tab import BaseNudgyTab
from ui.calendar_tab_init import Ui_calendar_tab

from src.api.calendar import CalendarAPI, CalendarItem


class CalendarTab(BaseNudgyTab):
    UI_OBJECT = Ui_calendar_tab
    TAB_LABEL = "Calendar"

    def __init__(self):
        super().__init__(self.parent_tab_widget)

        # Create the API endpoint
        self.api = CalendarAPI()


    def add_calendar_item(self, calendar_item: CalendarItem):
        pass