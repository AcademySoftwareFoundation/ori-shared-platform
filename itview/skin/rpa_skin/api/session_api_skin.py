from PySide2 import QtCore
from rpa.session_state.session import Session
from itview.skin.rpa_skin.attr_utils import make_callables, connect_signals
from typing import Any, List


class SessionApiSkin(QtCore.QObject):
    SIG_PLAYLISTS_MODIFIED = QtCore.Signal()
    SIG_PLAYLIST_MODIFIED = QtCore.Signal(str) # playlist_id
    SIG_FG_PLAYLIST_CHANGED = QtCore.Signal(str) # playlist_id
    SIG_BG_PLAYLIST_CHANGED = QtCore.Signal(object) # playlist_id
    SIG_CURRENT_CLIP_CHANGED = QtCore.Signal(object) # clip_id
    SIG_ATTR_VALUES_CHANGED = QtCore.Signal(list) # attr_values

    def __init__(self, rpa_tx, session):
        super().__init__()
        self.__rpa_tx = rpa_tx
        self.__session = session
        self.__timeline_api = None
        self.__core_attrs = set()

        make_callables(self.__rpa_tx, self)
        connect_signals(self.__rpa_tx, self)

        self.SIG_ATTR_VALUES_CHANGED.connect(self.__attr_values_changed)
        self.SIG_CURRENT_CLIP_CHANGED.connect(self.__current_clip_changed)

    def set_custom_session_attr(self, attr_id, value)->bool:
        return self.__session.set_custom_session_attr(attr_id, value)

    def get_custom_session_attr(self, attr_id)->Any:
        return self.__session.get_custom_session_attr(attr_id)

    def get_custom_session_attr_ids(self)->List[str]:
        return self.__session.get_custom_session_attr_ids()

    def set_custom_playlist_attr(self, playlist_id, attr_id, value)->bool:
        return self.__session.set_custom_playlist_attr(playlist_id, attr_id, value)

    def get_custom_playlist_attr(self, playlist_id, attr_id)->Any:
        return self.__session.get_custom_playlist_attr(playlist_id, attr_id)

    def get_custom_playlist_attr_ids(self, playlist_id)->List[str]:
        return self.__session.get_custom_playlist_attr_ids(playlist_id)

    def set_custom_clip_attr(self, clip_id, attr_id, value)->bool:
        return self.__session.set_custom_clip_attr(clip_id, attr_id, value)

    def get_custom_clip_attr(self, clip_id, attr_id)->Any:
        return self.__session.get_custom_clip_attr(clip_id, attr_id)

    def get_custom_clip_attr_ids(self, clip_id)->List[str]:
        return self.__session.get_custom_clip_attr_ids(clip_id)

    def get_attrs_metadata(self):
        get_attrs_metadata = self.__rpa_tx.get_attrs_metadata()
        self.__session.attrs_metadata.update(get_attrs_metadata)

        self.__core_attrs.clear()
        for attr, metadata in self.__session.attrs_metadata.get_copy().items():
            attr_type = metadata.get("attr_type")
            if attr_type and attr_type == "core": self.__core_attrs.add(attr)
        return self.__session.attrs_metadata.get_copy()

    def __attr_values_changed(self, attr_values):
        for attr_value in attr_values:
            playlist_id, clip_id, attr_id, value = attr_value
            playlist = self.__session.get_playlist(playlist_id)
            if playlist is None:
                continue
            clip = self.__session.get_clip(clip_id)
            if clip is None:
                continue
            if self.__session.attrs_metadata.is_keyable(attr_id):
                new_value = {}
                new_key_values = {}
                for key, val in value["key_values"].items():
                    new_key_values[int(key)] = val
                new_frame_values = {}
                for key, val in value["frame_values"].items():
                    new_frame_values[int(key)] = val

                new_value["value"] = value["value"]
                new_value["key_values"] = new_key_values
                new_value["frame_values"] = new_frame_values
                value = new_value
            clip.set_attr_value(attr_id, value)

    def get_playlists(self):
        return self.__session.get_playlist_ids()

    def get_playlist_name(self, id):
        playlist = self.__session.get_playlist(id)
        if playlist: return playlist.name
        return ""

    def set_fg_playlist(self, id):
        self.__session.set_fg_playlist(id)
        return self.__rpa_tx.set_fg_playlist(id)

    def get_fg_playlist(self):
        return self.__session.viewport.fg

    def set_bg_playlist(self, id):
        self.__session.set_bg_playlist(id)
        return self.__rpa_tx.set_bg_playlist(id)

    def get_bg_playlist(self):
        return self.__session.viewport.bg

    def delete_playlists_permanently(self, ids):
        self.__session.delete_playlists_permanently(ids)
        return self.__rpa_tx.delete_playlists_permanently(ids)

    def delete_playlists(self, ids=None):
        self.__session.delete_playlists(ids)
        return self.__rpa_tx.delete_playlists(ids)

    def get_deleted_playlists(self):
        return self.__session.get_deleted_playlist_ids()

    def restore_playlists(self, ids, index=None):
        self.__session.restore_playlists(ids, index)
        return self.__rpa_tx.restore_playlists(ids, index)

    def clear(self):
        self.__session.clear()
        return self.__rpa_tx.clear()

    def create_playlists(self, names, index=None, ids=None):
        for id in ids:
            if self.__session.get_playlist(id) is None: continue
            else:
                print(
                    "A Playlist with one of the given id already exists!", id)
                return []
        self.__session.create_playlists(names, index, ids)
        self.__rpa_tx.create_playlists(names, index, ids)

    def create_clips(self, playlist_id, paths, index=None, ids=None):
        for id in ids:
            if self.__session.get_clip(id) is None:
                continue
            else:
                print("A Clip with one of the given id already exists!", id)
                return []
        playlist = self.__session.get_playlist(playlist_id)
        playlist.create_clips(paths, ids, index)
        return self.__rpa_tx.create_clips(playlist_id, paths, index, ids)

    def move_playlists_to_index(self, index, ids):
        self.__session.move_playlists_to_index(index, ids)
        return self.__rpa_tx.move_playlists_to_index(index, ids)

    def move_playlists_by_offset(self, offset, ids):
        self.__session.move_playlists_by_offset(offset, ids)
        return self.__rpa_tx.move_playlists_by_offset(offset, ids)

    def set_playlist_name(self, id, name):
        playlist = self.__session.get_playlist(id)
        playlist.name = name
        return self.__rpa_tx.set_playlist_name(id, name)

    def get_clips(self, id):
        playlist = self.__session.get_playlist(id)
        if playlist is None:
            return []
        return playlist.clip_ids

    def set_active_clips(self, playlist_id, clip_ids):
        playlist = self.__session.get_playlist(playlist_id)
        playlist.set_active_clips(clip_ids)
        if self.__session.viewport.bg is None:
            self.__session.update_activated_clip_indexes()
        else:
            self.__session.match_fg_bg_clip_indexes()
        if self.__timeline_api:
            self.__timeline_api._playlist_seq_modified(playlist_id)
        self.__rpa_tx.set_active_clips(playlist_id, clip_ids)

    def get_active_clips(self, id):
        playlist = self.__session.get_playlist(id)
        if playlist is None:
            return []
        return playlist.active_clip_ids

    def get_attr_value(self, clip_id, attr_id):
        clip = self.__session.get_clip(clip_id)
        if clip is None: return
        value = clip.get_attr_value(attr_id)
        if value is None:
            value = self.get_default_attr_value(attr_id)
        return value

    def get_default_attr_value(self, id):
        value = self.__session.attrs_metadata.get_default_value(id)
        if self.__session.attrs_metadata.is_keyable(id):
            value = {'value': value, 'key_values': {}, 'frame_values': {}}
        return value

    def get_attrs(self):
        return self.__session.attrs_metadata.ids

    def get_attr_name(self, id):
        return self.__session.attrs_metadata.get_name(id)

    def get_read_write_attrs(self):
        return self.__session.attrs_metadata.read_write_ids

    def get_read_only_attrs(self):
        return self.__session.attrs_metadata.read_only_ids

    def get_keyable_attrs(self):
        return self.__session.attrs_metadata.keyable_ids

    def is_attr_read_only(self, id):
        return self.__session.attrs_metadata.is_read_only(id)

    def is_attr_keyable(self, id):
        return self.__session.attrs_metadata.is_keyable(id)

    def get_attr_data_type(self, id):
        return self.__session.attrs_metadata.get_data_type(id)

    def move_clips_to_index(self, index, ids):
        clip = self.__session.get_clip(ids[0])
        pl_id = clip.playlist_id
        to_move = []
        for id in ids:
            clip = self.__session.get_clip(id)
            if pl_id != clip.playlist_id:
                return False
            to_move.append(clip.id)

        playlist = self.__session.get_playlist(pl_id)
        playlist.move_clips_to_index(index, to_move)

        for play_order, clip_id in enumerate(playlist.clip_ids):
            clip = self.__session.get_clip(clip_id)
            clip.set_attr_value("play_order", play_order + 1)

        return self.__rpa_tx.move_clips_to_index(index, ids)

    def move_clips_by_offset(self, offset, ids):
        to_move = {}
        for id in ids:
            clip = self.__session.get_clip(id)
            to_move.setdefault(clip.playlist_id, []).append(clip.id)

        for playlist_id, clip_ids in to_move.items():
            playlist = self.__session.get_playlist(playlist_id)
            playlist.move_clips_by_offset(offset, clip_ids)
            for play_order, clip_id in enumerate(playlist.clip_ids):
                clip = self.__session.get_clip(clip_id)
                clip.set_attr_value("play_order", play_order + 1)
        return self.__rpa_tx.move_clips_by_offset(offset, ids)

    def delete_clips_permanently(self, ids):
        to_delete = {}
        for id in ids:
            clip = self.__session.get_clip(id)
            to_delete.setdefault(clip.playlist_id, []).append(clip.id)

        for playlist_id, clip_ids in to_delete.items():
            playlist = self.__session.get_playlist(playlist_id)
            playlist.delete_clips(clip_ids)
            for play_order, clip_id in enumerate(playlist.clip_ids):
                clip = self.__session.get_clip(clip_id)
                clip.set_attr_value("play_order", play_order + 1)

        return self.__rpa_tx.delete_clips_permanently(ids)

    def get_current_clip(self):
        playlist = self.__session.get_playlist(self.__session.viewport.fg)
        if len(playlist.clip_ids) == 0:
            self.__session.viewport.current_clip = None
        return self.__session.viewport.current_clip

    def set_current_clip(self, clip_id):
        self.__session.viewport.current_clip = clip_id
        return self.__rpa_tx.set_current_clip(clip_id)

    def __current_clip_changed(self, id):
        self.__session.viewport.current_clip = id

    def set_bg_mode(self, mode):
        self.__session.viewport.bg_mode = mode
        return self.__rpa_tx.set_bg_mode(mode)

    def get_bg_mode(self):
        return self.__session.viewport.bg_mode

    def set_source_frame_lock(self, enable_source_lock):
        self.__session.viewport.source_lock = enable_source_lock
        return self.__rpa_tx.set_source_frame_lock(enable_source_lock)

    def get_source_frame_lock(self):
        return self.__session.viewport.source_lock


    def set_attr_values(self, attr_values):
        core_attr_values = []
        session_attr_values = []
        for attr_value in attr_values:
            playlist_id, clip_id, attr_id, value = attr_value
            clip = self.__session.get_clip(clip_id)
            if attr_id in self.__core_attrs:
                core_attr_values.append(attr_value)
            else:
                _, clip_id, attr_id, value = attr_value
                clip.set_attr_value(attr_id, value)
                session_attr_values.append(attr_value)

        if session_attr_values:
            self.SIG_ATTR_VALUES_CHANGED.emit(session_attr_values)

        if core_attr_values:
            is_core_success = self.__rpa_tx.set_attr_values(core_attr_values)
        else: is_core_success = True

        return True and is_core_success

    def refresh_attrs(self, ids):
        return self.__rpa_tx.refresh_attrs(ids)

    def get_playlist_of_clip(self, id):
        clip = self.__session.get_clip(id)
        if clip is None:
            return None
        return self.__session.get_clip(id).playlist_id

    def set_clip_path(self, id, path):
        clip = self.__session.get_clip(id)
        clip.path = path
        return self.__rpa_tx.set_clip_path(clip, path)

    def get_attr_value_at(self, clip_id, attr_id, key):
        clip = self.__session.get_clip(clip_id)
        attr_value = clip.get_attr_value_at(attr_id, key)
        if attr_value is None:
            attr_value = self.get_default_attr_value(attr_id)
        return attr_value

    def set_attr_values_at(self, attr_values_at):
        return self.__rpa_tx.set_attr_values_at(attr_values_at)

    def clear_attr_values_at(self, clear_at):
        return self.__rpa_tx.clear_attr_values_at(clear_at)

    def get_attr_keys(self, clip_id, attr_id):
        if not self.__session.attrs_metadata.is_keyable(attr_id):
            return []

        clip = self.__session.get_clip(clip_id)
        key_values = list(clip.get_key_values(attr_id).keys())
        return key_values

    def get_cc_ids(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        return clip.color_corrections

    def get_session_str(self):
        return (
            str(self.__session),
            self.__rpa_tx.get_session_str())

    def set_current_frame_mode(self, mode:int):
        self.__session.current_frame_mode = mode
        return self.__rpa_tx.set_current_frame_mode(mode)

    def get_current_frame_mode(self):
        return self.__session.current_frame_mode

    def edit_frames(self, clip_id, edit, local_frame, num_frames):
        clip = self.__session.get_clip(clip_id)
        if not clip:
            return

        clip.edit_frames(edit, local_frame, num_frames)
        return self.__rpa_tx.edit_frames(clip_id, edit, local_frame, num_frames)

    def reset_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip:
            return

        clip.reset_frames()
        return self.__rpa_tx.reset_frames(clip_id)

    def are_frame_edits_allowed(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip:
            return False
        return clip.are_frame_edits_allowed()

    def _set_timeline_api(self, timeline_api):
        self.__timeline_api = timeline_api
