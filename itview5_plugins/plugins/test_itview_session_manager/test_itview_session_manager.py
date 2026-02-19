from PySide2 import QtCore
from rpa.widgets.test_widgets.test_session_api import TestSessionApi
from itview.skin.widgets.itv_dock_widget import ItvDockWidget


class TestItviewSessionManager:

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__test_session_manager = TestSessionApi(self.__rpa, self.__main_window)

        dock_widget = ItvDockWidget("Test RPA Session Api", self.__main_window)
        dock_widget.setWidget(self.__test_session_manager.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)
