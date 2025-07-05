import os
try:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtWidgets import QAction
except ImportError:
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtGui import QAction
from rpa.widgets.session_io import constants as C
from rpa.widgets.session_io.session_io_dialog import SessionIODialog
from rpa.widgets.session_io.otio_reader import OTIOReader
from rpa.widgets.session_io.otio_writer import OTIOWriter


class SessionIO(QtCore.QObject):

    def __init__(self, rpa, main_window, feedback=True):
        super().__init__()

        self.__rpa = rpa
        self.__main_window = main_window
        self.__feedback = feedback

        self.__otio_reader = OTIOReader(
            self.__rpa, self.__main_window, self.__feedback)
        self.__otio_writer = OTIOWriter(
            self.__rpa, self.__main_window, self.__feedback)

        self.__init_actions()
        self.__connect_signals()

        self.__last_location = None

    @property
    def otio_reader(self):
        return self.__otio_reader

    @property
    def otio_writer(self):
        return self.__otio_writer

    @property
    def actions(self):
        return [self.append_session_action,
                self.replace_session_action,
                self.save_session_action]

    def __init_actions(self):
        self.append_session_action = QAction("Append Session")
        self.append_session_action.setStatusTip(
            "Append a session file to the current session")

        self.replace_session_action = QAction("Replace Session")
        self.replace_session_action.setStatusTip(
            "Replace the current session with a session file")

        self.save_session_action = QAction("Save Session")
        self.save_session_action.setStatusTip(
            "Save the current session to a file")

    def __connect_signals(self):
        self.append_session_action.triggered.connect(self.append_session)
        self.replace_session_action.triggered.connect(self.replace_session)
        self.save_session_action.triggered.connect(self.save_session)

    def override_signal(self, action, handler):
        if action in self.actions:
            action.triggered.disconnect()
            action.triggered.connect(handler)

    def __get_default_directory(self):
        return os.path.expanduser("~")

    def __get_directory(self):
        return self.__last_location or self.__get_default_directory()

    def __get_filepath_from_dialog(self, dialog_mode):
        filepath = None
        dialog = SessionIODialog(self.__main_window)
        dialog.setup(dialog_mode, self.__get_directory())

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            filepath = dialog.get_selected_filepath()
            self.__last_location = os.path.dirname(filepath)
        else:
            if dialog.last_location:
                self.__last_location = dialog.last_location

        return filepath

    def append_session(self):
        filepath = self.__get_filepath_from_dialog(C.APPEND)

        if filepath is None:
            return

        if not filepath.endswith(C.OTIO_EXT):
            return

        self.__otio_reader.read_otio_file(filepath)

    def replace_session(self):
        filepath = self.__get_filepath_from_dialog(C.REPLACE)

        if filepath is None:
            return

        if not filepath.endswith(C.OTIO_EXT):
            return

        self.__rpa.session_api.clear()
        playlist_ids = self.__rpa.session_api.get_playlists() # default playlist
        success = self.__otio_reader.read_otio_file(filepath)
        if success:
            self.__rpa.session_api.delete_playlists_permanently(playlist_ids)

    def save_session(self):
        filepath = self.__get_filepath_from_dialog(C.SAVE)

        if filepath is None:
            return

        if not filepath.endswith(C.OTIO_EXT):
            filepath += C.OTIO_EXT

        self.__otio_writer.write_otio_file(filepath)
