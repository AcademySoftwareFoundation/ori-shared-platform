from PySide2 import QtCore, QtWidgets
from rpa.widgets.test_widgets.test_annotation_api import TestAnnotationApi
from itview.skin.widgets.itv_dock_widget import ItvDockWidget
from functools import partial
import uuid
from collections import deque


class TestRpaAnnotationApi:

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__test_annotation_api = TestAnnotationApi(self.__rpa, self.__main_window)

        dock_widget = ItvDockWidget("Test RPA Annotation Api", self.__main_window)
        dock_widget.setWidget(self.__test_annotation_api.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)
