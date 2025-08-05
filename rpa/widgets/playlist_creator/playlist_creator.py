from typing import List
try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets
import os


class PlaylistCreator(QtWidgets.QWidget):

    def __init__(self, rpa, main_window):
        super().__init__(main_window)
        self.__rpa = rpa

        self.__create_playlists_btn = QtWidgets.QPushButton("Create Playlists")
        self.__create_playlists_btn.setStyleSheet(self._get_style())

        self.__playlists_creation_permission_btn = QtWidgets.QPushButton("Allow Playlists Creation")
        self.__playlists_creation_permission_btn.setCheckable(True)
        self.__playlists_creation_permission_btn.setStyleSheet(self._get_style(False))

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.__create_playlists_btn)
        layout.addWidget(self.__playlists_creation_permission_btn)
        self.setLayout(layout)

        self.__playlists_creation_permission_btn.toggled.connect(self.__playlists_creation_permission_btn_toggled)
        self.__create_playlists_btn.clicked.connect(self.__create_playlists)

        self.__rpa.session_api.delegate_mngr.add_permission_delegate(
            self.__rpa.session_api.create_playlists,
            self.__permission_delegate
        )
        self.__rpa.session_api.delegate_mngr.add_post_delegate(
            self.__rpa.session_api.create_playlists,
            self.__post_delegate
        )

    def __create_playlists(self):
        self.__rpa.session_api.create_playlists(["anim", "comp", "fx", "layout"])

    def __playlists_creation_permission_btn_toggled(self, checked):
        text = "Disallow Playlists Creation" if checked else "Allow Playlists Creation"
        self.__playlists_creation_permission_btn.setText(text)
        self.__playlists_creation_permission_btn.setStyleSheet(self._get_style(checked))

    def __permission_delegate(self, *args, **kwargs):
        return not self.__playlists_creation_permission_btn.isChecked()

    def __post_delegate(self, out, names, index=None, ids=None):
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Playlists Created")
        msg.setText(f"Created playlists:\n{', '.join(names)}")
        msg.exec_()


    def _get_style(self, checked=None):

        if checked is True:
            return """
                QPushButton {
                    background-color: #dc3545;  /* Red */
                    color: white;
                    font-weight: bold;
                    border: 2px solid #b21f2d;
                    border-radius: 6px;
                    font-size: 16px;
                    padding: 8px;
                }
            """
        elif checked is False:
            return """
                QPushButton {
                    background-color: #28a745;  /* Green */
                    color: black;
                    font-weight: normal;
                    border: 2px solid #999999;
                    border-radius: 6px;
                    font-size: 16px;
                    padding: 8px;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #cccccc;  /* Light gray */
                    color: black;
                    font-weight: normal;
                    border: 2px solid #999999;
                    border-radius: 6px;
                    font-size: 16px;
                    padding: 8px;
                }
            """
