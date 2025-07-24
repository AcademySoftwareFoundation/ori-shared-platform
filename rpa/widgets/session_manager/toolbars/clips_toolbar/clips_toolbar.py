from typing import List, Union

try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtWidgets import QAction
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QAction
from rpa.widgets.session_manager.toolbars.icons import icons


class ClipsToolbar(QtWidgets.QToolBar):
    SIG_CREATE = QtCore.Signal()
    SIG_DELETE_PERMANENTLY = QtCore.Signal()
    SIG_MOVE_TOP = QtCore.Signal()
    SIG_MOVE_BOTTOM = QtCore.Signal()
    SIG_MOVE_UP = QtCore.Signal()
    SIG_MOVE_DOWN = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("Session Controller Clips Toolbar")
        self.setWindowTitle("Session Controller Clips Toolbar")
        self.setOrientation(QtCore.Qt.Vertical)

        make_icon = \
            lambda icon_name: QtGui.QIcon(QtGui.QPixmap(icon_name))

        self.addSeparator()
        label = QtWidgets.QLabel("Clips", self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(label)
        self.addSeparator()

        self.__create = QAction(
            make_icon(":plus28.png"), "Create clips", self)
        self.__create.triggered.connect(self.SIG_CREATE)
        self.addAction(self.__create)

        delete_permanently = QAction(
            make_icon(":minus28.png"), "Delete selected clips", self)
        delete_permanently.triggered.connect(self.SIG_DELETE_PERMANENTLY)
        self.addAction(delete_permanently)

        move_top = QAction(
            make_icon(":topArrow28.png"), "Move selected clips top", self)
        move_top.triggered.connect(self.SIG_MOVE_TOP)
        self.addAction(move_top)

        move_up = QAction(
            make_icon(":upArrow28.png"), "Move selected clips up", self)
        move_up.triggered.connect(self.SIG_MOVE_UP)
        self.addAction(move_up)

        move_down = QAction(
            make_icon(":downArrow28.png"), "Move selected clips down", self)
        move_down.triggered.connect(self.SIG_MOVE_DOWN)
        self.addAction(move_down)

        move_bottom = QAction(make_icon(":bottomArrow28.png"),
            "Move selected clips to bottom", self)
        move_bottom.triggered.connect(self.SIG_MOVE_BOTTOM)
        self.addAction(move_bottom)

        self.addSeparator()
        self.addSeparator()

    def inject_create_btn(self, action: QAction):
        self.insertAction(self.__create, action)
        self.__create.setVisible(False)

    def inject_button(self, actions: List[Union[QtWidgets.QWidget, QAction]]):
        for action in actions:
            self.addAction(action)
