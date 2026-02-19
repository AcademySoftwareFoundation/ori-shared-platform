import os
from PySide2 import QtCore, QtGui, QtWidgets
from rpa.widgets.session_io.session_io import SessionIO


class ItviewSessionIO(QtCore.QObject):

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window
        self.__session_io = SessionIO(
            self.__rpa, self.__main_window, feedback=True)

        self.__assign_shortcuts()
        self.__create_file_menu()

        self.__session_io.append_session_action.setProperty("hotkey_editor", True)
        self.__session_io.replace_session_action.setProperty("hotkey_editor", True)
        self.__session_io.save_session_action.setProperty("hotkey_editor", True)
        self.__session_io.core_preferences_action.setProperty("hotkey_editor", True)
        self.__session_io.clear_session_action.setProperty("hotkey_editor", True)

    def __assign_shortcuts(self):
        self.__session_io.append_session_action.setShortcut(
            QtGui.QKeySequence("Ctrl+O"))
        self.__session_io.replace_session_action.setShortcut(
            QtGui.QKeySequence("Ctrl+Alt+O"))
        self.__session_io.save_session_action.setShortcut(
            QtGui.QKeySequence("Ctrl+S"))

    def __create_file_menu(self):
        file_menu = self.__main_window.get_file_menu()
        file_menu.addSeparator()
        file_menu.addAction(self.__session_io.append_session_action)
        file_menu.addAction(self.__session_io.replace_session_action)
        file_menu.addSeparator()
        file_menu.addAction(self.__session_io.save_session_action)
        file_menu.addSeparator()
        file_menu.addAction(self.__session_io.core_preferences_action)
        file_menu.addSeparator()
        file_menu.addAction(self.__session_io.clear_session_action)
