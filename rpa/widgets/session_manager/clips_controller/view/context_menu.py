try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtWidgets import QAction
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QAction


class ContextMenu(QtWidgets.QMenu):
    SIG_CUT = QtCore.Signal()
    SIG_COPY = QtCore.Signal()
    SIG_PASTE = QtCore.Signal()
    SIG_DELETE_PERMANENTLY = QtCore.Signal()
    SIG_MOVE_TOP = QtCore.Signal()
    SIG_MOVE_UP = QtCore.Signal()
    SIG_MOVE_DOWN = QtCore.Signal()
    SIG_MOVE_BOTTOM = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__index = None
        self.__injected_obj = None

    def trigger_menu(self, index, pos):
        if index is None:
            return
        self.__index = index

        self.clear()
        cut = QAction("Cut", self)
        cut.setShortcut("Ctrl+X")
        copy = QAction("Copy", self)
        copy.setShortcut("Ctrl+C")
        paste = QAction("Paste", self)
        paste.setShortcut("Ctrl+V")
        delete_permanently = QAction("Delete Permanently", self)
        delete_permanently.setShortcut("Delete")

        move_top = QAction("Move to top", self)
        move_up = QAction("Move up", self)
        move_down = QAction("Move down", self)
        move_bottom = QAction("Move to bottom", self)

        # SIGNALS
        cut.triggered.connect(self.SIG_CUT)
        copy.triggered.connect(self.SIG_COPY)
        paste.triggered.connect(self.__paste_clips)
        delete_permanently.triggered.connect(self.SIG_DELETE_PERMANENTLY)
        move_top.triggered.connect(self.SIG_MOVE_TOP)
        move_up.triggered.connect(self.SIG_MOVE_UP)
        move_down.triggered.connect(self.SIG_MOVE_DOWN)
        move_bottom.triggered.connect(self.SIG_MOVE_BOTTOM)

        self.addAction(cut)
        self.addAction(copy)
        self.addAction(paste)
        self.addSeparator()
        self.addAction(delete_permanently)
        self.addSeparator()
        self.addAction(move_top)
        self.addAction(move_up)
        self.addAction(move_down)
        self.addAction(move_bottom)
        self.addSeparator()

        if self.__injected_obj is not None:
            for menu in self.__injected_obj.get_menus():
                if menu is None:
                    self.addSeparator()
                    continue
                self.addMenu(menu)

            for action in self.__injected_obj.get_actions():
                if action is None:
                    self.addSeparator()
                    continue
                self.addAction(action)

        self.exec_(pos)

    def inject_obj(self, obj):
        self.__injected_obj = obj

    def __paste_clips(self):
        self.SIG_PASTE.emit()

    def get_index(self):
        return self.__index
