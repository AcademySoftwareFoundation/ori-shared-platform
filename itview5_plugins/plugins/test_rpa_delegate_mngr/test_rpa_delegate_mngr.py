from PySide2 import QtCore, QtWidgets
from rpa.widgets.test_widgets.test_delegate_mngr import TestDelegateMngr
from itview.skin.widgets.itv_dock_widget import ItvDockWidget


class TestRpaDelegateMngr:

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__test_delegate_mngr = TestDelegateMngr(self.__rpa, self.__main_window)

        dock_widget = ItvDockWidget("Test RPA Delegate Mngr", self.__main_window)
        dock_widget.setWidget(self.__test_delegate_mngr.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)
