from typing import List
from rpa.utils import utils
try:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtWidgets import QAction
except:
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtGui import QAction


class SessionAssistant(QtCore.QObject):
    def __init__(self, rpa, main_window):
        super().__init__()
        self.__main_window = main_window
        self.__rpa = rpa
        self.__session_api = rpa.session_api
        self.__timeline_api = rpa.timeline_api
        self.__actions = []

        self.__init_actions()
        self.__connect_signals()

    def __init_actions(self):
        self.prev_playlist_action = QAction("Prev Playlist")
        self.next_playlist_action = QAction("Next Playlist")
        self.prev_clip_action = QAction("Prev Clip")
        self.next_clip_action = QAction("Next Clip")

        self.key_in_to_current_frame_action = \
            QAction("Key In to Current Frame")
        self.key_out_to_current_frame_action = \
            QAction("Key Out to Current Frame")

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
            lambda: utils.goto_prev_clip(self.__rpa))
        self.next_clip_action.triggered.connect(
            lambda: utils.goto_next_clip(self.__rpa))
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
            utils.get_offset_id(playlist_ids, current_index, offset)

        if playlist_id != new_playlist_id:
            self.__session_api.set_fg_playlist(new_playlist_id)


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
        start = self.__session_api.get_attr_value(clip_id, "media_start_frame")
        end = self.__session_api.get_attr_value(clip_id, "media_end_frame")

        cur_seq_frame = self.__timeline_api.get_current_frame()
        [clip_frame] = self.__timeline_api.get_clip_frames([cur_seq_frame])
        if clip_frame and clip_frame[0] != clip_id:
            return
        clip_id, cur_clip_frame, local_frame = clip_frame

        if attr_id == "key_in":
            comparison_key = start
        elif attr_id == "key_out":
            comparison_key = end
        else:
            return

        if cur_clip_frame == comparison_key:
            return

        cur_key = \
            self.__session_api.get_attr_value(clip_id, attr_id)

        if cur_key < start:
            new_key = start
        elif cur_key > end:
            new_key = end
        elif cur_clip_frame == cur_key:
            new_key = comparison_key
        else:
            new_key = cur_clip_frame

        self.__session_api.set_attr_values(
            [(playlist_id, clip_id, attr_id, new_key)])

        if attr_id == "key_in":
            goto_frame = 1
        elif attr_id == "key_out":
            seq_frame = self.__timeline_api.get_seq_frames(clip_id, [new_key])
            if seq_frame:
                (clip_frame, [goto_frame]) = seq_frame[0]
            else:
                goto_frame = 1
        else:
            return

        self.__timeline_api.goto_frame(goto_frame)
