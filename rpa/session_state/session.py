from rpa.session_state.playlist import Playlist
from rpa.session_state.clip import Clip
from rpa.session_state.viewport import Viewport
from rpa.session_state.attrs_metadata import AttrsMetadata
from rpa.session_state.timeline import Timeline
from rpa.session_state.utils import \
    insert_list_into_list, positive_list_move, negative_list_move, \
    move_list_items_to_index
from typing import List, Any, Optional
from rpa.utils.sequential_uuid_generator import SequentialUUIDGenerator
import os
import uuid
import gc


def obj_to_str(obj, indent=0, key="", visited=None):
    def get_name(class_name, name):
        n = name.removeprefix(f"_{class_name}__")
        return n if n == name else f"__{n}"

    if visited is None:
        visited = set()

    ref = id(obj)
    prefix = ' ' * indent

    # base types (str, int, float, bool, None)
    if isinstance(obj, (str, int, float, bool, type(None))):
        return f"{prefix}{key}{repr(obj)}"

    # lists, tuples, and sets
    if isinstance(obj, (list, tuple, set)):
        if ref in visited:
            return f"{prefix}{key}*"
        else:
            visited.add(ref)
            out = f"{prefix}{key}[\n"
            for item in obj:
                out += obj_to_str(item, indent + 4, visited=visited)
                out += "\n"
            out += f"{prefix}]"
            visited.remove(ref)
            return out

    # dictionaries
    if isinstance(obj, dict):
        if ref in visited:
            return f"{prefix}{key}*"
        else:
            visited.add(ref)
            out = f"{prefix}{key}{{\n"
            for key, value in obj.items():
                out += obj_to_str(value, indent + 4, key=f"{repr(key)}: ", visited=visited)
                out += "\n"
            out += f"{prefix}}}"
            visited.remove(ref)
            return out

    # custom objects
    if hasattr(obj, "__dict__"):
        if ref in visited:
            return f"{prefix}{key}*"
        else:
            visited.add(ref)
            out = f"{prefix}{key}{type(obj).__name__} {{\n"
            for attr, value in vars(obj).items():
                out += obj_to_str(value, indent + 4, key=f"{get_name(type(obj).__name__, attr)}: ", visited=visited)
                out += "\n"
            out += f"{prefix}}}"
            visited.remove(ref)
            return out

    # other objects (e.g., functions, modules)
    return f"{prefix}{key}{repr(obj)}"


