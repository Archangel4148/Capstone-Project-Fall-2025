from tabs.base_tab import BaseNudgyTab
from PyQt5.QtWidgets import QTabWidget
from ui.to_do_tab_init import Ui_to_do_tab


class ToDoListTab(BaseNudgyTab):
    UI_OBJECT = Ui_to_do_tab
    TAB_LABEL = "To-Do List"

    def __init__(self, parent_tab_widget: QTabWidget):
        super().__init__(parent_tab_widget)

        self.ui.add_task_button.clicked.connect(lambda: self.addItem())
        self.ui.remove_task_button.clicked.connect(lambda: self.deleteItem())

    def addItem(self):
        item = self.ui.task_description_line_edit.text() + ' Due: ' + self.ui.due_date_time_edit.text()
        self.ui.listWidget.addItem(item)

    def deleteItem(self):
        clicked = self.ui.listWidget.currentRow()
        self.ui.listWidget.takeItem(clicked)