from PySide2 import QtCore, QtWidgets
from rpa.widgets.test_widgets.test_color_api import TestColorApi
from itview.skin.widgets.itv_dock_widget import ItvDockWidget
from functools import partial
import uuid
from collections import deque


class TestRpaColorApi:

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__test_color_api = TestColorApi(self.__rpa, self.__main_window)

        dock_widget = ItvDockWidget("Test RPA Color Api", self.__main_window)
        dock_widget.setWidget(self.__test_color_api.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)
