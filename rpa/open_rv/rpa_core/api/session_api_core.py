from rpa.session_state.session import Session
try:
    from PySide2 import QtCore, QtWidgets
except:
    from PySide6 import QtCore, QtWidgets
from rv import commands, runtime, extra_commands
from typing import List, Any
from rpa.open_rv.rpa_core.api import prop_util
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore

from rpa.open_rv.rpa_core.api.utils import image_to_rv, itview_to_rv
from rpa.utils.rv_overlays import OverlayType, RectOverlay, TextOverlay
from rpa.session_state.session import Session
from pymu import MuSymbol


class SessionApiCore(QtCore.QObject):
    SIG_PLAYLISTS_MODIFIED = QtCore.Signal()
    SIG_PLAYLIST_MODIFIED = QtCore.Signal(str) # playlist_id
    SIG_FG_PLAYLIST_CHANGED = QtCore.Signal(str) # playlist_id
    SIG_BG_PLAYLIST_CHANGED = QtCore.Signal(object) # playlist_id
    SIG_CURRENT_CLIP_CHANGED = QtCore.Signal(object) # clip_id
    SIG_CLIPS_DELETED = QtCore.Signal(list) # [clip_ids]

    _SIG_ATTR_IDS_ADDED = QtCore.Signal(list) # attr_ids
    SIG_ATTR_VALUES_CHANGED = QtCore.Signal(list)

    PRG_CLIPS_CREATION_STARTED = QtCore.Signal(int)  # num of clips to create,
    PRG_CLIP_CREATED = QtCore.Signal(int, int) # num of clips created, num of clips to create,
    PRG_CLIPS_CREATION_COMPLETED = QtCore.Signal()

    PRG_CLIPS_DELETION_STARTED = QtCore.Signal(int) # num of clips to delete
    PRG_CLIP_DELETED = QtCore.Signal(int, int) # num of clips deleted, num of clips to delete
    PRG_CLIPS_DELETION_COMPLETED = QtCore.Signal()

    PRG_GET_ATTR_VALUES_STARTED = QtCore.Signal(int) # num_of_attrs_to_get
    PRG_GOT_ATTR_VALUE = QtCore.Signal(int, int) # num_of_attrs_got, num_of_attrs_to_get
    PRG_GET_ATTR_VALUES_COMPLETED = QtCore.Signal()

    PRG_SET_ATTR_VALUES_STARTED = QtCore.Signal(int) # total_cnt
    PRG_SET_ATTR_VALUE = QtCore.Signal(int, int) # progress_cnt, total_cnt
    PRG_SET_ATTR_VALUES_COMPLETED = QtCore.Signal()

    def __init__(self, session, annotation_api):
        super().__init__()
        self.__session: Session = session
        self.__annotation_api = annotation_api
        self.__timeline_api = None
        self.__clip_attr_api = ClipAttrApiCore.get_instance()
        self.__clip_attr_api.init(session)
        self.__core_attrs = set()
        self.SIG_PLAYLISTS_MODIFIED.connect(self.__playlists_modified)
        self.SIG_CURRENT_CLIP_CHANGED.connect(self.__clip_changed)
        self._init()

    def _init(self):
        self.__fg_playlist_id = self.__session.viewport.fg
        self.__bg_playlist_id = self.__session.viewport.bg
        self.__map_default_playlist_if_created()
        self.__set_fg_pl_seq_grp_to_view_node()
        self.__set_bg_mode(self.__session.viewport.bg_mode)
        self.SIG_PLAYLISTS_MODIFIED.emit()
        self.__update_current_clip()
        self.__empty_view = commands.newNode("RVSequenceGroup", "session_manager_empty_view")

    def get_playlists(self):
        return self.__session.get_playlist_ids()

    def get_playlist_name(self, id):
        playlist = self.__session.get_playlist(id)
        return playlist.name

    def get_clips(self, id):
        playlist = self.__session.get_playlist(id)
        if playlist is None:
            return []
        return playlist.clip_ids

    def get_active_clips(self, id):
        playlist = self.__session.get_playlist(id)
        if playlist is None:
            return []
        return playlist.active_clip_ids

    def get_bg_playlist(self):
        return self.__session.viewport.bg

    def get_fg_playlist(self):
        return self.__session.viewport.fg

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

    def delete_playlists_permanently(self, ids):
        commands.setViewNode(self.__empty_view)
        for playlist_id in ids:
            playlist = self.__session.get_playlist(playlist_id)
            clip_ids = playlist.clip_ids
            self.__delete_clips_permanently(clip_ids)
            node_name = playlist.get_custom_attr("rv_sequence_group")
            commands.deleteNode(node_name)

        self.__session.delete_playlists_permanently(ids)
        self.__map_default_playlist_if_created()
        self.__set_fg_pl_seq_grp_to_view_node()
        self.__set_bg_mode(self.__session.viewport.bg_mode)
        self.SIG_PLAYLISTS_MODIFIED.emit()

        self.__update_current_clip()
        return True

    def delete_playlists(self, ids:List[str]=None):
        self.__session.delete_playlists(ids)
        self.__map_default_playlist_if_created()
        self.__set_fg_pl_seq_grp_to_view_node()
        self.__set_bg_mode(self.__session.viewport.bg_mode)
        self.SIG_PLAYLISTS_MODIFIED.emit()
        self.__update_current_clip()
        return True

    def get_deleted_playlists(self):
        return self.__session.get_deleted_playlist_ids()

    def restore_playlists(self, ids, index=None):
        self.__session.restore_playlists(ids, index)
        self.SIG_PLAYLISTS_MODIFIED.emit()
        return True

    def clear(self):
        commands.clearSession()
        self.__session.clear()
        self._init()
        return True

    def create_playlists(self, names, index, ids):
        for id in ids:
            if self.__session.get_playlist(id) is None:
                continue
            else:
                print("A Playlist with one of the given id already exists!", id)
                return []
        self.__session.create_playlists(names, index, ids)
        for id in ids:
            playlist = self.__session.get_playlist(id)
            playlist_node = commands.newNode("RVSequenceGroup")
            commands.setStringProperty(f"{playlist_node}.ui.name", [playlist.name])
            playlist.set_custom_attr("rv_sequence_group", playlist_node)

        self.__set_fg_pl_seq_grp_to_view_node()
        self.SIG_PLAYLIST_MODIFIED.emit(self.__session.viewport.fg)
        self.__set_bg_mode(self.__session.viewport.bg_mode)
        self.SIG_PLAYLISTS_MODIFIED.emit()
        self.__update_current_clip()

    def set_fg_playlist(self, id):
        current_frame = commands.frame()
        self.__session.set_fg_playlist(id)
        # self.__set_fg_pl_seq_grp_to_view_node()
        if self.__session.viewport.bg is None:
            playlist = self.__session.get_playlist(self.__session.viewport.fg)
            self.__update_clip_nodes_in_playlist_node(playlist)
            self.SIG_PLAYLIST_MODIFIED.emit(playlist.id)
            self.__update_current_clip()
            self.__set_fg_pl_seq_grp_to_view_node()
        else:
            self.set_bg_playlist(self.__session.viewport.bg)
            if self.__session.viewport.bg_mode != 0:
                self.__set_bg_mode(self.__session.viewport.bg_mode)
            elif self.__session.viewport.mix_mode != 0:
                self.__set_mix_mode(self.__session.viewport.mix_mode)
        self.__toggle_bg_sync_retime(id, False)
        self.__update_current_clip()
        self.__set_current_frame(current_frame)
        self.__redraw_annotations()
        self.SIG_PLAYLISTS_MODIFIED.emit()
        return True

    def set_bg_playlist(self, id):
        self.__session.set_bg_playlist(id)
        # Cache source frames since we might change it because of sync modes
        clip_ids = self.get_clips(id)
        for clip_id in clip_ids:
            clip = self.__session.get_clip(clip_id)
            clip.set_custom_attr("source_frames", clip.get_source_frames())
        current_frame = commands.frame()
        if self.__session.viewport.bg is not None:
            self.__update_clip_nodes_in_playlist_node(
                self.__session.get_playlist(self.__session.viewport.bg))
        self.__set_fg_pl_seq_grp_to_view_node()
        if self.__session.viewport.bg_mode != 0:
            self.__set_bg_mode(self.__session.viewport.bg_mode)
        elif self.__session.viewport.mix_mode != 0:
            self.__set_mix_mode(self.__session.viewport.mix_mode)
        else:
            self.__set_fg_pl_seq_grp_to_view_node()
        if self.__session.viewport.bg is None:
            commands.setFrame(current_frame)
        else:
            self.__set_current_frame(current_frame)
        self.__update_bg_retime_node(id)
        self.SIG_PLAYLISTS_MODIFIED.emit()
        return True

    def __update_bg_retime_node(self, bg_playlist_id):
        if len(self.get_clips(bg_playlist_id)) == 0:
            return
        if bg_playlist_id is None:
            return
        fg_playlist = self.__session.get_playlist(self.get_fg_playlist())
        bg_playlist = self.__session.get_playlist(bg_playlist_id)

        if self.__session.viewport.source_frame_lock == 0:
            fg_clips = list(map(lambda clip_id: self.__session.get_clip(clip_id), fg_playlist.active_clip_ids))
            bg_clips = list(map(lambda clip_id: self.__session.get_clip(clip_id), bg_playlist.active_clip_ids))
            fg_playlist_len = sum(len(clip.get_source_frames()) for clip in fg_clips)
            bg_playlist_len = sum(len(clip.get_source_frames()) for clip in bg_clips)
            if fg_playlist_len - bg_playlist_len < 0:
                # trim to have fg and bg the same length
                total = fg_playlist_len
                i = 0
                while total > 0:
                    bg_clip = bg_clips[i]
                    total -= len(bg_clip.get_source_frames())
                    i += 1
                source_frames = bg_clip.get_source_frames() if bg_clip else []
                self.__set_bg_sync_retime_node(bg_playlist.active_clip_ids[i-1], source_frames[:total])
                bg_playlist.set_active_clips(bg_playlist.clip_ids[:i])
                self.__update_clip_nodes_in_playlist_node(
                    self.__session.get_playlist(self.__session.viewport.bg))
            else:
                # if fg is longer, the bg should loop
                pass
        elif self.__session.viewport.source_frame_lock == 1:
            self.__session.match_fg_bg_clip_indexes()
            fg_clip_ids = fg_playlist.active_clip_ids
            bg_clip_ids = bg_playlist.active_clip_ids
            for fg_clip_id, bg_clip_id in zip(fg_clip_ids, bg_clip_ids):
                fg_clip, bg_clip = self.__session.get_clip(fg_clip_id), self.__session.get_clip(bg_clip_id)
                fg_frames, bg_frames = fg_clip.get_source_frames(), bg_clip.get_source_frames()
                final_bg_frames = []
                fg_i, bg_i = 0, 0
                while fg_i < len(fg_frames):
                    while fg_i < len(fg_frames) and fg_frames[fg_i] < bg_frames[bg_i]:
                        final_bg_frames.append(bg_frames[bg_i])
                        fg_i += 1
                    while bg_i+1 < len(bg_frames) and fg_frames[fg_i] > bg_frames[bg_i]:
                        bg_i += 1
                    final_bg_frames.append(bg_frames[bg_i])
                    fg_i = fg_i+1
                    if bg_i+1 < len(bg_frames):
                        bg_i+=1
                self.__set_bg_sync_retime_node(bg_clip_id, final_bg_frames)

    def __set_bg_sync_retime_node(self, clip_id, source_frames):
        clip = self.__session.get_clip(clip_id)
        if not clip: return

        bg_sync_retime = clip.get_custom_attr("rv_bg_sync_retime")
        commands.setIntProperty(
            f"{bg_sync_retime}.explicit.firstOutputFrame", [source_frames[0]], True
        )
        commands.setIntProperty(
                    f"{bg_sync_retime}.explicit.inputFrames", source_frames, True)

        commands.setIntProperty(f"{bg_sync_retime}.explicit.active", [1], True)

    def __reset_bg_sync_retime_nodes(self, playlist_id):
        playlist = self.__session.get_playlist(playlist_id)
        clip_ids = playlist.active_clip_ids
        for clip_id in clip_ids:
            clip = self.__session.get_clip(clip_id)
            source_frames = clip.get_source_frames()
            bg_sync_retime = clip.get_custom_attr("rv_bg_sync_retime")
            commands.setIntProperty(
                f"{bg_sync_retime}.explicit.firstOutputFrame", [source_frames[0]], True
            )
            commands.setIntProperty(
                        f"{bg_sync_retime}.explicit.inputFrames", source_frames, True)

            commands.setIntProperty(f"{bg_sync_retime}.explicit.active", [1], True)

    def __get_retime_source_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return

        bg_sync_retime = clip.get_custom_attr("rv_bg_sync_retime")
        return commands.getIntProperty(
            f"{bg_sync_retime}.explicit.inputFrames")

    def check_fg_bg_sync(self):
        OK = '\033[92m'
        FAIL = '\033[91m'
        END = '\033[0m'
        PASSED = OK + "PASS" + END
        FAILED = FAIL + "FAIL" + END
        fg = self.__session.get_playlist(self.get_fg_playlist())
        bg = self.__session.get_playlist(self.get_bg_playlist())
        print(f'INFO: viewport frame lock: {self.__session.viewport.source_frame_lock}')
        if self.__session.viewport.source_frame_lock:
            print(f'INFO: source frame lock enabled')
            fg_active_clip_ids = fg.active_clip_ids
            bg_active_clips_ids =  bg.active_clip_ids
            fg_n, bg_n = len(fg_active_clip_ids), len(bg_active_clips_ids)
            print(f'INFO: testing for the same amount of clips')
            print(f'INFO: {bg_active_clips_ids=} {fg_active_clip_ids=} {PASSED if fg_n==bg_n else FAILED}')
            for fg_clip_id, bg_clip_id in zip(fg_active_clip_ids, bg_active_clips_ids):
                fg_clip, bg_clip = self.__session.get_clip(fg_clip_id), self.__session.get_clip(bg_clip_id)
                fg_frames, bg_frames = fg_clip.get_source_frames(), bg_clip.get_source_frames()
                fg_retime_frames, bg_retime_frames = self.__get_retime_source_frames(fg_clip_id), self.__get_retime_source_frames(bg_clip_id)
                print(f'INFO: testing for the same length per clip')
                print(f'INFO: {len(fg_frames) = } {len(bg_retime_frames)=} {PASSED if len(fg_frames) == len(bg_retime_frames) else FAILED}')
                if fg_frames[0] > bg_frames[0]:
                    print(f'INFO: first frames differed. Testing if changed')
                    print(f"INFO: {fg_frames[0]=} {bg_retime_frames[0]=} {PASSED if fg_frames[0] == bg_retime_frames[0] else FAILED}")
                if fg_frames[-1] < bg_frames[-1]:
                    print(f'INFO: last frames differed. Testing if changed')
                    print(f"INFO: {fg_frames[-1]=} {bg_retime_frames[-1]=} {PASSED if fg_frames[-1] == bg_retime_frames[-1] else FAILED}")
        else:
            print(f'INFO: testing for the BG to be at most of the length of FG')
            fg_clips = list(map(lambda clip_id: self.__session.get_clip(clip_id), fg.active_clip_ids))
            bg_clips = list(map(lambda clip_id: self.__session.get_clip(clip_id), bg.active_clip_ids))
            fg_playlist_len = sum(len(clip.get_source_frames()) for clip in fg_clips)
            bg_playlist_len = sum(len(clip.get_source_frames()) for clip in bg_clips[:-1])
            bg_playlist_len += len(self.__get_retime_source_frames(bg.active_clip_ids[-1]))
            print(f'INFO: {fg.active_clip_ids=} {bg.active_clip_ids=}')
            print(f"INFO: {fg_playlist_len=} {bg_playlist_len=} {PASSED if bg_playlist_len <= fg_playlist_len else FAILED}")

    def move_playlists_to_index(self, index, ids):
        self.__session.move_playlists_to_index(index, ids)
        self.SIG_PLAYLISTS_MODIFIED.emit()
        return True

    def move_playlists_by_offset(self, offset, ids):
        self.__session.move_playlists_by_offset(offset, ids)
        self.SIG_PLAYLISTS_MODIFIED.emit()
        return True

    def set_playlist_name(self, id, name):
        playlist = self.__session.get_playlist(id)
        playlist.name = name
        node_name = playlist.get_custom_attr("rv_sequence_group")
        commands.setStringProperty(f"{node_name}.ui.name", [playlist.name])
        return True

    def get_attr_value(self, clip_id, attr_id):
        clip = self.__session.get_clip(clip_id)
        if clip is None: return None
        value = clip.get_attr_value(attr_id)
        if value is None:
            value = self.get_default_attr_value(attr_id)
        return value

    def get_default_attr_value(self, id):
        value = self.__session.attrs_metadata.get_default_value(id)
        if self.__session.attrs_metadata.is_keyable(id):
            value = {'value': value, 'key_values': {}, 'frame_values': {}}
        return value

    def create_clips(self, playlist_id, paths, index, ids):
        # for id in ids:
        #     if self.__session.get_clip(id) is None:
        #         continue
        #     else:
        #         print("A Clip with one of the given id already exists!", id)
        #         return []
        num_of_clips_to_create = len(paths)
        if num_of_clips_to_create == 0:
            return []

        commands.setViewNode(self.__empty_view)
        self.PRG_CLIPS_CREATION_STARTED.emit(num_of_clips_to_create)

        playlist = self.__session.get_playlist(playlist_id)
        playlist.create_clips(paths, ids, index)

        clips_created = 0
        for id, path in zip(ids, paths):
            self.__create_clip_nodes(id, path)
            clips_created += 1
            self.PRG_CLIP_CREATED.emit(clips_created, num_of_clips_to_create)
        self.PRG_CLIPS_CREATION_COMPLETED.emit()

        attr_values_list = []
        attr_values = self.__get_attr_values(
            ids, self.__session.attrs_metadata.ids)
        for clip_id, attr_ids in attr_values.items():
            clip = self.__session.get_clip(clip_id)
            for attr_id in attr_ids:
                value = attr_values[clip_id][attr_id]
                clip.set_attr_value(attr_id, value)
                attr_values_list.append(
                    (playlist.id, clip.id, attr_id, value))

        self.__update_clip_nodes_in_playlist_node(playlist)

        for play_order, clip_id in enumerate(playlist.clip_ids):
            clip = self.__session.get_clip(clip_id)
            attr_id = "play_order"
            value = play_order + 1
            clip.set_attr_value(attr_id, value)
            attr_values_list.append(
                (playlist.id, clip.id, attr_id, value))
        self.SIG_ATTR_VALUES_CHANGED.emit(attr_values_list)

        self.__set_fg_pl_seq_grp_to_view_node()
        self.SIG_PLAYLIST_MODIFIED.emit(playlist_id)
        self.__update_current_clip()
        return ids

    def __set_fg_pl_seq_grp_to_view_node(self):
        fg_playlist = self.__session.get_playlist(self.__session.viewport.fg)
        sequence = fg_playlist.get_custom_attr("rv_sequence_group")
        commands.setViewNode(sequence)

    def __map_default_playlist_if_created(self):
        ids = self.__session.get_playlist_ids()
        if len(ids) == 1:
            playlist = self.__session.get_playlist(ids[0])
            playlist_node = playlist.get_custom_attr("rv_sequence_group")
            if playlist_node: return
            playlist_node = commands.newNode("RVSequenceGroup")
            commands.setStringProperty(f"{playlist_node}.ui.name", [playlist.name])
            playlist.set_custom_attr("rv_sequence_group", playlist_node)

    def __set_current_frame(self, frame):
        def set_frame(clip):
            key_in = clip.get_attr_value("key_in")
            source_node = clip.get_custom_attr("rv_source_group")
            global_frame = \
                prop_util.convert_to_global_frame(key_in, f"{source_node}_source")
            commands.setFrame(global_frame)

        playlist = self.__session.get_playlist(self.__session.viewport.fg)
        if self.__session.current_frame_mode == 0:
            active_clip_ids = playlist.active_clip_ids
            if self.__session.viewport.bg is None and len(active_clip_ids) == 1:
                set_frame(self.__session.get_clip(active_clip_ids[0]))
            else:
                commands.setFrame(frame)
        elif self.__session.current_frame_mode == 1:
            clip_ids = playlist.clip_ids
            if len(clip_ids) > 0:
                clip = self.__session.get_clip(clip_ids[0])
                set_frame(clip)
        elif self.__session.current_frame_mode == 2:
            active_clip_ids = playlist.active_clip_ids
            if self.__session.viewport.bg is None and len(active_clip_ids) == 1:
                set_frame(self.__session.get_clip(active_clip_ids[0]))

    def set_active_clips(self, playlist_id, clip_ids):
        commands.stop()
        current_frame = commands.frame()
        playlist = self.__session.get_playlist(playlist_id)
        playlist.set_active_clips(clip_ids)
        if self.__session.viewport.bg is None:
            self.__session.update_activated_clip_indexes()
        else:
            self.__session.match_fg_bg_clip_indexes()
            self.__update_clip_nodes_in_playlist_node(
                self.__session.get_playlist(self.__session.viewport.bg))
        self.__update_clip_nodes_in_playlist_node(playlist)

        if self.__timeline_api:
            self.__timeline_api._playlist_seq_modified(playlist_id)
        self.SIG_PLAYLIST_MODIFIED.emit(playlist_id)
        self.__update_current_clip()
        self.__set_current_frame(current_frame)

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

        attr_values = []
        for play_order, clip_id in enumerate(playlist.clip_ids):
            clip = self.__session.get_clip(clip_id)
            attr_id = "play_order"
            value = play_order + 1
            clip.set_attr_value(attr_id, value)
            attr_values.append((playlist.id, clip.id, attr_id, value))
        self.SIG_ATTR_VALUES_CHANGED.emit(attr_values)

        self.__update_clip_nodes_in_playlist_node(playlist)
        self.SIG_PLAYLIST_MODIFIED.emit(playlist.id)
        return True

    def move_clips_by_offset(self, offset, ids):
        to_move = {}
        for id in ids:
            clip = self.__session.get_clip(id)
            to_move.setdefault(clip.playlist_id, []).append(clip.id)

        attr_values = []
        for playlist_id, clip_ids in to_move.items():
            playlist = self.__session.get_playlist(playlist_id)
            playlist.move_clips_by_offset(offset, clip_ids)
            attr_values.clear()
            for play_order, clip_id in enumerate(playlist.clip_ids):
                clip = self.__session.get_clip(clip_id)
                attr_id = "play_order"
                value = play_order + 1
                clip.set_attr_value(attr_id, value)
                attr_values.append((playlist.id, clip.id, attr_id, value))
            self.SIG_ATTR_VALUES_CHANGED.emit(attr_values)
            self.__update_clip_nodes_in_playlist_node(playlist)
            self.SIG_PLAYLIST_MODIFIED.emit(playlist.id)
        return True

    def __delete_clips_permanently(self, clip_ids):
        if len(clip_ids) == 0:
            return
        num_of_clips_to_delete = len(clip_ids)
        num_of_clips_deleted = 0
        self.PRG_CLIPS_DELETION_STARTED.emit(num_of_clips_to_delete)
        for clip_id in clip_ids:
            clip = self.__session.get_clip(clip_id)
            rv_secondary_transform = clip.get_custom_attr("rv_secondary_transform")
            rv_retime = clip.get_custom_attr("rv_retime")
            rv_ro_paint = clip.get_custom_attr("rv_ro_paint")
            rv_ro_paint_parent = clip.get_custom_attr("rv_ro_paint_parent")
            rv_source_group = clip.get_custom_attr("rv_source_group")
            commands.deleteNode(rv_secondary_transform)
            commands.deleteNode(rv_retime)
            commands.deleteNode(rv_ro_paint)
            commands.deleteNode(rv_ro_paint_parent)
            commands.deleteNode(rv_source_group)
            num_of_clips_deleted += 1
            self.PRG_CLIP_DELETED.emit(
                num_of_clips_deleted, num_of_clips_to_delete)
        self.SIG_CLIPS_DELETED.emit(clip_ids)
        self.PRG_CLIPS_DELETION_COMPLETED.emit()

    def __redraw_annotations(self):
        playlist_id = self.__session.viewport.fg
        playlist = self.__session.get_playlist(playlist_id)
        for clip_id in playlist.clip_ids:
            clip = self.__session.get_clip(clip_id)
            self.__annotation_api._redraw_ro_annotations(clip_id)
            for frame in clip.annotations.get_rw_frames():
                self.__annotation_api._redraw_rw_annotations(clip_id, frame)

    def set_custom_session_attr(self, attr_id, value)->None:
        self.__session.set_custom_session_attr(attr_id, value)

    def get_custom_session_attr(self, attr_id)->Any:
        return self.__session.get_custom_session_attr(attr_id)

    def get_custom_session_attr_ids(self)->List[str]:
        return self.__session.get_custom_session_attr_ids()

    def set_custom_playlist_attr(self, playlist_id, attr_id, value)->None:
        self.__session.set_custom_playlist_attr(playlist_id, attr_id, value)

    def get_custom_playlist_attr(self, playlist_id, attr_id)->Any:
        return self.__session.get_custom_playlist_attr(playlist_id, attr_id)

    def get_custom_playlist_attr_ids(self, playlist_id)->List[str]:
        return self.__session.get_custom_playlist_attr_ids(playlist_id)

    def set_custom_clip_attr(self, clip_id, attr_id, value)->None:
        self.__session.set_custom_clip_attr(clip_id, attr_id, value)

    def get_custom_clip_attr(self, clip_id, attr_id)->Any:
        return self.__session.get_custom_clip_attr(clip_id, attr_id)

    def get_custom_clip_attr_ids(self, clip_id)->List[str]:
        return self.__session.get_custom_clip_attr_ids(clip_id)

    def get_attrs_metadata(self):
        self.__core_attrs.clear()
        for attr, metadata in self.__session.attrs_metadata.get_copy().items():
            attr_type = metadata.get("attr_type")
            if attr_type and attr_type == "core": self.__core_attrs.add(attr)
        return self.__session.attrs_metadata.get_copy()

    def __create_clip_nodes(self, id, path):
        clip = self.__session.get_clip(id)

        if (isinstance(path, list) or isinstance(path, tuple)) and len(path) > 1:
            if len(path) > 2:
                path = list(path[:2])
            if not path[1]: # no audio path
                path = path[0]
        if isinstance(path, str):
            path = [path]

        # Save the current cache mode and turn caching OFF during
        # graph modification. This prevents OpenRv from trying to
        # evaluate/cache media while we're still building the node
        # pipeline
        cache_mode = commands.cacheMode()
        commands.setCacheMode(commands.CacheOff)

        # Create the source group of clip
        source = commands.addSourceVerbose(path)
        source_group = commands.nodeGroup(source)
        prop_util.set_property(f"{source_group}.custom.rpa_clip_id", [id])
        prop_util.set_property(f"{source_group}.custom.has_frame_edits", [0])
        clip.set_custom_attr("rv_source_group", source_group)
        if isinstance(path, list):
            self.__check_and_set_audio(source)

        # Get the downstream connections before we modify the graph
        _, downstream = commands.nodeConnections(source_group, False)

        # Create an RVTransform2D node as parent container for programmatic paint
        # This breaks the direct parent relationship with RVSourceGroup, so annotation
        # tools won't select the programmatic paint node
        transform_parent = commands.newNode("RVTransform2D", f"{source_group}_paint_parent")
        commands.setNodeInputs(transform_parent, [source_group])
        clip.set_custom_attr("rv_ro_paint_parent", transform_parent)

        # Try to disable the transform to ensure zero performance overhead
        # Some node types may not support the node.active property
        try:
            if commands.propertyExists(f"{transform_parent}.node.active"):
                commands.setIntProperty(f"{transform_parent}.node.active", [0], True)
        except Exception:
            # If disabling fails, the transform will remain active (identity transform)
            # which is acceptable as it won't modify the image
            pass

        # Create programmatic paint node with disabled transform as parent
        ro_paint = commands.newNode("RVPaint", f"{source_group}_ro_paint")
        commands.setNodeInputs(ro_paint, [transform_parent])
        clip.set_custom_attr("rv_ro_paint", ro_paint)

        # Create the retime node
        retime = commands.newNode("RVRetime", f"{source_group}_retime")
        clip.set_custom_attr("rv_retime", retime)

        # Create retime node for BG sync
        bg_sync_retime = commands.newNode("RVRetime", f"{source_group}_bg_sync_retime")
        clip.set_custom_attr("rv_bg_sync_retime", bg_sync_retime)

        # Set up the node chain: source_group -> placeholder_transform_parent -> ro_paint_node -> retime_node -> bg_sync_retime
        commands.setNodeInputs(retime, [ro_paint])
        commands.setNodeInputs(bg_sync_retime, [retime])
        secondary_transform = commands.newNode("RVTransform2D", f"{source_group}_secondary_transform")
        commands.setNodeInputs(secondary_transform, [bg_sync_retime])
        clip.set_custom_attr("rv_secondary_transform", secondary_transform)
        prop_util.set_property(f"{source_group}.custom.secondary_transform", [secondary_transform])

        # Update all downstream nodes to use the transform node instead of the group
        for node in downstream:
            input_nodes, _ = commands.nodeConnections(node, False)
            updated = [secondary_transform if name == source_group else name for name in input_nodes]
            if updated != input_nodes:
                commands.setNodeInputs(node, updated)
        cross_dissolve = commands.newNode(
            "CrossDissolve", f"{source_group}_cross_dissolve")
        # Set the cross_dissolve node to be not active
        commands.setIntProperty(f"{cross_dissolve}.node.active", [0], True)
        commands.setFloatProperty(f"{cross_dissolve}.parameters.startFrame", [float(0)], True)
        commands.setFloatProperty(f"{cross_dissolve}.parameters.numFrames", [float(0)], True)
        clip.set_custom_attr("rv_cross_dissolve", cross_dissolve)
        self.__annotation_api._update_visibility(id)

        # Always restore the original cache mode.
        commands.setCacheMode(cache_mode)

    def __check_and_set_audio(self, source:str):
        smis = commands.sourceMediaInfoList(source)
        if len(smis) == 2:
            both_with_video = all(smi.get("hasVideo") for smi in smis)
            both_with_audio = all(smi.get("hasAudio") for smi in smis)

            has_video = [smi.get("hasVideo") for smi in smis]
            has_audio = [smi.get("hasAudio") for smi in smis]

            if both_with_audio and has_video.count(True) == 1:
                commands.setIntProperty(
                    f"{source}.group.noMovieAudio", [1])

            if both_with_video and \
                (both_with_audio or has_audio.count(True) == 1):
                commands.setIntProperty(
                    f"{source}.group.noMovieAudio", [0])

    def __get_attr_values(
        self, clip_ids:List[str], attr_ids:List[str]):
        out = {}
        total_cnt = len(clip_ids)*len(attr_ids)
        self.PRG_GET_ATTR_VALUES_STARTED.emit(total_cnt)
        cnt = 0
        for clip_id in clip_ids:
            clip = self.__session.get_clip(clip_id)
            source_group = clip.get_custom_attr("rv_source_group")
            out[clip_id] = {}
            for attr_id in attr_ids:
                if attr_id not in self.__core_attrs: continue
                attr = self.__clip_attr_api.get_attr(attr_id)
                value = None
                if attr is not None:
                    value = attr.get_value(source_group)
                    if attr.is_keyable:
                        value = {'value': value, 'key_values': {}, 'frame_values': {}}
                out[clip_id][attr_id] = value
                cnt += 1
                self.PRG_GOT_ATTR_VALUE.emit(cnt, total_cnt)
        self.PRG_GET_ATTR_VALUES_COMPLETED.emit()
        return out

    def delete_clips_permanently(self, ids):
        to_delete = {}
        for id in ids:
            clip = self.__session.get_clip(id)
            to_delete.setdefault(clip.playlist_id, []).append(clip.id)

        self.__delete_clips_permanently(ids)
        for playlist_id, clip_ids in to_delete.items():
            playlist = self.__session.get_playlist(playlist_id)
            playlist.delete_clips(clip_ids)
            self.__update_clip_nodes_in_playlist_node(playlist)
            for play_order, clip_id in enumerate(playlist.clip_ids):
                clip = self.__session.get_clip(clip_id)
                clip.set_attr_value("play_order", play_order + 1)

        for playlist_id in to_delete.keys():
            self.SIG_PLAYLIST_MODIFIED.emit(playlist_id)

        self.__update_current_clip()
        return True

    def __update_current_clip(self):
        clip_frames =self.__session.timeline.get_clip_frames([commands.frame()])
        if len(clip_frames) != 1: return
        clip_frame = clip_frames[0]
        if clip_frame is None: return
        clip_id = clip_frame[0]

        if self.__session.viewport.current_clip != clip_id:
            self.__session.viewport.current_clip = clip_id
            self.__set_custom_fps(clip_id)
            self.SIG_CURRENT_CLIP_CHANGED.emit(clip_id)

    def __toggle_bg_sync_retime(self, playlist_id, enable):
        clips = [self.__session.get_clip(clip_id) for clip_id in self.__session.get_playlist(playlist_id).clip_ids]
        for clip in clips:
            if not clip: continue
            bg_sync_retime = clip.get_custom_attr("rv_bg_sync_retime")
            commands.setIntProperty(f"{bg_sync_retime}.explicit.active", [1 if enable else 0], True)

    def _frame_changed(self):
        self.__update_current_clip()

    def get_current_clip(self):
        playlist = self.__session.get_playlist(self.__session.viewport.fg)
        if len(playlist.clip_ids) == 0:
            self.__session.viewport.current_clip = None
        return self.__session.viewport.current_clip

    def set_current_clip(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        key_in = clip.get_attr_value("key_in")
        source_node = clip.get_custom_attr("rv_source_group")
        global_frame = prop_util.convert_to_global_frame(
            key_in, f"{source_node}_source")
        commands.setFrame(global_frame)
        self.__update_current_clip()
        return True

    def get_bg_mode(self):
        return self.__session.viewport.bg_mode

    def set_bg_mode(self, mode):
        if self.__session.viewport.bg_mode == mode:
            return False
        self.__set_bg_mode(mode)
        self.__session.viewport.bg_mode = mode
        return True

    def __set_bg_mode(self, mode):
        if self.__session.viewport.bg is None:
            return
        frame = commands.frame()
        if mode != 0:
            self.set_mix_mode(0)
        if mode == 0:
            runtime.eval(
            "require rv_state_mngr;"
            "rv_state_mngr.enable_frame_change_mouse_events();",[])
            if self.__is_wipe_mode():
                self.__toggle_wipe_mode()
            self.__set_fg_pl_seq_grp_to_view_node()
        elif mode == 1:
            self.__set_bg_mode_wipe()
        elif mode == 2:
            self.__set_bg_mode_side_by_side()
        elif mode == 3:
            self.__set_bg_mode_top_bottom()
        elif mode == 4:
            self.__set_bg_mode_pip()
        commands.setFrame(frame)

        self.__set_bg_mode_audio_input(mode)

    def __set_bg_mode_audio_input(self, mode):
        default = ".all."
        first = ".first."
        current = prop_util.get_property("#RVStack.output.chosenAudioInput")
        current = current[0] if current else default

        if mode == 0:
            cai = default
        elif mode == 4: # pip
            inputs, _ = commands.nodeConnections(commands.viewNode(), False)
            bg_node, fg_node = inputs
            cai = fg_node
        else:
            cai = first

        if current != cai:
            prop_util.set_property("#RVStack.output.chosenAudioInput", [cai])
            commands.redraw()

    def __set_bg_mode_wipe(self):
        view = "defaultStack"
        fg_playlist = self.__session.get_playlist(self.__session.viewport.fg)
        fg_node = fg_playlist.get_custom_attr("rv_sequence_group")
        bg_playlist = self.__session.get_playlist(self.__session.viewport.bg)
        bg_node = bg_playlist.get_custom_attr("rv_sequence_group")
        commands.setNodeInputs(view, [fg_node, bg_node])
        commands.setViewNode(view)
        runtime.eval(
            "require rv_state_mngr;"
            "rv_state_mngr.disable_frame_change_mouse_events();",[])
        if not self.__is_wipe_mode():
            self.__toggle_wipe_mode()

    def __toggle_wipe_mode(self):
        runtime.eval(
            "require wipe_api;"
            "wipe_api.toggleWipeMode();",[])

    def __is_wipe_mode(self):
        mode_on = runtime.eval(
            "require wipe_api;"
            "wipe_api.is_wipe_mode();",[])
        return mode_on == "true"

    def __set_bg_mode_pip(self):
        runtime.eval(
            "require rv_state_mngr;"
            "rv_state_mngr.disable_frame_change_mouse_events();",[])
        view = "defaultLayout"
        fg_playlist = self.__session.get_playlist(self.__session.viewport.fg)
        fg_node = fg_playlist.get_custom_attr("rv_sequence_group")
        bg_playlist = self.__session.get_playlist(self.__session.viewport.bg)
        bg_node = bg_playlist.get_custom_attr("rv_sequence_group")
        commands.setNodeInputs(view, [bg_node, fg_node])
        prop_util.set_property("defaultLayout.layout.mode", ["static"])
        # reset any manipulations in case side by side or top to bottom were previously on
        prop_util.set_property(
            f"defaultLayout_t_{fg_node}.transform.translate", [0.0, 0.0])
        prop_util.set_property(
            f"defaultLayout_t_{fg_node}.transform.scale", [1.0, 1.0])
        prop_util.set_property(
            f"defaultLayout_t_{bg_node}.transform.translate", [0.70, -0.18])
        prop_util.set_property(
            f"defaultLayout_t_{bg_node}.transform.scale", [0.37, 0.37])
        commands.setViewNode(view)

    def __set_bg_mode_top_bottom(self):
        runtime.eval(
            "require rv_state_mngr;"
            "rv_state_mngr.disable_frame_change_mouse_events();",[])
        view = "defaultLayout"
        fg_playlist = self.__session.get_playlist(self.__session.viewport.fg)
        fg_node = fg_playlist.get_custom_attr("rv_sequence_group")
        bg_playlist = self.__session.get_playlist(self.__session.viewport.bg)
        bg_node = bg_playlist.get_custom_attr("rv_sequence_group")
        commands.setNodeInputs(view, [fg_node, bg_node])
        prop_util.set_property("defaultLayout.layout.mode", ["column"])
        commands.setViewNode(view)

    def __set_bg_mode_side_by_side(self):
        runtime.eval(
            "require rv_state_mngr;"
            "rv_state_mngr.disable_frame_change_mouse_events();",[])
        view = "defaultLayout"
        fg_playlist = self.__session.get_playlist(self.__session.viewport.fg)
        fg_node = fg_playlist.get_custom_attr("rv_sequence_group")
        bg_playlist = self.__session.get_playlist(self.__session.viewport.bg)
        bg_node = bg_playlist.get_custom_attr("rv_sequence_group")
        commands.setNodeInputs(view, [fg_node, bg_node])
        prop_util.set_property("defaultLayout.layout.mode", ["row"])
        commands.setViewNode(view)

    def set_source_frame_lock(self, enable_source_lock):
        self.__session.viewport.source_frame_lock = enable_source_lock
        self.__reset_bg_sync_retime_nodes(self.__session.viewport.bg)
        self.__update_bg_retime_node(self.__session.viewport.bg)

    def get_source_frame_lock(self):
        return self.__session.viewport.source_frame_lock

    def set_mix_mode(self, mode):
        if self.__session.viewport.mix_mode == mode:
            return
        self.__set_mix_mode(mode)
        self.__session.viewport.mix_mode = mode

    def __set_mix_mode(self, mode):
        if self.__session.viewport.bg is None:
            return
        mode_to_type_map = {
            0: "over",
            1: "add",
            2: "-difference",
            3: "difference",
            4: "replace"
        }
        if mode not in mode_to_type_map.keys():
            return
        if mode != 0:
            self.set_bg_mode(0)
        frame = commands.frame()
        view = "defaultStack"
        fg_playlist = self.__session.get_playlist(self.__session.viewport.fg)
        fg_node = fg_playlist.get_custom_attr("rv_sequence_group")
        bg_playlist = self.__session.get_playlist(self.__session.viewport.bg)
        bg_node = bg_playlist.get_custom_attr("rv_sequence_group")
        prop_util.set_property(f'{view}_stack.composite.type', [mode_to_type_map[mode]])

        commands.setNodeInputs(view, [fg_node, bg_node])
        commands.setViewNode(view)
        commands.setFrame(frame)

    def get_mix_mode(self):
        return self.__session.viewport.mix_mode

    def __is_clip_cross_dissolve_active(self, clip):
        """Check if a clip has an active cross-dissolve transition."""
        cross_dissolve = clip.get_custom_attr("rv_cross_dissolve")
        if cross_dissolve and commands.propertyExists(f"{cross_dissolve}.node.active"):
            active_values = commands.getIntProperty(f"{cross_dissolve}.node.active")
            return bool(active_values and active_values[0])
        return False

    def __get_clip_output_node(self, clip, index, total_clips):
        """
        Determine which node to use as output for this clip.

        Returns the clip's cross-dissolve node if:
        - The clip has an active cross-dissolve, AND
        - It's not the last clip in the sequence

        Otherwise returns the clip's secondary transform node.

        Args:
            clip: The clip object to get output node for
            index: The clip's position in the playlist (0-based)
            total_clips: Total number of clips in the playlist

        Returns:
            str: Node name to use as output
        """
        if self.__is_clip_cross_dissolve_active(clip) and index < total_clips - 1:
            return clip.get_custom_attr("rv_cross_dissolve")
        return clip.get_custom_attr("rv_secondary_transform")

    def __update_clip_nodes_in_playlist_node(self, playlist):
        """
        Update playlist node inputs with clips connected via cross-dissolves.

        Builds the node graph by processing clips from first to last, connecting
        adjacent clips either directly or through cross-dissolve transitions.

        Node connection logic:
        - Each clip normally connects via its secondary_transform node
        - If a clip has an active cross-dissolve, it blends into the next clip
        - The cross-dissolve node takes two inputs: [current_clip, next_clip]
        - Cross-dissolves are only applied between adjacent clips (not on last clip)

        Args:
            playlist: The playlist object to update
        """
        playlist_node = playlist.get_custom_attr("rv_sequence_group")
        num_clips = len(playlist.active_clip_ids)

        # Handle empty playlist
        if num_clips == 0:
            commands.setNodeInputs(playlist_node, [])
            return

        # Handle single clip - connect directly
        if num_clips == 1:
            first_clip = self.__session.get_clip(playlist.active_clip_ids[0])
            first_clip_node = first_clip.get_custom_attr("rv_secondary_transform")
            commands.setNodeInputs(playlist_node, [first_clip_node])
            return

        # Build inputs list by processing clips forward
        inputs = []

        for i in range(num_clips):
            clip_id = playlist.active_clip_ids[i]
            clip = self.__session.get_clip(clip_id)

            # Get the appropriate output node for this clip
            clip_output_node = self.__get_clip_output_node(clip, i, num_clips)

            # Check if previous clip has a cross-dissolve into this one
            if i > 0:
                prev_clip_id = playlist.active_clip_ids[i - 1]
                prev_clip = self.__session.get_clip(prev_clip_id)

                if self.__is_clip_cross_dissolve_active(prev_clip):
                    # Previous clip dissolves into current clip
                    dissolve_node = prev_clip.get_custom_attr("rv_cross_dissolve")
                    prev_clip_node = prev_clip.get_custom_attr("rv_secondary_transform")

                    # Configure the cross-dissolve: [previous_clip, current_clip]
                    commands.setNodeInputs(dissolve_node, [prev_clip_node, clip_output_node])

                    # Replace the previous clip's node with its dissolve node
                    # Only replace last element with dissolve_node if it's not already a cross-dissolve node
                    if inputs and not inputs[-1].endswith("_cross_dissolve"):
                        inputs[-1] = dissolve_node
                else:
                    # No dissolve from previous clip - add current clip normally
                    inputs.append(clip_output_node)
            else:
                # First clip - always add
                inputs.append(clip_output_node)

        # Connect all clips to the playlist sequence node
        commands.setNodeInputs(playlist_node, inputs)

    def set_attr_values(self, attr_values):
        num_of_attrs_to_set = len(attr_values)
        self.PRG_SET_ATTR_VALUES_STARTED.emit(num_of_attrs_to_set)
        num_of_attrs_set = 0
        attr_values_set = []
        for attr_value in attr_values:
            playlist_id, clip_id, attr_id, value = attr_value
            playlist = self.__session.get_playlist(playlist_id)
            clip = self.__session.get_clip(clip_id)

            clip_source_node = clip.get_custom_attr("rv_source_group")
            attr = self.__clip_attr_api.get_attr(attr_id)
            is_value_set = False
            if attr is None:
                continue
            elif self.__session.attrs_metadata.is_keyable(attr_id):
                is_value_set = attr._set_value(clip_source_node, value)
            else:
                is_value_set = attr.set_value(clip_source_node, value)

            if not is_value_set: continue

            clip.set_attr_value(attr_id, value)
            if attr_id in ("key_in", "key_out"):
                self.__update_retime_node(clip_id)
                self.__update_clip_nodes_in_playlist_node(playlist)
            if attr_id in ("dissolve_start", "dissolve_length"):
                self.__update_clip_nodes_in_playlist_node(playlist)

            attr_values_set.append((playlist_id, clip_id, attr_id, value))

            if hasattr(attr, "dependent_attr_ids"):
                for dependent_attr_id in attr.dependent_attr_ids:
                    attr = self.__clip_attr_api.get_attr(dependent_attr_id)
                    value  = attr.get_value(clip_source_node)
                    if value is None:
                        value = clip.get_attr_value(dependent_attr_id)
                    else:
                        clip.set_attr_value(dependent_attr_id, value)
                    attr_values_set.append(
                        (playlist_id, clip_id, dependent_attr_id, value))

            num_of_attrs_set += 1
            self.PRG_SET_ATTR_VALUE.emit(
                num_of_attrs_set, num_of_attrs_to_set)
        self.PRG_SET_ATTR_VALUES_COMPLETED.emit()

        # timeline update for when frame control attrs change
        if any(attr_value[0] == self.__session.viewport.fg and \
            attr_value[2] in ("key_in", "key_out") for attr_value in attr_values):
            playlist = self.__session.get_playlist(self.__session.viewport.fg)

        self.SIG_ATTR_VALUES_CHANGED.emit(attr_values_set)
        return True

    def __playlists_modified(self):
        if self.__fg_playlist_id != self.__session.viewport.fg:
            self.__fg_playlist_id = self.__session.viewport.fg
            self.SIG_FG_PLAYLIST_CHANGED.emit(self.__fg_playlist_id)

        if self.__bg_playlist_id != self.__session.viewport.bg:
            self.__bg_playlist_id = self.__session.viewport.bg
            self.SIG_BG_PLAYLIST_CHANGED.emit(self.__bg_playlist_id)

    def refresh_attrs(self, ids):
        """
        Refresh all attrs from the core expect the keyable attrs as their
        values are in the tree.
        """
        num_of_attrs_to_refresh = len(ids)
        self.PRG_GET_ATTR_VALUES_STARTED.emit(num_of_attrs_to_refresh)
        num_of_attrs_refreshed = 0
        attr_values = []
        for id in ids:
            playlist_id, clip_id, attr_id = id
            if attr_id == "play_order": continue
            attr = self.__clip_attr_api.get_attr(attr_id)
            if attr.is_keyable: continue
            playlist = self.__session.get_playlist(playlist_id)
            clip = self.__session.get_clip(clip_id)
            clip_source_node = clip.get_custom_attr("rv_source_group")
            value = attr.get_value(clip_source_node)
            clip.set_attr_value(attr_id, value)
            num_of_attrs_refreshed += 1
            self.PRG_GOT_ATTR_VALUE.emit(
                num_of_attrs_refreshed, num_of_attrs_to_refresh)
            attr_values.append((playlist_id, clip_id, attr_id, value))
        self.PRG_GET_ATTR_VALUES_COMPLETED.emit()
        self.SIG_ATTR_VALUES_CHANGED.emit(attr_values)
        return True

    def __set_custom_fps(self, clip_id:str):
        media_fps_attr_id = "media_fps"
        audio_fps_attr_id = "audio_fps"
        media_fps_attr = self.__clip_attr_api.get_attr(media_fps_attr_id)
        audio_fps_attr = self.__clip_attr_api.get_attr(audio_fps_attr_id)

        clip = self.__session.get_clip(clip_id)
        source_node = clip.get_custom_attr("rv_source_group")
        media_fps = media_fps_attr.get_value(source_node)
        audio_fps = audio_fps_attr.get_value(source_node)

        current_fps = commands.fps()

        if media_fps != current_fps:
            media_fps_attr.set_value(source_node, media_fps)
            audio_fps_attr.set_value(source_node, media_fps)

    def get_playlist_of_clip(self, id):
        clip = self.__session.get_clip(id)
        if clip is None:
            return None
        return self.__session.get_clip(id).playlist_id

    def set_clip_path(self, id, path):
        clip = self.__session.get_clip(id)
        attr_id = "media_path"
        attr = self.__clip_attr_api.get_attr(attr_id)
        source_node = clip.get_custom_attr("rv_source_group")
        attr._set_value(source_node, path)
        clip.path = attr.get_value(source_node)
        self.SIG_ATTR_VALUES_CHANGED.emit(
            [(clip.playlist_id, clip.id, attr_id, clip.path)])
        self.refresh_attrs([
            (clip.playlist_id, clip.id, attr_id) \
            for attr_id in attr.dependent_attr_ids])
        return True

    def get_attr_value_at(self, clip_id, attr_id, key):
        clip = self.__session.get_clip(clip_id)
        attr_value = clip.get_attr_value_at(attr_id, key)
        if attr_value is None:
            attr_value = self.get_default_attr_value(attr_id)["value"]
        return attr_value

    def set_attr_values_at(self, attr_values_at):
        clip_attr_values = []

        for attr_value_at in attr_values_at:
            playlist_id, clip_id, attr_id, key, value_at = attr_value_at
            playlist = self.__session.get_playlist(playlist_id)
            clip = self.__session.get_clip(clip_id)

            source_node = clip.get_custom_attr("rv_source_group")
            attr = self.__clip_attr_api.get_attr(attr_id)
            if self.__session.attrs_metadata.is_keyable(attr_id):
                clip.set_attr_value_at(attr_id, key, value_at)

                attr._set_value(source_node, value_at)
                attr_value = clip.get_attr_value(attr_id)
                clip_attr_values.append((playlist_id, clip_id, attr_id, attr_value))

        self.SIG_ATTR_VALUES_CHANGED.emit(clip_attr_values)
        return True

    def clear_attr_values_at(self, clear_at):
        clip_attr_values = []

        for attr_value_at in clear_at:
            playlist_id, clip_id, attr_id, key = attr_value_at
            playlist = self.__session.get_playlist(playlist_id)
            clip = self.__session.get_clip(clip_id)

            source_node = clip.get_custom_attr("rv_source_group")
            attr = self.__clip_attr_api.get_attr(attr_id)
            if self.__session.attrs_metadata.is_keyable(attr_id):
                clip.clear_attr_value_at(attr_id, key)
                key_values = clip.get_key_values(attr_id)
                default_value = self.__session.attrs_metadata.get_default_value(attr_id)
                if key_values:
                    clip.update_interpolation(attr_id)
                else:
                    clip.update_keyable_attrs(attr_id, default_value)

                _attr_value = clip.get_attr_value_at(attr_id, key)
                attr._set_value(source_node, _attr_value)

                attr_value = clip.get_attr_value(attr_id)
                clip_attr_values.append((playlist_id, clip_id, attr_id, attr_value))

            self.SIG_ATTR_VALUES_CHANGED.emit(clip_attr_values)
        return True

    def get_attr_keys(self, clip_id, attr_id):
        if not self.__session.attrs_metadata.is_keyable(attr_id):
            return []

        clip = self.__session.get_clip(clip_id)
        keys = list(clip.get_key_values(attr_id).keys())
        return keys

    def get_cc_ids(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        return clip.color_corrections

    def get_session_str(self):
        return str(self.__session)

    def set_current_frame_mode(self, mode:int):
        self.__session.current_frame_mode = mode
        return True

    def get_current_frame_mode(self):
        return self.__session.current_frame_mode

    def set_custom_attr(self, attr_id:str, value:Any):
        self.__session.set_custom_attr(attr_id, value)
        self.SIG_CUSTOM_ATTR_VALUE_CHANGED.emit(attr_id, value)

    def get_custom_attr(self, attr_id:str)->Any:
        return self.__session.get_custom_attr(attr_id)

    def get_custom_attr_ids(self)->List[str]:
        return self.__session.get_custom_attr_ids()

    def __clip_changed(self, clip_id):
        self.__annotation_api._redraw_ro_annotations(clip_id)

    def __update_retime_node(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        source_frames = clip.get_source_frames()
        retime = clip.get_custom_attr("rv_retime")
        source_group = clip.get_custom_attr("rv_source_group")
        commands.setIntProperty(
            f"{retime}.explicit.firstOutputFrame", [source_frames[0]], True
        )
        commands.setIntProperty(
            f"{retime}.explicit.inputFrames", source_frames, True)

        commands.setIntProperty(f"{retime}.explicit.active", [1], True)
        if clip.has_frame_edits:
            commands.setIntProperty(f"{source_group}.custom.has_frame_edits", [1], True)
        else:
            commands.setIntProperty(f"{source_group}.custom.has_frame_edits", [0], True)

    def __emit_timewarp_modified_signal(self, playlist_id, clip_id):
        clip = self.__session.get_clip(clip_id)
        attr_ids_modified = ["timewarp_in", "timewarp_out", "timewarp_length"]
        attr_values_modified = []
        for attr_id in attr_ids_modified:
            value = clip.get_attr_value(attr_id)
            attr_values_modified.append((playlist_id, clip_id, attr_id, value))
        self.SIG_ATTR_VALUES_CHANGED.emit(attr_values_modified)

    def edit_frames(self, clip_id, edit, local_frame, num_frames):
        clip = self.__session.get_clip(clip_id)
        if not clip: return

        clip.edit_frames(edit, local_frame, num_frames)
        self.__update_retime_node(clip_id)

        self.SIG_PLAYLIST_MODIFIED.emit(clip.playlist_id)
        self.__emit_timewarp_modified_signal(clip.playlist_id, clip_id)

        return True

    def reset_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return

        clip.reset_frames()
        self.__update_retime_node(clip_id)

        self.SIG_PLAYLIST_MODIFIED.emit(clip.playlist_id)
        self.__emit_timewarp_modified_signal(clip.playlist_id, clip_id)
        return True

    def set_source_frames(self, clip_id, source_frames):
        clip = self.__session.get_clip(clip_id)
        if not clip: return

        clip.set_source_frames(source_frames)
        self.__update_retime_node(clip_id)

        self.SIG_PLAYLIST_MODIFIED.emit(clip.playlist_id)
        return True

    def are_frame_edits_allowed(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip:
            return False
        return clip.are_frame_edits_allowed()

    def export(self, path, output_color_space, blocking):
        if path.endswith(".rv"):
            commands.saveSession(path, True)
        else:
            export_movie = MuSymbol("export_utils.exportMovieOverRange")
            export_movie(commands.frameStart(), commands.frameEnd(), path, blocking, output_color_space)

    def core_preferences(self):
        def get_preferences_action(widget=None):
            if widget is None:
                app = QtWidgets.QApplication.instance()
                for widget in app.topLevelWidgets():
                    action = get_preferences_action(widget)
                    if action is not None:
                        return action
                return None
            for action in widget.actions():
                if action.text() == "Preferences...":
                    return action
            for child in widget.children():
                if isinstance(child, QtWidgets.QWidget):
                    action = get_preferences_action(child)
                    if action is not None:
                        return action
            return None
        action = get_preferences_action()
        if action:
            action.trigger()

    def set_timeline_api(self, timeline_api):
        self.__timeline_api = timeline_api

    def set_media_overlay(self, clip_id, overlay_type, overlay_data, overlay_id):
        clip = self.__session.get_clip(clip_id)
        if clip is None: return

        source_group = clip.get_custom_attr("rv_source_group")
        src_overlay_node = f"{source_group}_overlay"
        src_node = f"{source_group}_source"
        smi = commands.sourceMediaInfo(src_node)
        width, height = smi.get("width"), smi.get("height")

        if overlay_type == 1: # text
            ol_type = OverlayType.text
            media_overlay = TextOverlay.from_json(overlay_data)
            text = media_overlay.text
            font_path = media_overlay.font_path
            text_size = image_to_rv(width, height, media_overlay.size)
            text_red, text_green, text_blue, text_alpha = media_overlay.color
            pos_x, pos_y = media_overlay.position
            text_pos_x, text_pos_y = itview_to_rv(width, height, pos_x, pos_y)

            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.text", [text])
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.font", [font_path])
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.size", [text_size])
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.color",
                [[text_red, text_green, text_blue, text_alpha]])
            # origin at this position
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.position",
                [[text_pos_x, text_pos_y]])

            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.origin", ["center-center"])
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.scale", [1.0])
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.spacing", [0.8])
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.active", [1])
            clip.set_media_overlay_info(overlay_id, overlay_type, overlay_data)
            return overlay_id

        elif overlay_type == 2: # rect
            ol_type = OverlayType.rect
            media_overlay = RectOverlay.from_json(overlay_data)
            rect_width = (media_overlay.width / width) * (width/height)
            rect_height = (media_overlay.height / height)
            rect_red, rect_green, rect_blue, rect_alpha = media_overlay.color
            pos_x, pos_y = media_overlay.position
            rect_pos_x, rect_pos_y = itview_to_rv(width, height, pos_x, pos_y)

            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.width", [rect_width])
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.height", [rect_height])
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.color",
                [[rect_red, rect_green, rect_blue, rect_alpha]])
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.position",
                [[rect_pos_x, rect_pos_y]])
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.active", [1])
            clip.set_media_overlay_info(overlay_id, overlay_type, overlay_data)
            return overlay_id

        else:
            return None

    def toggle_media_overlay(self, clip_id, overlay_id, overlay_type, active):
        clip = self.__session.get_clip(clip_id)
        if clip is None: return
        source_group = clip.get_custom_attr("rv_source_group")
        src_overlay_node = f"{source_group}_overlay"
        src_node = f"{source_group}_source"

        if not isinstance(overlay_type, int): return

        if overlay_type == 0:
            prop_util.set_property(
                f"{src_overlay_node}.overlay.show", [1 if active else 0])
        elif overlay_type == 1: # text
            ol_type = OverlayType.text
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.active", [1 if active else 0])
        elif overlay_type == 2: # rect
            ol_type = OverlayType.rect
            prop_util.set_property(
                f"{src_overlay_node}.{ol_type}:{overlay_id}.active", [1 if active else 0])
        else:
           return

    def get_media_overlays_info(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if clip is None: return []

        return clip.get_media_overlays_info()
