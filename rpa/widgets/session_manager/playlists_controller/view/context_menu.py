import os
from PySide2 import QtCore, QtWidgets


class ActionWithObj(QtWidgets.QAction):
    """Action that holds given object in it's SIG_TRIGGERED signal"""
    SIG_TRIGGERED = QtCore.Signal(object)
    def __init__(self, text, obj, parent=None):
        super().__init__(text, parent)
        self.__obj = obj
        self.triggered.connect(
            lambda: self.SIG_TRIGGERED.emit(self.__obj))


class ContextMenu(QtWidgets.QMenu):

    SIG_CREATE = QtCore.Signal()
    SIG_DUPLICATE = QtCore.Signal()
    SIG_CUT = QtCore.Signal()
    SIG_COPY = QtCore.Signal()
    SIG_PASTE = QtCore.Signal()
    SIG_RENAME_REQUESTED = QtCore.Signal(object)
    SIG_DELETE = QtCore.Signal()
    SIG_DELETE_PERMANENTLY = QtCore.Signal()
    SIG_DELETE_PERMANENTLY_DELETED = QtCore.Signal(list)
    SIG_RESTORE = QtCore.Signal(str)

    def __init__(self, rpa, parent=None):
        super().__init__(parent)

        self.__session_api = rpa.session_api
        self.__mindex = None
        self.__index = None
        self.__injected_obj = None

    def trigger_menu(self, mindex, pos):
        self.__mindex = mindex
        self.__index = self.__mindex.row()
        self.clear()

        create = QtWidgets.QAction("Create", self)
        duplicate = QtWidgets.QAction("Duplicate", self)
        cut = QtWidgets.QAction("Cut", self)
        copy = QtWidgets.QAction("Copy", self)
        paste = QtWidgets.QAction("Paste", self)
        rename = QtWidgets.QAction("Rename", self)
        delete = QtWidgets.QAction("Delete", self)

        create.triggered.connect(self.SIG_CREATE)
        duplicate.triggered.connect(self.SIG_DUPLICATE)
        cut.triggered.connect(self.SIG_CUT)
        copy.triggered.connect(self.SIG_COPY)
        paste.triggered.connect(self.SIG_PASTE)
        rename.triggered.connect(self.__rename_playlist)
        delete.triggered.connect(self.__check_permanent_deletion)

        self.__restore_menu = QtWidgets.QMenu("Restore", self)
        self.__restore_menu.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        ids = self.__session_api.get_deleted_playlists()
        ids = [] if ids is None else ids
        names = [self.__session_api.get_playlist_name(id) for id in ids]
        for id, name in zip(ids, names):
            action = QtWidgets.QAction(name, self.__restore_menu)
            action.setData(id)
            action.triggered.connect(self.__remove_from_recover_menu)
            self.__restore_menu.addAction(action)
        self.__restore_menu.customContextMenuRequested.connect(
            self.__load_restore_context_menu)

        if self.__index == -1:
            self.addAction(create)
            if self.__injected_obj is not None:
                for action in self.__injected_obj.get_actions(self.__index):
                    self.addAction(action)
            self.addSeparator()
            if len(names) > 0:
                self.addMenu(self.__restore_menu)
        else:
            self.addAction(rename)
            self.addSeparator()
            self.addAction(duplicate)
            self.addAction(cut)
            self.addAction(copy)
            self.addAction(paste)
            self.addSeparator()
            self.addAction(delete)
            self.addSeparator()

            if self.__injected_obj is not None:
                for action in self.__injected_obj.get_actions(self.__index):
                    self.addAction(action)
                for menu in self.__injected_obj.get_menus():
                    self.addMenu(menu)

        self.exec_(pos)

    def inject_obj(self, obj):
        self.__injected_obj = obj

    def __rename_playlist(self):
        self.SIG_RENAME_REQUESTED.emit(self.__mindex)

    def __check_permanent_deletion(self):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers & QtCore.Qt.ShiftModifier:
            self.__confirm_permanent_deletion()
        else:
            self.SIG_DELETE.emit()

    def __confirm_permanent_deletion(self):
        ans = QtWidgets.QMessageBox.question(
            self, "Confirm permanent deletion",
            "Are you sure you want to permanently delete?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if ans == QtWidgets.QMessageBox.Yes:
            self.SIG_DELETE_PERMANENTLY.emit()

    def __remove_from_recover_menu(self):
        action = self.sender()
        id = action.data()
        self.__restore_menu.removeAction(action)
        self.SIG_RESTORE.emit(id)

    def __load_restore_context_menu(self, pos):
        action = self.__restore_menu.actionAt(pos)
        menu = QtWidgets.QMenu(self.__restore_menu)
        del_action = ActionWithObj("Delete", action, menu)
        del_action.SIG_TRIGGERED.connect(self.__delete_permanently_deleted)
        menu.addAction(del_action)
        menu.exec_(self.__restore_menu.mapToGlobal(pos))

    def __delete_permanently_deleted(self, action):
        p_id = action.data()
        self.__restore_menu.removeAction(action)
        self.SIG_DELETE_PERMANENTLY_DELETED.emit([p_id])
