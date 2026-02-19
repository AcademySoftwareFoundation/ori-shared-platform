"""
View for Color Corrector
"""

try:
    from PySide2 import QtCore, QtWidgets
except:
    from PySide6 import QtCore, QtWidgets
from rpa.widgets.sub_widgets.mini_label_button import MiniLabelButton
from rpa.widgets.color_corrector.view.tab_widget import ColorCorrectorTabWidget
from rpa.widgets.color_corrector.utils import Slider


class Footer(QtWidgets.QWidget):
    SIG_COPY_CLICKED = QtCore.Signal()
    SIG_PASTE_CLICKED = QtCore.Signal()
    SIG_MUTE_TAB_CLICKED = QtCore.Signal()
    SIG_MUTE_ALL_TABS_CLICKED = QtCore.Signal()
    SIG_PRINT_CLICKED = QtCore.Signal()

    def __init__(self):
        super().__init__()
        copy = MiniLabelButton("Copy", self)
        paste = MiniLabelButton("Paste", self)
        self.mute_tab = MiniLabelButton("Mute Tab", self)
        self.mute_all_tabs = MiniLabelButton("Mute All Tabs", self)
        print_= MiniLabelButton("Print", self)
        print_.setToolTip("Print current clip's color corrections at current frame")

        self.__layout = QtWidgets.QHBoxLayout()
        self.__layout.addWidget(copy)
        self.__layout.addWidget(paste)
        self.__layout.addWidget(self.mute_tab)
        self.__layout.addWidget(self.mute_all_tabs)
        self.__layout.addWidget(print_)
        self.setLayout(self.__layout)

        copy.SIG_CLICKED.connect(self.SIG_COPY_CLICKED)
        paste.SIG_CLICKED.connect(self.SIG_PASTE_CLICKED)
        self.mute_tab.SIG_CLICKED.connect(self.SIG_MUTE_TAB_CLICKED)
        self.mute_all_tabs.SIG_CLICKED.connect(self.SIG_MUTE_ALL_TABS_CLICKED)
        print_.SIG_CLICKED.connect(self.SIG_PRINT_CLICKED)

    def inject_buttons(self, buttons):
        for button in buttons:
            self.__layout.addWidget(button)


class View(QtWidgets.QWidget):
    SIG_CLOSE = QtCore.Signal()
    def __init__(self, slider_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Testing Color Correction")
        self.setGeometry(0, 0, 400, 770)

        self.__tab_widget = ColorCorrectorTabWidget(self, slider_data)
        self.__footer = Footer()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.__tab_widget)
        layout.addWidget(self.__footer)
        self.setLayout(layout)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.SIG_CLOSE.emit()

    @property
    def tab_widget(self):
        return self.__tab_widget

    @property
    def current_tab(self):
        return self.tab_widget.currentWidget()

    @property
    def footer(self):
        return self.__footer
