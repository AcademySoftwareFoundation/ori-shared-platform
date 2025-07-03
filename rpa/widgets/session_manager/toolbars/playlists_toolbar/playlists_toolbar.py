from PySide2 import QtCore, QtGui, QtWidgets
from rpa.widgets.session_manager.toolbars.icons import icons
from typing import Union, List


class PlaylistsToolbar(QtWidgets.QToolBar):
    SIG_CREATE = QtCore.Signal()
    SIG_DELETE = QtCore.Signal()
    SIG_DELETE_PERMANENTLY = QtCore.Signal()
    SIG_MOVE_TOP = QtCore.Signal()
    SIG_MOVE_BOTTOM = QtCore.Signal()
    SIG_MOVE_UP = QtCore.Signal()
    SIG_MOVE_DOWN = QtCore.Signal()
    SIG_CLEAR = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("Session Controller Playlists Toolbar")
        self.setWindowTitle("Session Controller Playlists Toolbar")
        self.setOrientation(QtCore.Qt.Vertical)

        make_icon = \
            lambda icon_name: QtGui.QIcon(QtGui.QPixmap(icon_name))

        self.addSeparator()
        label = QtWidgets.QLabel("Playlists", self)
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(label)
        self.addSeparator()

        create = QtWidgets.QAction(
            make_icon(":plus28.png"), "Create playlist", self)
        create.triggered.connect(self.SIG_CREATE)
        self.addAction(create)

        self.__delete = QtWidgets.QAction(
            make_icon(":minus28.png"), "Delete selected playlists", self)
        self.__delete.triggered.connect(self.__delete_triggered)
        self.addAction(self.__delete)

        move_top = QtWidgets.QAction(
            make_icon(":topArrow28.png"), "Move selected playlists top", self)
        move_top.triggered.connect(self.SIG_MOVE_TOP)
        self.addAction(move_top)

        move_up = QtWidgets.QAction(
            make_icon(":upArrow28.png"), "Move selected playlists up", self)
        move_up.triggered.connect(self.SIG_MOVE_UP)
        self.addAction(move_up)

        move_down = QtWidgets.QAction(make_icon(":downArrow28.png"),
            "Move selected playlists down", self)
        move_down.triggered.connect(self.SIG_MOVE_DOWN)
        self.addAction(move_down)

        move_bottom = QtWidgets.QAction(make_icon(":bottomArrow28.png"),
            "Move selected playlists bottom", self)
        move_bottom.triggered.connect(self.SIG_MOVE_BOTTOM)
        self.addAction(move_bottom)

        self.addSeparator()

        clear = QtWidgets.QAction(make_icon(":minus28.png"),
            "Clear Session", self)
        clear.triggered.connect(self.__clear)
        self.addAction(clear)

        self.addSeparator()
        self.addSeparator()

    def inject_create_btns(
        self, create_btns:List[Union[QtWidgets.QWidget, QtWidgets.QAction]]):

        for btn in create_btns:
            if isinstance(btn, QtWidgets.QWidget):
                self.insertWidget(self.__delete, btn)
            elif isinstance(btn, QtWidgets.QAction):
                self.insertAction(self.__delete, btn)

    def __delete_triggered(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers & QtCore.Qt.ShiftModifier:
            self.__confirm_permanent_del_sel_playlists()
        else:
            self.SIG_DELETE.emit()

    def __confirm_permanent_del_sel_playlists(self):
        response = QtWidgets.QMessageBox.question(
            self,
            "Confirm permanent deletion",
            "Are you sure you want to permanently delete selected playlists?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if response == QtWidgets.QMessageBox.Yes:
            self.SIG_DELETE_PERMANENTLY.emit()

    def __clear(self):
        response = QtWidgets.QMessageBox.question(
            self,
            "Confirm permanent deletion of session!",
            "Are you sure you want to permanently delete current session?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if response == QtWidgets.QMessageBox.Yes:
            self.SIG_CLEAR.emit()
