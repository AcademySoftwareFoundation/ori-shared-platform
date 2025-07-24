import uuid
import opentimelineio as otio
from rpa.session_state.annotations import Annotation
from rpa.session_state.color_corrections import ColorCorrection
from rpa.widgets.session_io import constants as C


class OTIOReader(object):

    def __init__(self, rpa, main_window, feedback):
        super().__init__()

        self.__session_api = rpa.session_api
        self.__annotation_api = rpa.annotation_api
        self.__color_api = rpa.color_api
        self.__feedback = feedback
        self.__status_bar = main_window.statusBar()

    def read_otio_file(self, filepath):
        otio_timeline = otio.adapters.read_from_file(filepath)
        success = self.__create_session_from_otio(otio_timeline)

        if success:
            self.__status_bar.showMessage(
                f"Loaded session from {filepath}", 3000)
            return True
        else:
            self.__status_bar.showMessage(
                f"Failed to load session from {filepath}", 3000)
            return False

    def __create_session_from_otio(self, otio_timeline):
        timeline_name = otio_timeline.name
        fg_playlist_id = None
        bg_playlist_id = None
        rw_attrs_to_set = []
        keyable_attrs_to_set = []
        rw_annos = {}
        rw_ccs = {}

        attrs = self.__session_api.get_attrs()
        rw_attrs = self.__session_api.get_read_write_attrs()

        try:
            tracks = otio_timeline.tracks
            for track in tracks:
                playlist_name = track.name if track.name else ""
                playlist_id = self.__session_api.create_playlists([playlist_name])[0]

                playlist_metadata = track.metadata.get(C.ITVIEW_METADATA_KEY)
                is_fg = playlist_metadata.get("foreground", None)
                is_bg = playlist_metadata.get("background", None)
                if is_fg:
                    fg_playlist_id = playlist_id
                if is_bg:
                    bg_playlist_id = playlist_id

                clip_ids = []
                clip_paths = []

                for clip in track:
                    clip_media = clip.media_reference.target_url

                    if clip_media is None:
                        continue

                    clip_id = uuid.uuid4().hex
                    clip_ids.append(clip_id)
                    clip_paths.append(clip_media)
                    clip_attr_values = clip.metadata[C.ITVIEW_METADATA_KEY]

                    for attr_id, value in clip_attr_values.items():
                        if attr_id in attrs:
                            if self.__session_api.is_attr_keyable(attr_id):
                                key_values = value.get("key_values")
                                for frame, dynamic_value in key_values.items():
                                    keyable_attrs_to_set.append(
                                        (playlist_id, clip_id, attr_id, int(frame), float(dynamic_value)))
                            elif attr_id in rw_attrs:
                                rw_attrs_to_set.append((playlist_id, clip_id, attr_id, value))
                        else:
                            if attr_id == "annotations":
                                for frame, anno in value["rw"].items():
                                    rw_annos.setdefault(clip_id, {})[int(frame)] = \
                                        Annotation().__setstate__(anno)
                            elif attr_id == "color_corrections":
                                for frame, cc in value["rw"]:
                                    frame = int(frame) if frame is not None else None
                                    converted_cc = self.__convert_cc_nodes(cc)
                                    rw_ccs.setdefault(clip_id, []).append(
                                        (frame, ColorCorrection().__setstate__(converted_cc)))

                self.__session_api.create_clips(playlist_id, clip_paths, ids=clip_ids)

            if rw_attrs_to_set:
                self.__session_api.set_attr_values(rw_attrs_to_set)
            if keyable_attrs_to_set:
                self.__session_api.set_attr_values_at(keyable_attrs_to_set)

            # Feedback: Annotations & Color Corrections
            if self.__feedback:
                if rw_annos:
                    self.__annotation_api.set_rw_annotations(rw_annos)
                if rw_ccs:
                    self.__color_api.set_rw_ccs(rw_ccs)

            if fg_playlist_id is not None:
                self.__session_api.set_fg_playlist(fg_playlist_id)
            if bg_playlist_id is not None:
                self.__session_api.set_bg_playlist(bg_playlist_id)

            return True

        except Exception as exception:
            print(f"Failed to load {timeline_name}: {exception}")
            return False

    def __convert_cc_nodes(self, cc):
        color_timer = {}
        grade = {}
        converted_cc = {}

        for cc_key, cc_value in cc.items():
            if cc_key == "nodes":
                for cc_node in cc_value:
                    if cc_node.get("class_name") == "ColorTimer":
                        for cc_node_key, cc_node_value in cc_node.items():
                            if isinstance(cc_node_value, (otio._otio.AnyDictionary, dict)):
                                color_timer[cc_node_key] = dict(cc_node_value)
                            elif isinstance(cc_node_value, (otio._otio.AnyVector, tuple)):
                                color_timer[cc_node_key] = tuple(cc_node_value)
                            else:
                                color_timer[cc_node_key] = cc_node_value
                    if cc_node.get("class_name") == "Grade":
                        for cc_node_key, cc_node_value in cc_node.items():
                            if isinstance(cc_node_value, (otio._otio.AnyDictionary, dict)):
                                grade[cc_node_key] = dict(cc_node_value)
                            elif isinstance(cc_node_value, (otio._otio.AnyVector, tuple)):
                                grade[cc_node_key] = tuple(cc_node_value)
                            else:
                                grade[cc_node_key] = cc_node_value
            else:
                converted_cc[cc_key] = cc_value

        converted_cc["id"] = uuid.uuid4().hex
        converted_cc["nodes"] = [color_timer, grade]

        return converted_cc
