from typing import List
from PySide2 import QtCore, QtWidgets


class SessionAssistant(QtCore.QObject):
    def __init__(self, rpa, main_window):
        super().__init__()
        self.__main_window = main_window
        self.__session_api = rpa.session_api
        self.__timeline_api = rpa.timeline_api
        self.__actions = []

        self.__init_actions()
        self.__connect_signals()

    def __init_actions(self):
        self.prev_playlist_action = QtWidgets.QAction("Prev Playlist")
        self.next_playlist_action = QtWidgets.QAction("Next Playlist")
        self.prev_clip_action = QtWidgets.QAction("Prev Clip")
        self.next_clip_action = QtWidgets.QAction("Next Clip")

        self.key_in_to_current_frame_action = \
            QtWidgets.QAction("Key In to Current Frame")
        self.key_out_to_current_frame_action = \
            QtWidgets.QAction("Key Out to Current Frame")

        self.__actions = [self.prev_playlist_action,
                          self.next_playlist_action,
                          self.prev_clip_action,
                          self.next_clip_action,
                          self.key_in_to_current_frame_action,
                          self.key_out_to_current_frame_action]

    def __connect_signals(self):
        self.prev_playlist_action.triggered.connect(
            self.__goto_prev_playlist)
        self.next_playlist_action.triggered.connect(
            self.__goto_next_playlist)
        self.prev_clip_action.triggered.connect(
            self.__goto_prev_clip)
        self.next_clip_action.triggered.connect(
            self.__goto_next_clip)
        self.key_in_to_current_frame_action.triggered.connect(
            self.__set_key_in_to_current_frame)
        self.key_out_to_current_frame_action.triggered.connect(
            self.__set_key_out_to_current_frame)

    @property
    def actions(self):
        return self.__actions

    def __goto_prev_playlist(self):
        self.__goto_playlist(-1)

    def __goto_next_playlist(self):
        self.__goto_playlist(1)

    def __goto_playlist(self, offset:int):
        playlist_id = self.__session_api.get_fg_playlist()
        playlist_ids = self.__session_api.get_playlists()
        current_index = playlist_ids.index(playlist_id)

        new_playlist_id = \
            self.__get_offset_id(playlist_ids, current_index, offset)

        if playlist_id != new_playlist_id:
            self.__session_api.set_fg_playlist(new_playlist_id)

    def __goto_prev_clip(self):
        self.__goto_clip(-1)

    def __goto_next_clip(self):
        self.__goto_clip(1)

    def __goto_clip(self, offset:int):
        clip_id = self.__session_api.get_current_clip()
        if clip_id is None:
            return

        reselect = False
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        selected_clip_ids = self.__session_api.get_active_clips(playlist_id)
        clip_ids = self.__session_api.get_clips(playlist_id)

        if not selected_clip_ids:
            selected_clip_ids = clip_ids
        elif len(selected_clip_ids) == 1:
            selected_clip_ids = clip_ids
            reselect = True

        current_index = selected_clip_ids.index(clip_id)

        new_clip_id = \
            self.__get_offset_id(selected_clip_ids, current_index, offset)

        if clip_id != new_clip_id:
            self.__session_api.set_current_clip(new_clip_id)
            if reselect:
                self.__session_api.set_active_clips(
                    playlist_id, [new_clip_id])

    def __get_offset_id(self, ids:List[str], index:int, offset:int)->str:
        if len(ids) == 1:
            new_index = 0
        elif index == len(ids) - 1:
            new_index = 0 if offset > 0 else index - 1
        else:
            new_index = index + offset

        if new_index == -1:
            new_index = len(ids) - 1

        new_id = ids[new_index]
        return new_id

    def __set_key_in_to_current_frame(self):
        clip_id = self.__session_api.get_current_clip()
        if clip_id is None:
            return

        self.__set_new_key(clip_id, "key_in")

    def __set_key_out_to_current_frame(self):
        clip_id = self.__session_api.get_current_clip()
        if clip_id is None:
            return

        self.__set_new_key(clip_id, "key_out")

    def __set_new_key(self, clip_id:str, attr_id:str):
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        cur_frame = self.__timeline_api.get_current_frame()
        start, end = self.__timeline_api.get_default_start_end_frame()

        if attr_id == "key_in":
            comparison_key = start
        elif attr_id == "key_out":
            comparison_key = end
        else:
            return

        if cur_frame == comparison_key:
            return

        cur_key = \
            self.__session_api.get_attr_value(clip_id, attr_id)

        if cur_key < start:
            new_key = start
        elif cur_key > end:
            new_key = end
        elif cur_frame == cur_key:
            new_key = comparison_key
        else:
            new_key = cur_frame

        self.__session_api.set_attr_values(
            [(playlist_id, clip_id, attr_id, new_key)])
        self.__timeline_api.set_frame(playlist_id, clip_id, cur_frame)
