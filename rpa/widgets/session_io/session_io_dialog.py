import os
try:
    from PySide2 import QtWidgets
except ImportError:
    from PySide6 import QtWidgets
from rpa.widgets.session_io import constants as C


class SessionIODialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Session IO Dialog")

        self.file_dialog = QtWidgets.QFileDialog()
        self.file_dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        self.file_dialog.setNameFilter("OTIO Files (*.otio)")

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addWidget(self.file_dialog)

        self.__connect_signals()

        self.last_location = None

    def __connect_signals(self):
        self.file_dialog.finished.connect(self.__on_file_dialog_finished)

    def __on_file_dialog_finished(self, result):
        self.last_location = self.file_dialog.directory().absolutePath()

        if result == QtWidgets.QDialog.Accepted:
            self.accept()
        else:
            self.reject()

    def closeEvent(self, event):
        if self.file_dialog:
            self.last_location = self.file_dialog.directory().absolutePath()
        super().closeEvent(event)

    def get_selected_filepath(self):
        selected_files = self.file_dialog.selectedFiles()
        if selected_files:
            # first selected file
            return selected_files[0]
        else:
            return None

    def setup(self, mode, directory):
        if mode == C.APPEND:
            self.file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
            self.setWindowTitle("Append Session")
        elif mode == C.REPLACE:
            self.file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
            self.setWindowTitle("Replace Session")
        elif mode == C.SAVE:
            self.file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
            self.setWindowTitle("Save Session")

        self.file_dialog.setDirectory(directory)
