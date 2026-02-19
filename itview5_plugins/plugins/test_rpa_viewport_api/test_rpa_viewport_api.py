from PySide2 import QtCore, QtWidgets
from rpa.widgets.test_widgets.test_viewport_api import TestViewportApi
from itview.skin.widgets.itv_dock_widget import ItvDockWidget


class TestRpaViewportApi:

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__test_viewwport_api = TestViewportApi(self.__rpa, self.__main_window)

        dock_widget = ItvDockWidget("Test RPA Viewport Api", self.__main_window)
        dock_widget.setWidget(self.__test_viewwport_api.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)
