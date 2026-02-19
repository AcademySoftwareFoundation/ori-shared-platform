"""Color corrector module."""
from PySide2 import QtCore
from itview.skin.rpa_skin.attr_utils import make_callables


class ColorApiSkin(QtCore.QObject):

    def __init__(self, rpa_tx, session):
        super().__init__()
        self.__rpa_tx = rpa_tx
        self.__session = session

        make_callables(self.__rpa_tx, self)

    def set_channel(self, channel:int):
        self.__session.viewport.color_channel = channel
        return self.__rpa_tx.set_channel(channel)

    def get_channel(self):
        return self.__session.viewport.color_channel

    def set_fstop(self, value):
        self.__session.viewport.fstop = value
        return self.__rpa_tx.set_fstop(value)

    def get_fstop(self):
        return self.__session.viewport.fstop

    def set_gamma(self, value):
        self.__session.viewport.gamma = value
        return self.__rpa_tx.set_gamma(value)

    def get_gamma(self):
        return self.__session.viewport.gamma

    def get_cc_ids(self, clip_id, frame=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.color_corrections.get_cc_ids(frame=frame)

    def move_cc(self, clip_id, from_index, to_index, frame=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.move_cc(from_index, to_index, frame)
        return self.__rpa_tx.move_cc(clip_id, from_index, to_index, frame)

    def append_ccs(self, clip_id, names, frame=None, cc_ids=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.append_ccs(names, frame=frame, cc_ids=cc_ids)
        return self.__rpa_tx.append_ccs(
            clip_id, names, frame=frame, cc_ids=cc_ids)

    def delete_ccs(self, clip_id, cc_ids, frame=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.delete_ccs(cc_ids, frame)
        return self.__rpa_tx.delete_ccs(clip_id, cc_ids, frame)

    def get_frame_of_cc(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return None
        return clip.color_corrections.get_frame_of_cc(cc_id)

    def get_nodes(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.color_corrections.get_nodes(cc_id)

    def get_node_count(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_node_count(cc_id)

    def get_node(self, clip_id, cc_id, node_index):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_node(cc_id, node_index)

    def append_nodes(self, clip_id, cc_id, nodes):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.append_nodes(cc_id, nodes)
        return self.__rpa_tx.append_nodes(clip_id, cc_id, nodes)

    def clear_nodes(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.clear_nodes(cc_id)
        return self.__rpa_tx.clear_nodes(clip_id, cc_id)

    def delete_node(self, clip_id, cc_id, node_index):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.delete_node(cc_id, node_index)
        return self.__rpa_tx.delete_node(clip_id, cc_id, node_index)

    def set_node_properties(
        self, clip_id, cc_id, node_index, properties):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.set_node_properties(cc_id, node_index, properties)
        return self.__rpa_tx.set_node_properties(
            clip_id, cc_id, node_index, properties)

    def get_node_properties(self, clip_id, cc_id, node_index, property_names):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.color_corrections.get_node_properties(cc_id, node_index, property_names)

    def is_modified(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        return clip.color_corrections.is_modified(cc_id)

    def set_name(self, clip_id, cc_id, name):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        clip.color_corrections.set_name(cc_id, name)
        return self.__rpa_tx.set_name(clip_id, cc_id, name)

    def get_name(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_name(cc_id)

    def create_region(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.create_region(cc_id)
        return self.__rpa_tx.create_region(clip_id, cc_id)

    def has_region(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        return clip.color_corrections.has_region(cc_id)

    def append_shape_to_region(self, clip_id, cc_id, points):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.append_shape_to_region(cc_id, points)
        return self.__rpa_tx.append_shape_to_region(clip_id, cc_id, points)

    def set_transient_points(self, clip_id, cc_id, token, points):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.set_transient_points(cc_id, token, points)
        return self.__rpa_tx.set_transient_points(clip_id, cc_id, token, points)

    def append_transient_points(self, clip_id, cc_id, token, points):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.append_transient_points(cc_id, token, points)
        return self.__rpa_tx.append_transient_points(clip_id, cc_id, token, points)

    def delete_transient_points(self, clip_id, cc_id, token):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        clip.color_corrections.delete_transient_points(cc_id, token)
        return self.__rpa_tx.delete_transient_points(clip_id, cc_id, token)

    def delete_region(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.delete_region(cc_id)
        return self.__rpa_tx.delete_region(clip_id, cc_id)

    def set_region_falloff(self, clip_id, cc_id, falloff):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.set_region_falloff(cc_id, falloff)
        return self.__rpa_tx.set_region_falloff(clip_id, cc_id, falloff)

    def get_region_falloff(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_region_falloff(cc_id)

    def mute(self, clip_id, cc_id, value):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.set_mute(cc_id, value)
        return self.__rpa_tx.mute(clip_id, cc_id, value)

    def is_mute(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        return clip.color_corrections.is_mute(cc_id)

    def mute_all(self, clip_id, value):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.mute_all(value)
        return self.__rpa_tx.mute_all(clip_id, value)

    def is_mute_all(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        return clip.color_corrections.is_mute_all()

    def set_read_only(self, clip_id, cc_id, value):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.set_read_only(cc_id, value)
        return self.__rpa_tx.set_read_only(clip_id, cc_id, value)

    def is_read_only(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        return clip.color_corrections.is_read_only(cc_id)

    def get_rw_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.color_corrections.get_rw_frames()

    def get_ro_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.color_corrections.get_ro_frames()

    def set_ro_ccs(self, ro_ccs):
        for clip_id, ccs in ro_ccs.items():
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            clip.color_corrections.set_ro_ccs(ccs)
        return self.__rpa_tx.set_ro_ccs(ro_ccs)

    def set_frame_ro_ccs(self, clip_id, frame, ccs):
        clip = self.__session.get_clip(clip_id)
        if clip:
            clip.color_corrections.set_frame_ro_ccs(frame, ccs)
        return self.__rpa_tx.set_frame_ro_ccs(clip_id, frame, ccs)

    def get_ro_ccs(self, clip_id:str, frame=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_ro_ccs(frame)

    def set_rw_ccs(self, rw_ccs):
        for clip_id, ccs in rw_ccs.items():
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            clip.color_corrections.set_rw_ccs(ccs)
        return self.__rpa_tx.set_rw_ccs(rw_ccs)

    def update_frame_rw_ccs(self, clip_id, frame, ccs):
        clip = self.__session.get_clip(clip_id)
        if clip:
            clip.color_corrections.update_frame_rw_ccs(frame, ccs)
        return self.__rpa_tx.update_frame_rw_ccs(clip_id, frame, ccs)

    def get_rw_ccs(self, clip_id:str, frame=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_rw_ccs(frame)

    def delete_ro_ccs(self, clips):
        for clip_id in clips:
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            clip.color_corrections.delete_ro_ccs()
        return self.__rpa_tx.delete_ro_ccs(clips)
