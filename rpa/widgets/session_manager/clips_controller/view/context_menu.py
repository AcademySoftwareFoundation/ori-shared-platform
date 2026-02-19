try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtWidgets import QAction
except:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QAction


class ContextMenu(QtWidgets.QMenu):
    SIG_CREATE = QtCore.Signal()
    SIG_CUT = QtCore.Signal()
    SIG_COPY = QtCore.Signal()
    SIG_PASTE = QtCore.Signal()
    SIG_DELETE_PERMANENTLY = QtCore.Signal()
    SIG_MOVE_TOP = QtCore.Signal()
    SIG_MOVE_UP = QtCore.Signal()
    SIG_MOVE_DOWN = QtCore.Signal()
    SIG_MOVE_BOTTOM = QtCore.Signal()
    SIG_ADD_TITLE = QtCore.Signal(int)
    SIG_EDIT_TITLE = QtCore.Signal(str)
    SIG_SET_COLOR = QtCore.Signal()
    SIG_CLEAR_COLOR = QtCore.Signal()

    def __init__(self, session_api, parent=None):
        super().__init__(parent)

        self.__index = None
        self.__injected_obj = None
        self.__session_api = session_api

    def trigger_menu(self, clip_id, index, pos):
        if index is None:
            return
        self.__index = index

        self.clear()
        clipboard = QtWidgets.QApplication.clipboard()
        mime_data = clipboard.mimeData()

        create = QAction("Add Clip")
        create.triggered.connect(self.SIG_CREATE)

        add_title = QAction("Add Title")
        add_title.triggered.connect(lambda: self.SIG_ADD_TITLE.emit(self.__index))

        paste = QAction("Paste", self)
        paste.setShortcut("Ctrl+V")
        paste.triggered.connect(self.SIG_PASTE)

        if self.__index == -1:
            if mime_data.hasFormat("rpa/clips"):
                self.addAction(paste)
                self.addSeparator()
            self.addAction(create)
            self.addSeparator()
            self.addAction(add_title)
            self.addSeparator()

        else:
            cut = QAction("Cut", self)
            cut.setShortcut("Ctrl+X")
            copy = QAction("Copy", self)
            copy.setShortcut("Ctrl+C")

            delete_permanently = QAction("Delete Permanently", self)
            delete_permanently.setShortcut("Delete")

            move_top = QAction("Move To Top", self)
            move_up = QAction("Move Up", self)
            move_down = QAction("Move Down", self)
            move_bottom = QAction("Move To Bottom", self)

            set_color = QAction("Set Color", self)
            set_color.setShortcut("Shift+C")
            clear_color = QAction("Clear Color", self)
            clear_color.setShortcut("Shift+X")

            cut.triggered.connect(self.SIG_CUT)
            copy.triggered.connect(self.SIG_COPY)            
            delete_permanently.triggered.connect(self.SIG_DELETE_PERMANENTLY)
            move_top.triggered.connect(self.SIG_MOVE_TOP)
            move_up.triggered.connect(self.SIG_MOVE_UP)
            move_down.triggered.connect(self.SIG_MOVE_DOWN)
            move_bottom.triggered.connect(self.SIG_MOVE_BOTTOM)
            set_color.triggered.connect(self.SIG_SET_COLOR)
            clear_color.triggered.connect(self.SIG_CLEAR_COLOR)

            self.addAction(cut)
            self.addAction(copy)
            if mime_data.hasFormat("rpa/clips"):
                paste.setEnabled(True)
            else:
                paste.setEnabled(False)
            self.addAction(paste)
            self.addSeparator()
            self.addAction(delete_permanently)
            self.addSeparator()
            self.addAction(move_top)
            self.addAction(move_up)
            self.addAction(move_down)
            self.addAction(move_bottom)
            self.addSeparator()
            self.addAction(set_color)
            self.addAction(clear_color)
            self.addSeparator()
            self.addAction(add_title)

            is_tm = self.__session_api.get_custom_clip_attr(clip_id, "title_media")
            if is_tm:
                edit_title = QAction("Edit Title")
                edit_title.triggered.connect(lambda: self.SIG_EDIT_TITLE.emit(clip_id))
                edit_title.setProperty("hotkey_editor", True)
                self.addAction(edit_title)
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

    def get_index(self):
        return self.__index
