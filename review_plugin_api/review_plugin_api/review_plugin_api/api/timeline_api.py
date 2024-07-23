from PySide2 import QtCore
from review_plugin_api.api._delegate_mngr import DelegateMngr


class TimelineApi(QtCore.QObject):
    SIG_FRAME_CHANGED = QtCore.Signal(int) # frame
    SIG_FRAME_COUNT_CHANGED = QtCore.Signal(int) # frame count
    SIG_PLAY_STATUS_CHANGED = QtCore.Signal(bool, bool) # playing, forward
    SIG_NEW_MEDIA_ADDED = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.__delegate_mngr = DelegateMngr()

    def get_delegate_mngr(self):
        return self.__delegate_mngr

    def is_empty(self):
        return self.__delegate_mngr.call(self.is_empty)

    def is_playing(self):
        return self.__delegate_mngr.call(self.is_playing)

    def is_forward(self):
        return self.__delegate_mngr.call(self.is_forward)

    def set_playing(self, frame, playing, forward):
        self.__delegate_mngr.call(self.set_playing, [frame, playing, forward])

    def stop(self):
        frame = self.get_current_frame()
        forward = self.is_forward()
        self.set_playing(frame, False, forward)

    def play(self):
        frame = self.get_current_frame()
        forward = self.is_forward()
        self.set_playing(frame, True, forward)

    def play_forward(self):
        frame = self.get_current_frame()
        self.set_playing(frame, True, True)

    def play_backward(self):
        frame = self.get_current_frame()
        self.set_playing(frame, True, False)

    def toggle_play(self):
        frame = self.get_current_frame()
        playing = self.is_playing()
        forward = self.is_forward()
        self.set_playing(frame, not playing, forward)

    def toggle_play_forward(self):
        frame = self.get_current_frame()
        playing = self.is_playing()
        forward = self.is_forward()
        self.set_playing(frame, not (playing and forward), True)

    def toggle_play_backward(self):
        frame = self.get_current_frame()
        playing = self.is_playing()
        backward = not self.is_forward()
        self.set_playing(frame, not (playing and backward), False)

    def goto_frame(self, frame:int, clip_mode=False):
        self.__delegate_mngr.call(
            self.goto_frame, [frame, clip_mode])

    def step_forward(self):
        a, b = self.get_frame_range()
        frame = self.get_current_frame() + 1
        self.goto_frame(a if frame > b else frame)

    def step_backward(self):
        a, b = self.get_frame_range()
        frame = self.get_current_frame() - 1
        self.goto_frame(b if frame < a else frame)

    def get_frame_range(self):
        return self.__delegate_mngr.call(
            self.get_frame_range)

    def get_start_frame(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_start_frame, [clip_mode]
        )

    def get_end_frame(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_end_frame, [clip_mode]
        )

    def get_start_timecode(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_start_timecode, [clip_mode]
        )

    def get_start_seconds(self):
        return self.__delegate_mngr.call(
            self.get_start_seconds
        )

    def get_frame_count(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_frame_count, [clip_mode])

    def get_end_timecode(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_end_timecode, [clip_mode]
        )

    def get_total_timecode(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_total_timecode, [clip_mode]
        )

    def get_end_seconds(self):
        return self.__delegate_mngr.call(
            self.get_end_seconds
        )

    def get_current_frame(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_current_frame, [clip_mode])

    def get_current_timecode(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_current_timecode, [clip_mode]
        )

    def get_current_seconds(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_current_seconds, [clip_mode]
        )

    def get_current_source_frame(self):
        return self.__delegate_mngr.call(
            self.get_current_source_frame)

    def get_start_feet(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_start_feet, [clip_mode]
        )

    def get_current_feet(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_current_feet, [clip_mode]
        )

    def get_end_feet(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_end_feet, [clip_mode]
        )

    def get_total_feet(self, clip_mode=False):
        return self.__delegate_mngr.call(
            self.get_total_feet, [clip_mode]
        )

    def set_sequence_view(self):
        return self.__delegate_mngr.call(
            self.set_sequence_view)

    def set_stack_view(self):
        return self.__delegate_mngr.call(
            self.set_stack_view)

    def set_layout_view(self):
        return self.__delegate_mngr.call(
            self.set_layout_view)

    def set_stack_mode_replace(self):
        return self.__delegate_mngr.call(
            self.set_stack_mode_replace)

    def set_stack_mode_over(self):
        return self.__delegate_mngr.call(
            self.set_stack_mode_over)

    def set_stack_mode_add(self):
        return self.__delegate_mngr.call(
            self.set_stack_mode_add)

    def set_stack_mode_difference(self):
        return self.__delegate_mngr.call(
            self.set_stack_mode_difference)

    def set_stack_mode_inverted_difference(self):
        return self.__delegate_mngr.call(
            self.set_stack_mode_inverted_difference)

    def get_volume(self):
        return self.__delegate_mngr.call(
            self.get_volume)

    def set_volume(self, volume: int):
        return self.__delegate_mngr.call(
            self.set_volume, [volume])

    def toggle_mute(self, state: bool):
        return self.__delegate_mngr.call(
            self.toggle_mute, [state])

    def set_clip_mode(self, clip_mode: bool):
        return self.__delegate_mngr.call(
            self.set_clip_mode, [clip_mode])
