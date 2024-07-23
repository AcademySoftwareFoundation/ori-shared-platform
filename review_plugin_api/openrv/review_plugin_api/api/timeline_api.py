from PySide2 import QtCore
from rv import runtime
from rv import extra_commands as rve
from rv import commands as rvc
from exceptions import SingletonInstantiatedException
import numpy as np


def set_property(prop, values):
    """
    Helper function for setting RV's property. It automatically detects the type and dimension
    of the property values.

    Args:
        prop (str): Name of the property.
        values (list): List of values to be set.
    """
    if not values:
        if rvc.propertyExists(prop):
            rvc.deleteProperty(prop)
        return
    def _(prop_type, width, setter):
        if not rvc.propertyExists(prop):
            rvc.newProperty(prop, prop_type, width)
        return setter(prop, values, True)
    value = values[0]
    width = 1
    if isinstance(value, list):
        width = len(value)
        values = sum(values, [])
        value = value[0]
    if isinstance(value, int):
        return _(rvc.IntType, width, rvc.setIntProperty)
    if isinstance(value, float):
        return _(rvc.FloatType, width, rvc.setFloatProperty)
    if isinstance(value, str):
        return _(rvc.StringType, width, rvc.setStringProperty)
    raise TypeError("Unsupported property type")

def convert_to_global_frame(frame, node):
    """ Function that helps convert frame relative to node to global frame.
        Source frame (1001...) can be converted to global frame as long as the
        node provided is the source. If stack node provided, for example,
        frame in range (1...) needs to be given.
        Return -1 if unable to convert
    """
    temp_prop = f"{node}.find.frames"
    if not rvc.propertyExists(temp_prop):
        set_property(temp_prop, [frame])
    global_frame_map = rvc.mapPropertyToGlobalFrames("find.frames", 1)
    rvc.deleteProperty(temp_prop)
    if len(global_frame_map) > 0:
        return global_frame_map[0]
    return -1


