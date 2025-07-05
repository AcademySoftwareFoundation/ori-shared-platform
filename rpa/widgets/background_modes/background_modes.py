try:
    from PySide2 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
from rpa.widgets.background_modes.actions import Actions


class BackgroundModes(QtCore.QObject):
    def __init__(self, rpa, main_window):
        self.__rpa = rpa
        self.__session_api = self.__rpa.session_api        

        self.actions = Actions()
        self.__connect_signals()

        self.__mode_to_action = {
            1: self.actions.wipe,
            2: self.actions.side_by_side,
            3: self.actions.top_to_bottom,
            4: self.actions.pip}

        self.__session_api.delegate_mngr.add_post_delegate(
            self.__session_api.set_bg_mode, self.__bg_mode_changed)

        self.__session_api.SIG_BG_PLAYLIST_CHANGED.connect(
            self.__bg_playlist_changed)

        self.__bg_mode_changed(True, self.__session_api.get_bg_mode())
        self.__bg_playlist_changed(self.__session_api.get_bg_playlist())

    def __connect_signals(self):
        self.actions.turn_off_background.triggered.connect(
            self.__turn_off_background)
        self.actions.pip.triggered.connect(self.__toggle_pip)
        self.actions.side_by_side.triggered.connect(self.__toggle_side_by_side)
        self.actions.top_to_bottom.triggered.connect(self.__toggle_top_to_bottom)
        self.actions.wipe.triggered.connect(self.__toggle_wipe)
        self.actions.swap_background.triggered.connect(self.__swap_background)

    def __turn_off_background(self):
        self.__session_api.set_bg_playlist(None)

    def __toggle_bg_mode(self, state, mode):
        if state:
            self.__session_api.set_bg_mode(mode)
        else:
            self.__session_api.set_bg_mode(0)

    def __toggle_wipe(self, state):
        self.__toggle_bg_mode(state, 1)

    def __toggle_side_by_side(self, state):
        self.__toggle_bg_mode(state, 2)

    def __toggle_top_to_bottom(self, state):
        self.__toggle_bg_mode(state, 3)

    def __toggle_pip(self, state):
        self.__toggle_bg_mode(state, 4)

    def __swap_background(self):
        self.__session_api.set_fg_playlist(
            self.__session_api.get_bg_playlist())

    def __bg_mode_changed(self, out:bool, mode:int):
        self.__uncheck_checkboxes()
        if mode > 0:
            self.__mode_to_action[mode].setChecked(True)

    def __bg_playlist_changed(self, id):
        if id is None:
            self.__enable_actions(False)
            self.__uncheck_checkboxes()
        else:
            self.__enable_actions(True)
            self.__bg_mode_changed(True, self.__session_api.get_bg_mode())

    def __enable_actions(self, state):
        for action in [
            self.actions.turn_off_background,
            self.actions.wipe, self.actions.pip,
            self.actions.side_by_side, self.actions.top_to_bottom,
            self.actions.swap_background]:
            action.setEnabled(state)

    def __uncheck_checkboxes(self):
        for action in [
            self.actions.wipe, self.actions.pip,
            self.actions.side_by_side, self.actions.top_to_bottom]:
            action.setChecked(False)
