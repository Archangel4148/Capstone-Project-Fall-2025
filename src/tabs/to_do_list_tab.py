from tabs.base_tab import BaseNudgyTab
from ui.to_do_tab_init import Ui_to_do_tab


class ToDoListTab(BaseNudgyTab):
    UI_OBJECT = Ui_to_do_tab
    TAB_LABEL = "To-Do List"