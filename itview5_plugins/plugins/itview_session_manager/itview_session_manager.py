import os
from PySide2 import QtCore, QtGui, QtWidgets
from rpa.widgets.session_manager.session_manager import SessionManager
from itview.skin.widgets.itv_dock_widget import ItvDockWidget

INTERACTIVE_MODE = "interactive_mode"


class ComboBoxWithTooltip(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.installEventFilter(self)
        self.tooltips = {}

    def addItem(self, text, tooltip=""):
        super().addItem(text)
        self.tooltips[text] = tooltip

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent):
        if obj == self and event.type() == QtCore.QEvent.ToolTip:
            index = self.view().indexAt(event.pos())
            if index.isValid():
                text = self.itemText(index.row())
                if text in self.tooltips:
                    QtWidgets.QToolTip.showText(
                        event.globalPos(), self.tooltips[text], self)
            return True
        return super().eventFilter(obj, event)


class ItviewSessionManager(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window
        self.__session_manager = SessionManager(self.__rpa, self.__main_window)

        self.__session_api = self.__rpa.session_api
        self.__config_api = self.__rpa.config_api

        self.__current_frame_mode_config_key = "session_manager_current_frame_mode"
        current_frame_mode = self.__config_api.value(self.__current_frame_mode_config_key)
        if current_frame_mode is None:
            current_frame_mode = self.__session_api.get_current_frame_mode()
        else:
            current_frame_mode = int(current_frame_mode)
        self.__session_api.set_current_frame_mode(current_frame_mode)
        self.__setup_settings_menu()

        dock_widget = \
            ItvDockWidget("Itview Session Manager", self.__main_window)
        dock_widget.setWidget(self.__session_manager.view)
        self.__main_window.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)
        dock_widget.hide()

        self.__toggle_action = dock_widget.toggleViewAction()
        self.__toggle_action.setShortcut(QtGui.QKeySequence("Ctrl+P"))
        self.__add_to_session_menu()

        core_view = self.__main_window.get_core_view()
        core_view.installEventFilter(self)
        core_view.setMouseTracking(True)

        self.__session_api.SIG_CURRENT_CLIP_CHANGED.connect(
            self.__update_window_title)
        self.__session_api.delegate_mngr.add_post_delegate(
            self.__session_api.set_playlist_name,
            self.__playlist_name_changed)
        self.__main_window.SIG_CLOSED.connect(
            self.__session_manager.save_preferences)

    def __add_to_session_menu(self):
        session_menu = self.__main_window.get_session_menu()
        session_menu.addAction(self.__toggle_action)
        session_menu.addSeparator()

    def __playlist_name_changed(self, out, playlist_id, name):
        clip_id = self.__session_api.get_current_clip()
        self.__update_window_title(clip_id)

    def __update_window_title(self, clip_id:str):
        if clip_id is None:
            title = None
        else:
            playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
            playlist_name = self.__session_api.get_playlist_name(playlist_id)
            media_path = self.__session_api.get_attr_value(clip_id, "media_path")
            media_filename = os.path.basename(media_path)
            resolution = self.__session_api.get_attr_value(clip_id, "resolution")
            play_order = self.__session_api.get_attr_value(clip_id, "play_order")
            total = len(self.__session_api.get_clips(playlist_id))
            title = f"{playlist_name} - {media_filename} {resolution} ({play_order} of {total})"

        self.__main_window.update_title(title)

    def __current_frame_mode_changed(self, mode):
        self.__session_api.set_current_frame_mode(mode)
        self.__config_api.setValue(
            self.__current_frame_mode_config_key, str(mode))

    def __setup_settings_menu(self):
        menubar = self.__session_manager.view.menuBar()
        menu = menubar.addMenu("Settings")
        menu = menu.addMenu("Current Frame Mode")
        same_across_pls_action = QtWidgets.QAction("Same Across Playlists", self.__session_manager.view)
        same_across_pls_action.triggered.connect(lambda: self.__current_frame_mode_changed(0))
        same_across_pls_action.setCheckable(True)
        same_across_pls_action.setToolTip(\
            "Current frame will be synced across all playlists. \n"\
            "In the case when a single clip is selected in a playlist, \n"\
            "current frame defaults to first frame of the clip."
        )
        first_frame_action = QtWidgets.QAction("First Frame", self.__session_manager.view)
        first_frame_action.triggered.connect(lambda: self.__current_frame_mode_changed(1))
        first_frame_action.setCheckable(True)
        first_frame_action.setToolTip(\
            "Current frame will default to first frame of a selected clip \n"\
            "or sequence of clips within a playlist or among playlists. \n"\
            "Only in the case when BG playlist exist, current frame will \n"\
            "be synced across FG and BG playlists."
        )
        remember_last = QtWidgets.QAction("Remember Last", self.__session_manager.view)
        remember_last.triggered.connect(lambda: self.__current_frame_mode_changed(2))
        remember_last.setCheckable(True)
        remember_last.setToolTip(\
            "Current frame will be set to last frame it was at for the \n"\
            "playlist. Only in the case when BG playlist exist, current \n"\
            "frame will be synced across FG and BG playlists."
        )
        self.__action_group = QtWidgets.QActionGroup(self.__session_manager.view)
        self.__action_group.addAction(same_across_pls_action)
        self.__action_group.addAction(first_frame_action)
        self.__action_group.addAction(remember_last)
        self.__action_group.setExclusive(True)
        menu.addAction(same_across_pls_action)
        menu.addAction(first_frame_action)
        menu.addAction(remember_last)

        current_frame_mode = self.__session_api.get_current_frame_mode()
        action = self.__action_group.actions()[current_frame_mode]
        action.setChecked(True)
