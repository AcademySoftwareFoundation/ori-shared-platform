from PySide2 import QtCore, QtWidgets
from rpa.widgets.test_widgets.test_timeline_api import TestTimelineApi
from itview.skin.widgets.itv_dock_widget import ItvDockWidget
from functools import partial
import uuid
from collections import deque


class TestRpaTimelineApi:

    def itview_init(self, itview):
        rpa, main_window = itview.rpa, itview.main_window
        self.__test_timeline_api = TestTimelineApi(rpa, main_window)

        dock_widget = ItvDockWidget("Test RPA Timeline Api", main_window)
        dock_widget.setWidget(self.__test_timeline_api.view)
        main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)
