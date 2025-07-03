from rpa.session_state.clip import Clip
from typing import List, Optional, Tuple, Union
from rpa.session_state.utils import \
    insert_list_into_list, negative_list_move, positive_list_move, \
    move_list_items_to_index


class Playlist:

    def __init__(self, id, name):
        self.name = name
        self.__clips = {}
        self.__id = id
        self.__custom_attrs = {}
        self.__active_clip_ids = []

    @property
    def id(self):
        return self.__id

    @property
    def clip_ids(self):
        return list(self.__clips.keys())

    @property
    def active_clip_ids(self):
        if self.__active_clip_ids: return self.__active_clip_ids[:]
        return list(self.__clips.keys())

    # Clip Methods
    ###############

    def create_clips(
        self, paths:List[Union[str, Tuple[str, str]]], ids:List[str], index:Optional[int]=None):
        new_clips = {}
        for id, path in zip(ids, paths):
            if isinstance(path, tuple):
                # from a tuple of (video_path, audio_path), take video_path
                path = path[0]
            new_clips[id] = Clip(self.__id, id, path)

        old_clip_ids = list(self.__clips.keys())
        new_clip_ids = list(new_clips.keys())

        index = len(old_clip_ids) if index is None else index
        clip_ids = \
            insert_list_into_list(old_clip_ids, new_clip_ids, index)

        clips = {}
        for clip_id in clip_ids:
            clip = self.__clips.get(clip_id)
            if clip is None:
                clip = new_clips.get(clip_id)
            clips[clip_id] = clip
        self.__clips.clear()
        self.__clips.update(clips)

        self.set_active_clips(new_clip_ids[0:1])

    def set_active_clips(self, ids:List[str]):
        self.__active_clip_ids.clear()
        def sort_based_on_play_order(id):
            clip = self.__clips.get(id)
            play_order = clip.get_attr_value("play_order")
            return 0 if play_order is None else play_order
        ids.sort(key=sort_based_on_play_order)
        self.__active_clip_ids.extend(ids)

    def move_clips_to_index(self, index:int, ids):
        reordered_ids = \
            move_list_items_to_index(list(self.__clips.keys()), ids, index)

        clips = {}
        for id in reordered_ids:
            clips[id] = self.__clips.get(id)

        self.__clips.clear()
        self.__clips.update(clips)

    def move_clips_by_offset(self, offset:int, ids):
        if len(ids) == 0:
            return
        all_ids = list(self.__clips.keys())
        if offset < 0:
            negative_list_move(all_ids, ids, offset)
        else:
            positive_list_move(all_ids, ids, offset)

        clips = {}
        for id in all_ids:
            clip = self.__clips.get(id)
            clips[id] = clip
        self.__clips.clear()
        self.__clips.update(clips)

    def delete_clips(self, ids):
        for id in ids:
            clip = self.__clips.pop(id)
            clip.delete()
        self.set_active_clips(
            list(set(self.__active_clip_ids).difference(set(ids))))

    # Playlist Methods
    ##################

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def delete(self):
        clip_ids = list(self.__clips.keys())
        for clip_id in clip_ids:
            clip = self.__clips.pop(clip_id)
            clip.delete()
        self.__custom_attrs.clear()
        self.name = None
        self.__id = None
