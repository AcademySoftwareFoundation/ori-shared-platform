from PySide2 import QtCore, QtGui, QtWidgets
from rpa.widgets.color_corrector.controller import Controller
from itview.skin.widgets.itv_dock_widget import ItvDockWidget


class ItviewColorCorrector(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__color_api = self.__rpa.color_api
        self.__color_corrector = Controller(self.__rpa, self.__main_window)

        self.__dock_widget = ItvDockWidget("Color Corrector", self.__main_window)
        self.__dock_widget.setWidget(self.__color_corrector.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__dock_widget)
        self.__dock_widget.hide()

        plugins_menu = self.__main_window.get_plugins_menu()
        self.__toggle_action = self.__dock_widget.toggleViewAction()
        self.__toggle_action.setShortcut(QtGui.QKeySequence("F9"))
        plugins_menu.addAction(self.__toggle_action)
        self.__toggle_action.setProperty("hotkey_editor", True)
