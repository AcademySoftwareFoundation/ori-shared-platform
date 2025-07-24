from dataclasses import dataclass, field
from enum import Enum


class FrameScopeMode(Enum):
    CLIP = 1
    SEQUENCE = 2


class FrameDisplayMode(Enum):
    FRAME = 1
    TIMECODE = 2
    FEET = 3


@dataclass
class SliderScope:
    scope_mode: Enum = FrameScopeMode.SEQUENCE

    def set_clip_scope(self):
        self.scope_mode = FrameScopeMode.CLIP

    def is_clip_scope(self):
        return self.scope_mode == FrameScopeMode.CLIP

    def set_sequence_scope(self):
        self.scope_mode = FrameScopeMode.SEQUENCE

    def is_sequence_scope(self):
        return self.scope_mode == FrameScopeMode.SEQUENCE

    def __getstate__(self):
        return {
            "scope": self.scope_mode
        }


@dataclass
class RangeScope:
    scope_mode: Enum = FrameScopeMode.CLIP
    display_mode: Enum = FrameDisplayMode.FRAME

    def set_clip_scope(self):
        self.scope_mode = FrameScopeMode.CLIP

    def is_clip_scope(self):
        return self.scope_mode == FrameScopeMode.CLIP

    def set_sequence_scope(self):
        self.scope_mode = FrameScopeMode.SEQUENCE

    def is_sequence_scope(self):
        return self.scope_mode == FrameScopeMode.SEQUENCE

    def set_display_mode_frame(self):
        self.display_mode = FrameDisplayMode.FRAME

    def is_display_mode_frame(self):
        return self.display_mode == FrameDisplayMode.FRAME

    def set_display_mode_timecode(self):
        self.display_mode = FrameDisplayMode.TIMECODE

    def is_display_mode_timecode(self):
        return self.display_mode == FrameDisplayMode.TIMECODE

    def set_display_mode_feet(self):
        self.display_mode = FrameDisplayMode.FEET

    def is_display_mode_feet(self):
        return self.display_mode == FrameDisplayMode.FEET

    def __getstate__(self):
        return {
            "scope": self.scope_mode,
            "display": self.display_mode
        }


@dataclass
class TimelineScope:
    slider: SliderScope = field(default_factory=SliderScope)
    range: RangeScope = field(default_factory=RangeScope)

    def __getstate__(self):
        return {
            "slider": self.slider.__getstate__(),
            "range": self.range.__getstate__()
        }


class Keys(Enum):
    ANNOT_EDITABLE_KEY = 1
    ANNOT_NON_EDITABLE_KEY = 2
    CC_KEY = 3
    MISC_KEY = 4