class Session:
    def __init__(self):
        self.__name = "session"

        self.__id = os.environ.get("RPA_SESSION_ID", uuid.uuid4().hex)
        self.__playlist_uuid_generator = SequentialUUIDGenerator(
            os.environ.get("PLAYLIST_UUID_SEED", uuid.uuid4().hex))

        self.__playlists = {}
        self.__deleted_playlists = {}
        self.__activated_clip_indexes = []
        self.__custom_attrs = {}
        self.current_frame_mode = 0

        self.__viewport = Viewport()
        self.__attrs_metadata = AttrsMetadata(self)
        self.__timeline = Timeline(self)

        self.__create_if_empty()

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def viewport(self):
        return self.__viewport

    @property
    def attrs_metadata(self):
        return self.__attrs_metadata

    @property
    def timeline(self):
        return self.__timeline

    ###########################################################################
    # Playlist Methods                                                        #
    ###########################################################################

    def create_playlists(
        self, names:List[str], index:Optional[int]=None, ids=None):

        if ids is None: ids = [uuid.uuid4().hex for _ in  names]
        new_playlists = {}
        for id, name in zip(ids, names):
            new_playlists[id] = Playlist(id, name)

        old_playlist_ids = list(self.__playlists.keys())
        new_playlist_ids = list(new_playlists.keys())

        index = len(old_playlist_ids) if index is None else index
        playlist_ids = \
            insert_list_into_list(old_playlist_ids, new_playlist_ids, index)

        playlists = {}
        for playlist_id in playlist_ids:
            playlist = self.__playlists.get(playlist_id)
            if playlist is None:
                playlist = new_playlists.get(playlist_id)
            playlists[playlist_id] = playlist

        self.__playlists.clear()
        self.__playlists.update(playlists)

    def get_playlist_ids(self)->list:
        return list(self.__playlists.keys())

    def get_playlist(self, pl_id:str):
        playlist = self.__playlists.get(pl_id)
        if playlist is None:
            playlist = self.__deleted_playlists.get(pl_id)
        return playlist

    def move_playlists_to_index(self, index:int, ids):
        reordered_ids = \
            move_list_items_to_index(list(self.__playlists.keys()), ids, index)

        playlists = {}
        for id in reordered_ids:
            playlists[id] = self.__playlists.get(id)

        self.__playlists.clear()
        self.__playlists.update(playlists)

    def move_playlists_by_offset(self, offset:int, ids):
        to_move = []
        for id in ids:
            playlist = self.__playlists.get(id)
            if playlist is None: continue
            to_move.append(id)

        all_ids = list(self.__playlists.keys())
        if offset < 0:
            negative_list_move(all_ids, to_move, offset)
        else:
            positive_list_move(all_ids, to_move, offset)

        playlists = {}
        for id in all_ids:
            playlist = self.__playlists.get(id)
            playlists[id] = playlist

        self.__playlists.clear()
        self.__playlists.update(playlists)

    def delete_playlists(self, ids):
        for id in ids:
            self.__update_fg_bg_before_delete(id)
            self.__deleted_playlists[id] = self.__playlists.pop(id)
        self.__create_if_empty()

    def get_deleted_playlist_ids(self):
        return list(self.__deleted_playlists.keys())

    def restore_playlists(self, ids, index:int=None):
        restored_playlists = {}
        for id in ids:
            if self.__deleted_playlists.get(id) is None: continue
            restored_playlists[id] = self.__deleted_playlists.pop(id)

        index = len(self.__playlists.keys()) if index is None else index
        playlist_ids = insert_list_into_list(
            list(self.__playlists.keys()),
            list(restored_playlists.keys()), index)

        playlists = {}
        for playlist_id in playlist_ids:
            playlist = self.__playlists.get(playlist_id)
            if playlist is None:
                playlist = restored_playlists.get(playlist_id)
            playlists[playlist_id] = playlist

        self.__playlists.clear()
        self.__playlists.update(playlists)

    def delete_playlists_permanently(self, ids):
        for id in ids:
            if id in self.__playlists:
                self.__update_fg_bg_before_delete(id)
                playlist = self.__playlists.pop(id)
            else:
                playlist = self.__deleted_playlists.pop(id)
            playlist.delete()
        gc.collect()
        self.__create_if_empty()

    def __create_if_empty(self):
        if len(self.__playlists.keys()) > 0:
            return
        pl_id = self.__playlist_uuid_generator.next_uuid()
        playlist = Playlist(pl_id, "New Playlist")
        self.__playlists[pl_id] = playlist
        self.__viewport.fg = pl_id

    def __update_fg_bg_before_delete(self, id):
        if id == self.__viewport.bg: self.__viewport.bg  = None
        if id == self.__viewport.fg:
            if self.__viewport.bg is not None: self.__viewport.bg = None

            ids = list(self.__playlists.keys())
            if len(ids) > 1:
                index = ids.index(self.__viewport.fg)
                if index > 0:
                    index -= 1
                else:
                    index += 1
                self.__viewport.fg = ids[index]
            else:
                self.__viewport.fg = None

    def set_fg_playlist(self, id):
        self.__viewport.fg = id
        if self.__viewport.bg is None:
            self.__update_fg_active_clips()
        else:
            self.match_fg_bg_clip_indexes()

    def set_bg_playlist(self, id):
        self.__viewport.bg = id
        if self.__viewport.bg is not None: self.match_fg_bg_clip_indexes()

    def set_custom_playlist_attr(self, playlist_id, attr_id, value)->bool:
        playlist = self.__playlists.get(playlist_id)
        if not playlist: return False
        return playlist.set_custom_attr(attr_id, value)

    def get_custom_playlist_attr(self, playlist_id, attr_id)->Optional[Any]:
        playlist = self.__playlists.get(playlist_id)
        if not playlist: return None
        return playlist.get_custom_attr(attr_id)

    def get_custom_playlist_attr_ids(self, playlist_id)->List[str]:
        playlist = self.__playlists.get(playlist_id)
        if not playlist: return []
        return playlist.get_custom_attr_ids()

    #######################################################################
    # Clip Methods                                                        #
    #######################################################################

    def get_clip(self, id:str):
        return Clip.id_to_self.get(id)

    def update_activated_clip_indexes(self):
        fg_playlist = self.get_playlist(self.__viewport.fg)
        clip_ids = fg_playlist.clip_ids
        if len(clip_ids) == 0:
            return

        fg_active_clip_ids = fg_playlist.active_clip_ids
        self.__activated_clip_indexes.clear()
        for clip_id in fg_active_clip_ids:
            try:
                index = clip_ids.index(clip_id)
            except ValueError:
                continue
            self.__activated_clip_indexes.append(index)

    def match_fg_bg_clip_indexes(self):
        if self.__viewport.bg is None:
            return

        fg_playlist = self.get_playlist(self.__viewport.fg)
        clip_ids = fg_playlist.clip_ids
        if len(clip_ids) == 0:
            return

        fg_active_clip_ids = fg_playlist.active_clip_ids
        bg_playlist = self.get_playlist(self.__viewport.bg)
        if len(fg_active_clip_ids) == 0:
            bg_playlist.set_active_clips([])
        else:
            fg_sel_clip_indexes = []
            for clip_id in fg_active_clip_ids:
                try:
                    index = clip_ids.index(clip_id)
                except ValueError:
                    continue
                fg_sel_clip_indexes.append(index)

            bg_clip_ids = bg_playlist.clip_ids

            bg_clip_ids_to_activate = []
            for index in fg_sel_clip_indexes:
                try:
                    bg_clip_ids_to_activate.append(bg_clip_ids[index])
                except IndexError:
                    continue
            bg_playlist.set_active_clips(bg_clip_ids_to_activate)

    def clear(self):
        def delete_playlists(playlists):
            pl_ids = list(playlists.keys())
            for pl_id in pl_ids:
                playlist = playlists.pop(pl_id)
                playlist.delete()

        delete_playlists(self.__playlists)
        delete_playlists(self.__deleted_playlists)

        self.__activated_clip_indexes.clear()
        self.__custom_attrs.clear()
        self.current_frame_mode = 0

        gc.collect()
        self.__create_if_empty()

    def set_custom_session_attr(self, attr_id, value)->bool:
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_session_attr(self, attr_id)->Any:
        return self.__custom_attrs.get(attr_id)

    def get_custom_session_attr_ids(self)->List[str]:
        return list(self.__custom_attrs.keys())

    def set_custom_clip_attr(self, clip_id, attr_id, value)->bool:
        clip = Clip.id_to_self.get(clip_id)
        if not clip: return False
        return clip.set_custom_attr(attr_id, value)

    def get_custom_clip_attr(self, clip_id, attr_id)->Any:
        clip = Clip.id_to_self.get(clip_id)
        if not clip: return
        return clip.get_custom_attr(attr_id)

    def get_custom_clip_attr_ids(self, clip_id)->List[str]:
        clip = Clip.id_to_self.get(clip_id)
        if not clip: return []
        return clip.get_custom_attr_ids()

    def __update_fg_active_clips(self):
        if len(self.__activated_clip_indexes) == 0:
            return
        fg_playlist = self.get_playlist(self.__viewport.fg)
        clip_ids = fg_playlist.clip_ids
        if len(clip_ids) == 0:
            return
        fg_playlist.set_active_clips([])

        clip_ids_to_activate = []
        for index in self.__activated_clip_indexes:
            try:
                clip_ids_to_activate.append(clip_ids[index])
            except IndexError:
                continue
        fg_playlist.set_active_clips(clip_ids_to_activate)


    def __str__(self):
        return obj_to_str(self)

    def __repr__(self):
        return "Session"
