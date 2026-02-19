from rpa.session_state.transforms import \
    Interpolator, RotationInterpolator, DYNAMIC_TRANSFORM_ATTRS
from rpa.session_state.color_corrections import ColorCorrections
from rpa.session_state.annotations import Annotations
import copy



class Clip:
    id_to_self = {}
    def __init__(self, playlist_id, id, path, cc_uuid_generator):
        Clip.id_to_self[id] = self
        self.__playlist_id = playlist_id
        self.__id = id
        self.path = path
        self.__attrs = {}
        self.__custom_attrs = {}
        self.__color_corrections = ColorCorrections(cc_uuid_generator)
        self.__annotations = Annotations()

        # frame edits
        self.__source_frames = []
        self.__has_key_in_out_edits = False
        self.__has_frame_edits = False

        # media overlays
        self.__media_overlays = []

    @property
    def id(self):
        return self.__id

    @property
    def playlist_id(self):
        return self.__playlist_id

    @property
    def color_corrections(self):
        return self.__color_corrections

    @property
    def annotations(self):
        return self.__annotations

    @property
    def has_frame_edits(self)->bool:
        return self.__has_frame_edits

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def set_attr_value(self, id, value):
        if id in ("key_in", "key_out"):
            # This logic is based on the assumption that key_in and key_out
            # will always be set after media_start_frame and media_end_frame.
            media_start = self.__attrs.get("media_start_frame")
            media_end = self.__attrs.get("media_end_frame")
            if not self.__has_frame_edits:
                self.__attrs[id] = value
                key_in = self.__attrs.get("key_in")
                key_out = self.__attrs.get("key_out")
                self.__source_frames.clear()
                self.__source_frames = self.__generate_clamped_source_frames(
                    key_in, key_out, media_start, media_end
                )
                if key_in != media_start or key_out != media_end:
                    self.__has_key_in_out_edits = True
                else:
                    self.__has_key_in_out_edits = False
        else:
            self.__attrs[id] = value

    def __generate_clamped_source_frames(self, key_in, key_out, media_start, media_end):
        """
        Generate source frames list with clamping logic.

        - Frames before media_start are set to media_start value
        - Frames within media_start to media_end are incremental
        - Frames after media_end are set to media_end value

        Args:
            key_in: Start frame of the key range
            key_out: End frame of the key range
            media_start: First valid media frame
            media_end: Last valid media frame

        Returns:
            List of source frames with clamped values
        """
        key_in = media_start if key_in is None else key_in
        key_out = media_end if key_out is None else key_out
        source_frames = []
        for frame in range(key_in, key_out + 1):
            if frame < media_start:
                # Repeat media_start for frames before media range
                source_frames.append(media_start)
            elif frame > media_end:
                # Repeat media_end for frames after media range
                source_frames.append(media_end)
            else:
                # Normal incremental value within media range
                source_frames.append(frame)

        return source_frames

    def get_attr_value(self, id):
        return self.__attrs.get(id)

    def set_attr_value_at(self, id, frame, value):
        if id in DYNAMIC_TRANSFORM_ATTRS:
            self.__attrs[id]["key_values"][frame] = value
            self.update_interpolation(id)

    def get_attr_value_at(self, id, frame):
        if id in DYNAMIC_TRANSFORM_ATTRS:
            raw_attr_value = self.__attrs.get(id)
            if not raw_attr_value:
                return None
            key_values = raw_attr_value.get("key_values")
            if not key_values:
                return raw_attr_value.get("value")

            frame_values = raw_attr_value.get("frame_values")
            keys = list(key_values.keys())
            first_key = min(keys)
            last_key = max(keys)
            if frame <= first_key:
                value_at = key_values[first_key]
            elif frame >= last_key:
                value_at = key_values[last_key]
            else:
                value_at = frame_values.get(frame)
        else:
            value_at = self.get_attr_value(id)

        return value_at

    def clear_attr_value_at(self, id, frame):
        if id in DYNAMIC_TRANSFORM_ATTRS:
            key_values = self.__attrs.get(id).get("key_values")
            key_values.pop(frame, None)

    def get_key_values(self, id):
        if id in DYNAMIC_TRANSFORM_ATTRS:
            key_values = self.__attrs.get(id).get("key_values", {}) if self.__attrs.get(id) else {}
            return dict(sorted(key_values.items()))
        else:
            return {}

    def update_keyable_attrs(self, id, value):
        self.__attrs[id]["value"] = value
        self.__attrs[id]["key_values"] = {}
        self.__attrs[id]["frame_values"] = {}

    def update_interpolation(self, id):
        sorted_items = dict(sorted(self.__attrs[id].get("key_values").items()))
        keys = list(sorted_items.keys())
        values = list(sorted_items.values())

        first_key = keys[0]
        last_key = keys[-1]

        interpolated_values = {}

        if id == "dynamic_rotation":
            interpolator = RotationInterpolator(keys, values)
        else:
            interpolator = Interpolator(keys, values)

        for frame in range(first_key, last_key + 1):
            interpolated_values[frame] = interpolator.get(frame)

        self.__attrs[id]["frame_values"] = interpolated_values

    def are_frame_edits_allowed(self):
        return not self.__has_key_in_out_edits

    def edit_frames(self, edit, local_frame, num_frames):
        if self.__has_key_in_out_edits:
            print("frame edits are not allowed when key_in and/or key_out edits are present!")
            return

        if edit not in (1, -1): return
        if local_frame <= 0 or local_frame > len(self.__source_frames): return
        if num_frames <= 0: return

        frame_index = local_frame - 1
        if edit == 1: # hold
            source_frame = self.__source_frames[frame_index]
            hold_frames = [source_frame] * num_frames
            # Insert values after the current frame using slice assignment
            self.__source_frames[frame_index + 1:frame_index + 1] = hold_frames
        elif edit == -1: # drop
            del self.__source_frames[frame_index:frame_index + num_frames]

        self.__update_has_frame_edits()
        self.__set_timewarp_attr_values()

    def set_source_frames(self, source_frames):
        if self.__has_key_in_out_edits:
            print("frame edits are not allowed when key_in and/or key_out edits are present!")
            return
        self.__source_frames = source_frames
        self.__set_timewarp_attr_values()
        self.__update_has_frame_edits()

    def reset_frames(self):
        if self.__has_key_in_out_edits:
            print("reset frame edits are not allowed when key_in and/or key_out edits are present!")
            return
        key_in = self.__attrs.get("key_in")
        key_out = self.__attrs.get("key_out")
        media_start = self.__attrs.get("media_start_frame")
        media_end = self.__attrs.get("media_end_frame")
        self.__source_frames = self.__generate_clamped_source_frames(
            key_in, key_out, media_start, media_end
        )

        self.__update_has_frame_edits()
        self.__set_timewarp_attr_values()

    def __update_has_frame_edits(self):
        if len(self.__source_frames) <= 1:
            self.__has_frame_edits = False
            return

        for index in range(len(self.__source_frames) - 1):
            current_frame = self.__source_frames[index]
            next_frame = self.__source_frames[index + 1]

            # Check for held frames (duplicates)
            if current_frame == next_frame:
                self.__has_frame_edits = True
                return

            # Check for dropped frames (gaps greater than 1)
            # Normal sequence should increment by 1, so any gap > 1 indicates dropped frames
            if abs(next_frame - current_frame) > 1:
                self.__has_frame_edits = True
                return

        self.__has_frame_edits = False

    def get_source_frames(self):
        return self.__source_frames

    def get_timeline_frames(self):
        dissolve_length = self.__attrs.get("dissolve_length")
        if dissolve_length is not None and dissolve_length > 0:
            return self.__source_frames[:-dissolve_length]
        return self.__source_frames

    def __set_timewarp_attr_values(self):
        key_in = self.__attrs.get("key_in")
        if key_in is None: return

        if self.__has_frame_edits:
            tw_in = self.__source_frames[0]
            tw_out = tw_in - 1
            for _ in self.__source_frames:
                tw_out += 1
            tw_length = tw_out - tw_in + 1

            self.set_attr_value("timewarp_in", tw_in)
            self.set_attr_value("timewarp_out", tw_out)
            self.set_attr_value("timewarp_length", tw_length)
        else:
            self.set_attr_value("timewarp_in", None)
            self.set_attr_value("timewarp_out", None)
            self.set_attr_value("timewarp_length", None)

    def set_media_overlay_info(self, overlay_id, overlay_type, overlay_data):
        new_media_overlay = (overlay_id, overlay_type, overlay_data)
        for i, (id_, type_, data_) in enumerate(self.__media_overlays):
            if isinstance(overlay_id, str) and id_ == overlay_id and \
                isinstance(overlay_type, int) and type_ == overlay_type:
                self.__media_overlays[i] = new_media_overlay
                return

        if isinstance(overlay_id, str) and isinstance(overlay_type, int):
            self.__media_overlays.append(new_media_overlay)

    def get_media_overlays_info(self):
        return self.__media_overlays

    def get_attrs(self):
        return copy.deepcopy(self.__attrs)

    def delete(self):
        self.__playlist_id = None
        self.path = None
        self.__attrs.clear()
        self.__custom_attrs.clear()
        self.__color_corrections.delete()
        self.__annotations.delete()
        del Clip.id_to_self[self.__id]
        self.__id = None
        del self

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path
