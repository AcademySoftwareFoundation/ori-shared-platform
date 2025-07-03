from PySide2 import QtCore
from rpa.widgets.session_manager.playlists_controller.view.view \
    import View
from rpa.widgets.session_manager.playlists_controller.view.context_menu \
    import ContextMenu
from rpa.widgets.session_manager.playlists_controller.view.model \
    import Model
from rpa.utils.playlist_name_generator import PlaylistNameGenerator


class PlaylistsController(QtCore.QObject):
    SIG_CUT = QtCore.Signal()
    SIG_COPY = QtCore.Signal()
    SIG_PASTE = QtCore.Signal()
    SIG_DUPLICATE = QtCore.Signal()
    SIG_MOVE = QtCore.Signal(int)
    SIG_ADD_CLIPS = QtCore.Signal(str, list)

    def __init__(self, rpa, parent=None):
        super().__init__(parent)
        self.__session_api = rpa.session_api
        self.__name_generator = PlaylistNameGenerator()
        self.__view = View(parent)
        self.__model = Model(rpa, parent)
        self.__model.SIG_MOVE.connect(self.SIG_MOVE)
        self.__model.SIG_ADD_CLIPS.connect(self.__add_clips_to_playlist)
        self.__view.setModel(self.__model)
        self.__view.SIG_CONTEXT_MENU_REQUESTED.connect(
            self.__context_menu_requested)
        self.__view.SIG_SET_FG.connect(self.__set_fg)
        self.__view.SIG_SET_BG.connect(self.__set_bg)
        self.__view.SIG_DELETE.connect(self.delete)
        self.__view.selectionModel().selectionChanged.connect(
            self.__selection_changed)

        self.__context_menu = ContextMenu(rpa, self.__view)
        self.__context_menu.SIG_CREATE.connect(self.create)
        self.__context_menu.SIG_DUPLICATE.connect(self.SIG_DUPLICATE)
        self.__context_menu.SIG_CUT.connect(self.SIG_CUT)
        self.__context_menu.SIG_COPY.connect(self.SIG_COPY)
        self.__context_menu.SIG_PASTE.connect(self.SIG_PASTE)
        self.__context_menu.SIG_RENAME_REQUESTED.connect(
            self.__view.rename_requested)
        self.__context_menu.SIG_DELETE.connect(self.delete)
        self.__context_menu.SIG_DELETE_PERMANENTLY.connect(
            self.delete_permanently)
        self.__context_menu.SIG_DELETE_PERMANENTLY_DELETED.connect(
            self.__delete_permanently_deleted)
        self.__context_menu.SIG_RESTORE.connect(self.__restore)

        self.__session_api.SIG_PLAYLISTS_MODIFIED.connect(
            self.__update_playlists)
        self.__session_api.delegate_mngr.add_post_delegate(
             self.__session_api.set_playlist_name, self.__playlist_name_changed)

    def __selection_changed(self, selected, deselected):
        playlists_selection = []
        selected_indexes = self.__view.get_selected_indexes()

        for index in selected_indexes:
            id = self.__model.playlist_ids[index]
            playlists_selection.append(id)

        self.__session_api.set_custom_session_attr(
            "playlists_selection", playlists_selection)

    def __update_playlists(self):
        self.__model.update_playlists()
        self.__update_selection()

    def __update_selection(self):
        playlists_selection = \
            self.__session_api.get_custom_session_attr("playlists_selection")
        if playlists_selection:
            self.__view.select_playlists(playlists_selection)

    def __playlist_name_changed(self, out, id, name):
        self.__model.update_playlist_name(id)

    @property
    def view(self):
        return self.__view

    @property
    def context_menu(self):
        return self.__context_menu

    def __set_fg(self, id):
        self.__session_api.set_fg_playlist(id)
        self.__view.clear_selection()

    def __set_bg(self, id):
        if self.__session_api.get_bg_playlist() == id:
            self.__session_api.set_bg_playlist(None)
        else:
            self.__session_api.set_bg_playlist(id)

    def create(self):
        playlist_ids = self.__session_api.get_playlists()
        last_selected_playlist = playlist_ids[-1]
        index = playlist_ids.index(last_selected_playlist) + 1
        id = self.__session_api.create_playlists(
            [self.__name_generator.generate_name()], index=index)[0]
        self.__session_api.set_fg_playlist(id)

    def delete(self):
        playlists = self.get_selected_playlists()
        self.__session_api.delete_playlists(playlists)

    def delete_permanently(self):
        playlists = self.get_selected_playlists()
        self.__session_api.delete_playlists_permanently(playlists)

    def move_top(self):
        num_of_pls = len(self.__session_api.get_playlists())
        playlists = self.get_selected_playlists()
        self.__session_api.move_playlists_by_offset(-num_of_pls, playlists)

    def move_bottom(self):
        num_of_pls = len(self.__session_api.get_playlists())
        playlists = self.get_selected_playlists()
        self.__session_api.move_playlists_by_offset(num_of_pls, playlists)

    def move_up(self):
        playlists = self.get_selected_playlists()
        self.__session_api.move_playlists_by_offset(-1, playlists)

    def move_down(self):
        playlists = self.get_selected_playlists()
        self.__session_api.move_playlists_by_offset(1, playlists)

    def __add_clips_to_playlist(self, drop_index, clip_ids):
        if drop_index == -1:
            playlist_id = self.__session_api.create_playlists(
                [self.__name_generator.generate_name()])[0]
        else:
            playlist_id = self.__model.playlist_ids[drop_index]
        self.SIG_ADD_CLIPS.emit(playlist_id, clip_ids)

    def __context_menu_requested(self, index:QtCore.QModelIndex, pos:QtCore.QPoint):
        self.__context_menu.trigger_menu(index, pos)

    def __delete_permanently_deleted(self, ids):
        self.__session_api.delete_playlists_permanently(ids)

    def __restore(self, id):
        playlists = self.__session_api.get_playlists()
        last_playlist = playlists[-1]
        index = playlists.index(last_playlist) + 1
        self.__session_api.restore_playlists([id], index)

    def clear(self):
        self.__session_api.clear()

    def get_selected_playlists(self):
        indexes = self.__view.get_selected_indexes()
        playlist_ids = self.__session_api.get_playlists()
        selected_playlists = [playlist_ids[index] for index in sorted(indexes)]
        return selected_playlists