class TimelineApi(QtCore.QObject):
    __instance = None
    SIG_FRAME_CHANGED = QtCore.Signal(int) # frame
    SIG_FRAME_COUNT_CHANGED = QtCore.Signal(int) # frame count
    SIG_PLAY_STATUS_CHANGED = QtCore.Signal(bool, bool) # playing, forward
    SIG_NEW_MEDIA_ADDED = QtCore.Signal()

    @classmethod
    def get_instance(cls):
        """Returns the sigleton instance of ActionsHeader"""
        if cls.__instance is None:
            cls.__instance = TimelineApi()
        return cls.__instance

    def __init__(self):
        if TimelineApi.__instance is not None:
            raise SingletonInstantiatedException()
        TimelineApi.__instance = self
        super().__init__()
        self.__clip_mode = False

    def is_empty(self):
        return rve.isSessionEmpty()

    def is_playing(self):
        return rvc.isPlaying()

    def is_forward(self):
        return rvc.inc() > 0

    def set_playing(self, frame, playing, forward):
        if playing:
            rvc.play()
            if forward != rve.isPlayingForwards():
                rve.toggleForwardsBackwards()
        else:
            rvc.stop()
            rvc.setFrame(frame)

    def goto_frame(self, frame, clip_mode):
        rvc.stop()
        if clip_mode:
            sources = rvc.sourcesAtFrame(rvc.frame())
            if len(sources) == 0:
                # frame outside of appropriate range. Use without conversion,
                # will lead to either going to beginning or end
                rvc.setFrame(frame)
                return
            rvc.setFrame(convert_to_global_frame(frame, sources[0]))
        else:
            rvc.setFrame(frame)

    def get_start_frame(self, clip_mode=False):
        if not clip_mode:
            return 1
        return self.__get_key_in()

    def get_end_frame(self, clip_mode=False):
        if not clip_mode:
            return rvc.frameEnd()
        return self.__get_key_out()

    def get_frame_range(self):
        return [rvc.frameStart(), rvc.frameEnd()]

    def get_frame_count(self, clip_mode):
        if not clip_mode:
            return rvc.outPoint()-rvc.inPoint()+1

        key_in = self.__get_key_in()
        key_out = self.__get_key_out()
        return key_out - key_in + 1

    def get_current_frame(self, clip_mode):
        if not clip_mode:
            frame = rvc.frame()
            frame_count = self.get_frame_count(clip_mode)
            if frame < 1 or frame > frame_count:
                key_in = self.__get_key_in()
                return frame - key_in + 1
            return frame
        frame = rve.sourceFrame(rvc.frame())
        return frame

    def get_current_source_frame(self):
        return rve.sourceFrame(rvc.frame())

    def __set_view_node(self, view_node_name):
        playing = rvc.isPlaying()
        if playing:
            rvc.stop()
        rvc.setViewNode(view_node_name)
        if playing:
            rvc.play()
        else:
            rvc.redraw()

    def set_sequence_view(self):
        self.__set_view_node("defaultSequence")

    def set_stack_view(self):
        self.__set_view_node("defaultStack")

    def set_layout_view(self):
        self.__set_view_node("defaultLayout")

    def set_stack_mode_replace(self):
        for node_name in rvc.nodesOfType("RVStack"):
            rvc.setStringProperty(f"{node_name}.composite.type", ["replace"])

    def set_stack_mode_over(self):
        for node_name in rvc.nodesOfType("RVStack"):
            rvc.setStringProperty(f"{node_name}.composite.type", ["over"])

    def set_stack_mode_add(self):
        for node_name in rvc.nodesOfType("RVStack"):
            rvc.setStringProperty(f"{node_name}.composite.type", ["add"])

    def set_stack_mode_difference(self):
        for node_name in rvc.nodesOfType("RVStack"):
            rvc.setStringProperty(f"{node_name}.composite.type", ["difference"])

    def set_stack_mode_inverted_difference(self):
        for node_name in rvc.nodesOfType("RVStack"):
            rvc.setStringProperty(f"{node_name}.composite.type", ["-difference"])

    def get_volume(self):
        rv_volume = rvc.getFloatProperty("#RVSoundTrack.audio.volume")[0]
        float_volume = rv_volume * 100
        volume = int(float_volume)
        frac = float_volume - volume
        if frac >= 0.5:
            volume = volume + 1
        return volume

    def set_volume(self, volume):
        volume = volume / 100.0
        rvc.setFloatProperty(
            "#RVSoundTrack.audio.volume", [volume])

    def toggle_mute(self, state):
        rvc.setIntProperty(
            "#RVSoundTrack.audio.mute", [1 if state else 0])

    def emit_frame_changed(self):
        self.SIG_FRAME_CHANGED.emit(self.get_current_frame(self.__clip_mode))

    def emit_play_status_changed(self):
        self.SIG_PLAY_STATUS_CHANGED.emit(
            rvc.isPlaying(), rvc.inc() > 0)

    def emit_new_media_added(self):
        self.SIG_NEW_MEDIA_ADDED.emit()

    def emit_frame_count_changed(self):
        self.SIG_FRAME_COUNT_CHANGED.emit(rvc.frameEnd())

    def __get_default_start_frame(self):
        frame = rvc.frame()
        # copied from clip_attr_key_in.py
        sources = rvc.sourcesAtFrame(frame)
        if len(sources) == 0:
            return 1
        source = sources[0]
        media_info = rvc.sourceMediaInfo(source)
        # use the fact that when key in changed, startFrame stays the same
        default_start_frame = media_info.get("startFrame")
        return default_start_frame

    def __get_key_in(self):
        # copied from clip_attr_key_in.py
        frame = rvc.frame()
        # copied from clip_attr_key_in.py
        sources = rvc.sourcesAtFrame(frame)
        if len(sources) == 0:
            return 1
        source = sources[0]
        key_in = rvc.getIntProperty(f"{source}.cut.in")[0]
        media_info = rvc.sourceMediaInfo(source)
        if key_in == (np.iinfo(np.int32).max * -1):
            key_in = media_info.get("startFrame")
        return key_in

    def __get_key_out(self):
        # copied from clip_attr_key_out.py
        frame = rvc.frame()
        # copied from clip_attr_key_in.py
        sources = rvc.sourcesAtFrame(frame)
        if len(sources) == 0:
            return 1
        source = sources[0]
        key_in = rvc.getIntProperty(f"{source}.cut.out")[0]
        media_info = rvc.sourceMediaInfo(source)
        if key_in == (np.iinfo(np.int32).max):
            key_in = media_info.get("endFrame")
        return key_in

    def __frame_to_timecode(self, frame, clip_mode):
        # OpenRV starts at 00 while itview4 start at 01, so we need to add extra frames
        timecode = runtime.eval(
            "require timeline;"
            "timeline.Timeline.globalTimeCode({0});".format(frame+1), []
        ).replace('"', '')
        # OpenRV does not include hours if it's 0. We can just manually add them
        timecode_split = timecode.split(":")
        if len(timecode_split) < 4:
            timecode = "00:" + timecode

        # if in clip/source mode, add 1 hour
        if clip_mode:
            timecode_split = timecode.split(":")
            hours = timecode_split[0]
            hours = "0" + str(int(hours) + 1) if int(hours) + 1 < 10 else str(int(hours) + 1)
            timecode = hours + ":" + ':'.join(timecode_split[1:])

        # Itview 4 has . before frames, but OpenRV has :
        timecode_split = timecode.split(":")
        timecode = ":".join(timecode_split[:-1]) + "." + timecode_split[-1]
        return timecode

    def get_start_timecode(self, clip_mode):
        if not clip_mode:
            return self.__frame_to_timecode(self.get_start_frame(clip_mode=clip_mode), clip_mode)

        default_start_frame = self.__get_default_start_frame()
        key_in = self.__get_key_in()
        return self.__frame_to_timecode(key_in - default_start_frame + 1, clip_mode)

    def get_current_timecode(self, clip_mode):
        if not clip_mode:
            current_frame = self.get_current_frame(clip_mode)
            # OpenRV starts at 00 while itview4 start at 1, so we need to add extra frames
            timecode = self.__frame_to_timecode(current_frame, clip_mode)
            return timecode

        key_in = self.__get_key_in()
        current_frame = self.get_current_frame(clip_mode=clip_mode)
        timecode = self.__frame_to_timecode(current_frame - key_in + 1, clip_mode)
        return timecode

    def get_end_timecode(self, clip_mode):
        if not clip_mode:
            return self.__frame_to_timecode(self.get_end_frame(clip_mode=clip_mode), clip_mode)

        default_start_frame = self.__get_default_start_frame()
        key_out = self.__get_key_out()
        return self.__frame_to_timecode(key_out - default_start_frame + 1, clip_mode)

    def get_total_timecode(self, clip_mode):
        return self.__frame_to_timecode(self.get_frame_count(clip_mode), clip_mode)

    def __frame_to_seconds(self, frame):
        timecode = runtime.eval(
            "require timeline;"
            "timeline.Timeline.seconds({0});".format(frame), []
        )
        return timecode

    def get_start_seconds(self):
        frame = rvc.frame()
        # copied from clip_attr_key_in.py
        sources = rvc.sourcesAtFrame(frame)
        if len(sources) == 0:
            return 1
        source = sources[0]
        media_info = rvc.sourceMediaInfo(source)

        return rvc.frameStart()
        # return self.__frame_to_seconds(self.get_start_frame())

    def get_current_seconds(self, clip_mode):
        return self.__frame_to_seconds(self.get_current_frame(clip_mode))

    def get_end_seconds(self):
        return rvc.frameEnd()

    def __frames_to_feet(self, frame):
        # Function to convert frames to feet. This was adapted from
        # cutlistthingy implementation
        return '{:.3f}'.format(frame/16.0)

    def get_start_feet(self, clip_mode):
        if not clip_mode:
            return self.__frames_to_feet(self.get_start_frame(clip_mode))

        default_start_frame = self.__get_default_start_frame()
        key_in = self.__get_key_in()
        return self.__frames_to_feet(key_in - default_start_frame + 1)

    def get_current_feet(self, clip_mode):
        if not clip_mode:
            return self.__frames_to_feet(self.get_current_frame(clip_mode))

        key_in = self.__get_key_in()
        current_frame = self.get_current_frame(clip_mode)
        return self.__frames_to_feet(current_frame - key_in + 1)

    def get_end_feet(self, clip_mode):
        if not clip_mode:
            return self.__frames_to_feet(self.get_end_frame(clip_mode))

        default_start_frame = self.__get_default_start_frame()
        key_out = self.__get_key_out()
        return self.__frames_to_feet(key_out - default_start_frame + 1)

    def get_total_feet(self, clip_mode):
        return self.__frames_to_feet(self.get_frame_count(clip_mode))

    def set_clip_mode(self, clip_mode):
        self.__clip_mode = clip_mode
