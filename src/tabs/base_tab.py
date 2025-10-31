from PyQt5.QtWidgets import QWidget, QTabWidget


class BaseNudgyTab(QWidget):
    UI_OBJECT = None  # Import this from the python UI file (For example: UI_OBJECT = Ui_TimerTab)
    TAB_LABEL = ""  # Set this to the label of the tab (For example: TAB_LABEL = "Timer")

    def __init__(self, parent_tab_widget: QTabWidget):
        super().__init__()
        self.ui = self.UI_OBJECT()  # Create an instance of the imported UI class
        self.ui.setupUi(self)

        # Add the tab to the parent tab widget
        self.tab_widget = parent_tab_widget
        self.tab_widget.addTab(self, self.TAB_LABEL)

