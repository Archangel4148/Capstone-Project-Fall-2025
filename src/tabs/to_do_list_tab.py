from tabs.base_tab import BaseNudgyTab
from PyQt5.QtWidgets import QTabWidget
from ui.to_do_tab_init import Ui_to_do_tab
from api.to_do_list import ToDoListAPI, To_Do_Item
from api.calendar import CalendarAPI, CalendarItem

class ToDoListTab(BaseNudgyTab):
    UI_OBJECT = Ui_to_do_tab
    TAB_LABEL = "To-Do List"

    def __init__(self, parent_tab_widget: QTabWidget):
        super().__init__(parent_tab_widget)

        self.ui.add_task_button.clicked.connect(lambda: self.addItem())
        self.ui.remove_task_button.clicked.connect(lambda: self.deleteItem())
        to_do_list_api = ToDoListAPI()
        savedItems = to_do_list_api.get_all_items()

        for dbItem in savedItems:
            item = dbItem.description + ' Due: ' + dbItem.due_date
            self.ui.listWidget.addItem(item)

    def addItem(self):
        item = self.ui.task_description_line_edit.text() + ' Due: ' + self.ui.due_date_time_edit.text()
        to_do_list_api = ToDoListAPI()
        dbItem = To_Do_Item(taskID= self.ui.listWidget.count(), description=self.ui.task_description_line_edit.text(), due_date=self.ui.due_date_time_edit.text(), include_calendar_item=self.ui.include_calendar_item_check_box.isChecked())
        to_do_list_api.add_item(dbItem)

        if self.ui.include_calendar_item_check_box.isChecked():
            calendar_api = CalendarAPI()
            dateTimeFix = self.ui.due_date_time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            calendar_item = CalendarItem(calendar_item_id=self.ui.listWidget.count(), datetime=dateTimeFix, event_name=self.ui.task_description_line_edit.text(), event_description="", duration=0, include_to_do_task=True, has_reminder=False)
            calendar_api.add_item(calendar_item)


        self.ui.listWidget.addItem(item)

    def deleteItem(self):
        clicked = self.ui.listWidget.currentRow()
        to_do_list_api = ToDoListAPI()
        dbItem = To_Do_Item(taskID=self.ui.listWidget.currentRow(), description=self.ui.listWidget.item(clicked).text().split(' Due: ')[0], due_date=self.ui.listWidget.item(clicked).text().split(' Due: ')[1])
        to_do_list_api.delete_item(dbItem)
        self.ui.listWidget.takeItem(clicked)