from PySide2 import QtCore, QtGui
from itview.skin.widgets.itv_dock_widget import ItvDockWidget
from rpa.widgets.rpa_interpreter.rpa_interpreter import RpaInterpreter as _RpaInterpreter


class RpaInterpreter(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__rpa_interpreter_widget = _RpaInterpreter(self.__rpa, self.__main_window)

        dock_widget = ItvDockWidget("Rpa Interpreter", self.__main_window)
        dock_widget.setWidget(self.__rpa_interpreter_widget)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)
        dock_widget.hide()

        self.__toggle_action = dock_widget.toggleViewAction()
        self.__toggle_action.setShortcut(QtGui.QKeySequence("Shift+Q"))
        self.__toggle_action.setProperty("hotkey_editor", True)

        plugins_menu = self.__main_window.get_plugins_menu()
        plugins_menu.addAction(self.__toggle_action)
