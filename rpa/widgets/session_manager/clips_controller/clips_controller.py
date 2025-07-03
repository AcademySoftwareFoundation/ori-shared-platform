from PySide2 import QtCore, QtWidgets, QtGui
from rpa.widgets.session_manager.clips_controller.view.model import Model
from rpa.widgets.session_manager.clips_controller.view.context_menu \
    import ContextMenu
from rpa.widgets.session_manager.clips_controller.view.view import View
from rpa.widgets.session_manager.clips_controller.view.header_view \
    import HeaderView, HeaderViewPrefCntrlr
import json
from enum import Enum
import datetime
from dataclasses import dataclass


PLAY_ORDER_ID = "play_order"

class PrefKey(Enum):
    PLUGIN = "playlist_manager"
    HEADER_COLUMNS = "clip_attributes"
    HEADER_SORT_BY = "clip_attributes_sort"
    HEADER_COLUMN_WIDTHS = "column_widths"
    ASC = "asc"
    DESC = 'desc'


class ClipsController(QtCore.QObject):
    SIG_CUT = QtCore.Signal()
    SIG_COPY = QtCore.Signal()
    SIG_PASTE = QtCore.Signal()
    SIG_MOVE = QtCore.Signal(int)

    def __init__(
        self, rpa, parent):
        super().__init__(parent)

        self.__config_api = rpa.config_api
        self.__session_api = rpa.session_api
        self.__rpa = rpa

        self.__view = View(parent)
        self.__model = Model(rpa)
        self.__model.SIG_MOVE.connect(self.SIG_MOVE)
        self.__view.table.setModel(self.__model.get_proxy_model())
        self.__view.table.selectionModel().selectionChanged.connect(
            self.__selection_changed)

        self.__header_view = HeaderView(QtCore.Qt.Horizontal, self.__view.table)
        self.__view.table.setHorizontalHeader(self.__header_view)
        self.__header_view.load_column_toggle_menu()
        self.__header_view.SIG_REFRESH_ATTR.connect(self.__refresh_attr)
        self.__header_view.SIG_REFRESH_ALL_ATTRS.connect(
            self.__refresh_all_attrs)
        self.__header_view_pref_cntrlr = HeaderViewPrefCntrlr(self.__header_view)

        self.__context_menu = ContextMenu(self.__view.table)
        self.__context_menu.SIG_CUT.connect(self.SIG_CUT)
        self.__context_menu.SIG_COPY.connect(self.SIG_COPY)
        self.__context_menu.SIG_PASTE.connect(self.SIG_PASTE)
        self.__context_menu.SIG_DELETE_PERMANENTLY.connect(
            self.delete_permanently)
        self.__context_menu.SIG_MOVE_UP.connect(self.move_up)
        self.__context_menu.SIG_MOVE_DOWN.connect(self.move_down)
        self.__context_menu.SIG_MOVE_TOP.connect(self.move_top)
        self.__context_menu.SIG_MOVE_BOTTOM.connect(self.move_bottom)

        self.__view.table.SIG_CONTEXT_MENU_REQUESTED.connect(
            self.__context_menu_requested)

        self.__playlist = self.__session_api.get_fg_playlist()
        self.__session_api.SIG_PLAYLISTS_MODIFIED.connect(
            self.__playlists_modified)
        self.__session_api.SIG_PLAYLIST_MODIFIED.connect(
            self.__playlist_modified)
        self.__session_api.SIG_ACTIVE_CLIPS_CHANGED.connect(
            self.__update_selection)
        self.__session_api.SIG_CURRENT_CLIP_CHANGED.connect(
            self.__current_clip_changed)
        self.__session_api.SIG_ATTR_VALUES_CHANGED.connect(
            self.__attr_values_changed)

        self.load_preferences()

        copy_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+C"), self.__view.table)
        copy_shortcut.setContext(QtCore.Qt.WidgetShortcut)
        copy_shortcut.activated.connect(self.SIG_COPY)

        cut_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+X"), self.__view.table)
        cut_shortcut.setContext(QtCore.Qt.WidgetShortcut)
        cut_shortcut.activated.connect(self.SIG_CUT)

        paste_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+V"), self.__view.table)
        paste_shortcut.setContext(QtCore.Qt.WidgetShortcut)
        paste_shortcut.activated.connect(self.SIG_PASTE)

        delete_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Delete"), self.__view.table)
        delete_shortcut.setContext(QtCore.Qt.WidgetShortcut)
        delete_shortcut.activated.connect(self.delete_permanently)

    @property
    def view(self):
        return self.__view

    @property
    def context_menu(self):
        return self.__context_menu

    def create(self):
        paths, what = QtWidgets.QFileDialog.getOpenFileNames(
            self.__view.table,
            "Open Media",
            "",
            "",
            options=QtWidgets.QFileDialog.DontUseNativeDialog)
        if len(paths) == 0:
            return
        fg_playlist = self.__session_api.get_fg_playlist()
        selected_clips = \
            self.__session_api.get_active_clips(fg_playlist)
        if len(selected_clips) == 0:
            self.__session_api.create_clips(fg_playlist, paths)
        else:
            last_selected_clip = selected_clips[-1]
            clips = self.__session_api.get_clips(fg_playlist)
            index = clips.index(last_selected_clip) + 1
            self.__session_api.create_clips(fg_playlist, paths, index)

    def delete_permanently(self):
        selected_clips = \
            self.__session_api.get_active_clips(self.__playlist)
        self.__session_api.delete_clips_permanently(selected_clips)

    def move_top(self):
        clips = self.__session_api.get_clips(self.__playlist)
        selected_clips = \
            self.__session_api.get_active_clips(self.__playlist)
        self.__session_api.move_clips_by_offset(-len(clips), selected_clips)

    def move_bottom(self):
        clips = self.__session_api.get_clips(self.__playlist)
        selected_clips = \
            self.__session_api.get_active_clips(self.__playlist)
        self.__session_api.move_clips_by_offset(len(clips), selected_clips)

    def move_up(self):
        selected_clips = \
            self.__session_api.get_active_clips(self.__playlist)
        self.__session_api.move_clips_by_offset(-1, selected_clips)

    def move_down(self):
        selected_clips = \
            self.__session_api.get_active_clips(self.__playlist)
        self.__session_api.move_clips_by_offset(1, selected_clips)

    def __playlists_modified(self):
        fg_playlist = self.__session_api.get_fg_playlist()
        if self.__playlist == fg_playlist:
            return
        self.__playlist = fg_playlist
        self.__model.update_playlist()
        self.__update_selection(self.__playlist)

    def __playlist_modified(self, playlist):
        if self.__playlist != playlist:
            return
        self.__model.update_playlist()
        self.__update_selection(self.__playlist)

    def __update_selection(self, playlist_id):
        if self.__playlist != playlist_id:
            return
        active_clips = self.__session_api.get_active_clips(playlist_id)
        all_clips = self.__session_api.get_clips(playlist_id)
        if len(all_clips) == len(active_clips): clips = []
        else: clips = active_clips
        self.__view.table.select_clips(clips)

    def __current_clip_changed(self):
        self.__model.update_current_clip_icon()

    def __attr_values_changed(self, attr_values):
        self.__model.update_attr_values(attr_values)

    def __selection_changed(self):
        ids = []
        for index in self.__view.table.selectionModel().selectedRows():
            index = self.__view.table.model().mapToSource(index)
            id = self.__model.clips[index.row()]
            ids.append(id)
        self.__session_api.set_active_clips(self.__playlist, ids)

    def load_preferences(self):
        self.__config_api.beginGroup(PrefKey.PLUGIN.value)
        pref_attrs = json.loads(
            self.__config_api.value(PrefKey.HEADER_COLUMNS.value, "[]"))
        if PLAY_ORDER_ID not in pref_attrs:
            pref_attrs.insert(0, PLAY_ORDER_ID)
        self.__header_view_pref_cntrlr.set_attrs(pref_attrs)
        sort_attr_id_value, order = self.__config_api.value(
            PrefKey.HEADER_SORT_BY.value, [None, None])
        if order:
            order = QtCore.Qt.AscendingOrder if order == PrefKey.ASC.value \
            else QtCore.Qt.DescendingOrder
        self.__header_view_pref_cntrlr.set_sort_state(sort_attr_id_value, order)
        self.__header_view_pref_cntrlr.set_column_widths(
            json.loads(self.__config_api.value(
                PrefKey.HEADER_COLUMN_WIDTHS.value, "{}")))
        self.__config_api.endGroup()

    def save_preferences(self):
        self.__config_api.beginGroup(PrefKey.PLUGIN.value)
        self.__config_api.setValue(
            PrefKey.HEADER_COLUMNS.value,
            json.dumps(self.__header_view_pref_cntrlr.get_attrs()))
        sort_attr_id, order  = self.__header_view_pref_cntrlr.get_sort_state()
        order = PrefKey.ASC.value if order == QtCore.Qt.AscendingOrder \
            else PrefKey.DESC.value
        self.__config_api.setValue(
            PrefKey.HEADER_SORT_BY.value, [sort_attr_id, order])
        self.__config_api.setValue(
            PrefKey.HEADER_COLUMN_WIDTHS.value,
            json.dumps(self.__header_view_pref_cntrlr.get_column_widths()))

        self.__config_api.endGroup()

    def __context_menu_requested(self, index:int, pos:QtCore.QPoint):
        self.__context_menu.trigger_menu(index, pos)

    def __refresh_attr(self, attr):
        full_attr_ids = [(self.__playlist, clip, attr) for clip in self.__model.clips]
        self.__session_api.refresh_attrs(full_attr_ids)

    def __refresh_all_attrs(self):
        full_attr_ids = []
        for clip in self.__model.clips:
            for attr in self.__model.attrs:
                full_attr_ids.append((self.__playlist, clip, attr))
        self.__session_api.refresh_attrs(full_attr_ids)
