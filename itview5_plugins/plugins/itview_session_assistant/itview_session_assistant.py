from PySide2 import QtCore, QtGui
from rpa.widgets.session_assistant.session_assistant import SessionAssistant


class ItviewSessionAssistant:

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__session_assistant = SessionAssistant(self.__rpa, self.__main_window)

        self.__assign_shortcuts()
        self.__create_session_menu()

        self.__session_assistant.prev_playlist_action.setProperty("hotkey_editor", True)
        self.__session_assistant.next_playlist_action.setProperty("hotkey_editor", True)
        self.__session_assistant.prev_clip_action.setProperty("hotkey_editor", True)
        self.__session_assistant.next_clip_action.setProperty("hotkey_editor", True)
        self.__session_assistant.key_in_to_current_frame_action.setProperty("hotkey_editor", True)
        self.__session_assistant.key_out_to_current_frame_action.setProperty("hotkey_editor", True)

    def __assign_shortcuts(self):
        self.__session_assistant.prev_playlist_action.setShortcut(
            QtGui.QKeySequence("Shift+Up"))
        self.__session_assistant.next_playlist_action.setShortcut(
            QtGui.QKeySequence("Shift+Down"))
        self.__session_assistant.prev_clip_action.setShortcut(
            QtGui.QKeySequence("PgUp"))
        self.__session_assistant.next_clip_action.setShortcut(
            QtGui.QKeySequence("PgDown"))
        self.__session_assistant.key_in_to_current_frame_action.setShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_BracketLeft))
        self.__session_assistant.key_out_to_current_frame_action.setShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_BracketRight))

    def __create_session_menu(self):
        session_menu = self.__main_window.get_session_menu()
        session_menu.addAction(self.__session_assistant.prev_playlist_action)
        session_menu.addAction(self.__session_assistant.next_playlist_action)
        session_menu.addSeparator()
        session_menu.addAction(self.__session_assistant.prev_clip_action)
        session_menu.addAction(self.__session_assistant.next_clip_action)
        session_menu.addSeparator()
        session_menu.addAction(
            self.__session_assistant.key_in_to_current_frame_action)
        session_menu.addAction(
            self.__session_assistant.key_out_to_current_frame_action)
