import os
import re
import opentimelineio as otio
from rpa.widgets.session_io import constants as C

class OTIOWriter(object):

    def __init__(self, rpa, main_window, feedback):
        super().__init__()

        self.__session_api = rpa.session_api
        self.__annotation_api = rpa.annotation_api
        self.__color_api = rpa.color_api
        self.__feedback = feedback
        self.__status_bar = main_window.statusBar()

    def write_otio_file(self, file_path:str):
        timeline = otio.schema.Timeline()

        playlist_ids = self.__session_api.get_playlists()
        for playlist_id in playlist_ids:
            track = self.__create_otio_track(playlist_id)

            clip_ids = self.__session_api.get_clips(playlist_id)
            for clip_id in clip_ids:
                clip = self.__create_otio_clip(playlist_id, clip_id)
                track.append(clip)

            timeline.tracks.append(track)

        timeline.name = os.path.splitext(os.path.basename(file_path))[0]
        success = otio.adapters.write_to_file(timeline, file_path)
        if success:
            self.__status_bar.showMessage(
                f"Current session saved successfully in {file_path}", 3000)
            return True
        else:
            return False

    def __create_otio_track(self, playlist_id:str):
        playlist_name = self.__session_api.get_playlist_name(playlist_id)
        playlist_metadata = self.__get_playlist_metadata(playlist_id)

        track = otio.schema.Track(
            name=playlist_name,
            kind=otio.schema.TrackKind.Video
        )
        track.metadata[C.ITVIEW_METADATA_KEY] = playlist_metadata

        return track

    def __get_playlist_metadata(self, playlist_id:str):
        playlist_metadata = {}
        fg_playlist_id = self.__session_api.get_fg_playlist()
        bg_playlist_id = self.__session_api.get_bg_playlist()

        if playlist_id == fg_playlist_id:
            playlist_metadata["foreground"] = True
        if playlist_id == bg_playlist_id:
            playlist_metadata["background"] = True

        return playlist_metadata

    def __create_otio_clip(self, playlist_id:str, clip_id:str):
        media_reference = self.__create_media_reference(playlist_id, clip_id)
        clip_metadata = self.__get_clip_metadata(playlist_id, clip_id)

        key_in = self.__session_api.get_attr_value(clip_id, "key_in")
        key_out = self.__session_api.get_attr_value(clip_id, "key_out")
        video_fps = self.__session_api.get_attr_value(clip_id, "media_fps")
        start_frame = self.__session_api.get_attr_value(clip_id, "media_start_frame")
        end_frame = self.__session_api.get_attr_value(clip_id, "media_end_frame")

        if start_frame == key_in and end_frame == key_out:
            source_range = None
        else:
            source_range = self.__get_time_range(key_in, key_out, video_fps)
        source_range = self.__get_time_range(key_in, key_out, video_fps)

        clip = otio.schema.Clip(
            media_reference=media_reference,
            source_range=source_range
        )
        clip.metadata[C.ITVIEW_METADATA_KEY] = clip_metadata

        return clip

    def __create_media_reference(self, playlist_id:str, clip_id:str):
        video_path = self.__session_api.get_attr_value(clip_id, "media_path")
        video_fps = self.__session_api.get_attr_value(clip_id, "media_fps")
        start_frame = self.__session_api.get_attr_value(clip_id, "media_start_frame")
        end_frame = self.__session_api.get_attr_value(clip_id, "media_end_frame")

        available_range = self.__get_time_range(start_frame, end_frame, video_fps)
        is_img_seq, frame_zero_padding = self.__is_image_sequence(video_path)

        if is_img_seq:
            media_ref = otio.schema.ImageSequenceReference(
                target_url_base=video_path,
                available_range=available_range,
                frame_zero_padding=frame_zero_padding
            )
        else:
            media_ref = otio.schema.ExternalReference(
                target_url=video_path,
                available_range=available_range
            )

        return media_ref

    def __get_time_range(self, start_frame:int, end_frame:int, fps:float):
        start_time, duration = \
            self.frames_to_otio_rational_times(start_frame, end_frame, fps)

        if not start_time or not duration:
            return None

        time_range = otio.opentime.TimeRange(
            start_time=start_time,
            duration=duration
        )
        return time_range

    def frames_to_otio_rational_times(self, start_frame:int, end_frame:int, fps:float):
        if start_frame is None or end_frame is None or not fps:
            return None, None

        start_time = otio.opentime.RationalTime(start_frame, rate=fps)
        end_time_inclusive = otio.opentime.RationalTime(end_frame, rate=fps)
        duration = otio.opentime.RationalTime.duration_from_start_end_time_inclusive(
            start_time, end_time_inclusive)
        return start_time, duration

    def __is_image_sequence(self, media_path:str):
        basename = os.path.basename(media_path)
        frame_zero_padding = None
        image_seq_pattern = re.findall("\.%0\d+d\.", basename)
        if image_seq_pattern:
            frame_zero_padding = int(re.search("\d+", image_seq_pattern[0]).group(0))
        else:
            image_seq_pattern = re.findall("\.\d+-\d+#|@+", basename)
            if image_seq_pattern:
                pattern = re.search("#|@+", image_seq_pattern[0]).group(0)
                frame_zero_padding = 4 if "#" in pattern else len(pattern)

        return (len(image_seq_pattern) == 1, frame_zero_padding)

    def __get_clip_metadata(self, playlist_id:str, clip_id:str):
        clip_metadata = {}
        rw_attrs = self.__session_api.get_read_write_attrs()
        keyable_attrs = self.__session_api.get_keyable_attrs()

        for rw_attr in rw_attrs:
            if "sg_" in rw_attr:
                continue
            default_attr_value = self.__session_api.get_default_attr_value(rw_attr)
            attr_value = self.__session_api.get_attr_value(clip_id, rw_attr)
            if attr_value != default_attr_value:
                clip_metadata[rw_attr] = attr_value

        for keyable_attr in keyable_attrs:
            default_attr_value = self.__session_api.get_default_attr_value(keyable_attr)
            attr_value = self.__session_api.get_attr_value(clip_id, keyable_attr)
            if attr_value != default_attr_value:
                key_value_dict = \
                    {str(key): value for key, value in attr_value.get("key_values").items()}
                print('key_value_dict', key_value_dict, type(key_value_dict))
                clip_metadata.setdefault(keyable_attr, {})["key_values"] = key_value_dict

        # Feedback: Annotations & Color Corrections
        if self.__feedback:
            # RW Annotations
            for frame in self.__annotation_api.get_rw_frames(clip_id):
                rw_anno = self.__annotation_api.get_rw_annotation(clip_id, frame)
                clip_metadata.setdefault("annotations", {}).\
                    setdefault("rw", {})[str(frame)] = rw_anno.__getstate__()

            # RW Clip CCs
            clip_rw_ccs = self.__color_api.get_rw_ccs(clip_id)
            clip_rw_ccs = [(None, cc.__getstate__()) for cc in clip_rw_ccs if \
                self.__color_api.is_modified(clip_id, cc.__getstate__().get("id"))]
            if clip_rw_ccs:
                clip_metadata.setdefault("color_corrections", {}).\
                    setdefault("rw", []).extend(clip_rw_ccs)

            # RW Frame CCs
            for frame in self.__color_api.get_rw_frames(clip_id):
                clip_rw_ccs = self.__color_api.get_rw_ccs(clip_id, frame)
                clip_rw_ccs = [(str(frame), cc.__getstate__()) for cc in clip_rw_ccs if \
                    self.__color_api.is_modified(clip_id, cc.__getstate__().get("id"))]
                if clip_rw_ccs:
                    clip_metadata.setdefault("color_corrections", {}).\
                        setdefault("rw", []).extend(clip_rw_ccs)

        return clip_metadata
