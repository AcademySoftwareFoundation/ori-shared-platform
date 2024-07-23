from enum import Enum
from review_plugin_api.widgets.color_corrector._color_corrector \
    import constants as C

def FormatNumber(v):
    num_digits = 5
    try:
        if v != 0 and abs(v) < .1**num_digits:
            return '%.2e' % v
        elif (v % 1) < .1**num_digits:
            return str(int(v))
        else:
            return str(round(v, num_digits))
    except:
        return '0'


class TabType(Enum):
    CLIP = "Clip"
    FRAME = "Frame"
    REGION = "Region"

class RegionName(Enum):
    RECTANGLE = "rectangle"
    ELLIPSE = "ellipse"
    LASSO = "lasso"

class Slider(Enum):
    GAMMA = "gamma"
    WHITEPOINT = "whitepoint"
    BLACKPOINT = "blackpoint"
    FSTOP = "gain"
    FALLOFF = "falloff"
    LIFT = "lift"
    POWER = "power"
    OFFSET = "offset"
    SLOPE = "slope"
    SAT = "saturation"

class SliderAttrs:
    def __init__(self):
        self.__data = {}

    def set_value(self, index:Slider, value:dict):
        self.__data[index] = value

    def get_value(self, index:Slider):
        return self.__data.get(index)

class ColorTimer:
    def __init__(self,
                 slope=C.DEFAULT_SLOPE,
                 offset=C.DEFAULT_OFFSET,
                 power=C.DEFAULT_POWER,
                 saturation=C.DEFAULT_SAT):
        self.slope = list(slope)
        self.offset = list(offset)
        self.power = list(power)
        self.saturation = saturation
        self.mute = False
        self.is_expanded = False

    @staticmethod
    def default():
        return {
            Slider.OFFSET.value:list(C.DEFAULT_OFFSET),
            Slider.SLOPE.value:list(C.DEFAULT_SLOPE),
            Slider.POWER.value:list(C.DEFAULT_POWER),
            Slider.SAT.value:C.DEFAULT_SAT}

    def update(self, var, value):
        if hasattr(self, var):
            setattr(self, var, value)

    def update_all(self, value):
        self.offset = value[Slider.OFFSET.value]
        self.slope = value[Slider.SLOPE.value]
        self.power = value[Slider.POWER.value]
        self.saturation = value[Slider.SAT.value]

    def set_mute(self, value):
        self.mute = value

    def get(self):
        if self.mute:
            return ColorTimer.default()
        else:
            return {
                Slider.OFFSET.value: self.offset,
                Slider.SLOPE.value: self.slope,
                Slider.POWER.value: self.power,
                Slider.SAT.value:self.saturation}

    def get_actual(self):
        return {
                Slider.OFFSET.value: self.offset,
                Slider.SLOPE.value: self.slope,
                Slider.POWER.value: self.power,
                Slider.SAT.value:self.saturation}

    def reset(self):
        self.slope = list(C.DEFAULT_SLOPE)
        self.offset = list(C.DEFAULT_OFFSET)
        self.power = list(C.DEFAULT_POWER)
        self.saturation = C.DEFAULT_SAT

class Grade:
    def __init__(self,
                 gain = C.DEFAULT_FSTOP,
                 gamma = C.DEFAULT_GAMMA,
                 blackpoint = C.DEFAULT_BLACKPOINT,
                 whitepoint = C.DEFAULT_WHITEPOINT,
                 lift = C.DEFAULT_LIFT):
        self.gain = list(gain)
        self.gamma = list(gamma)
        self.blackpoint = list(blackpoint)
        self.whitepoint = list(whitepoint)
        self.lift = list(lift)
        self.mute = False
        self.is_expanded = False

    @staticmethod
    def default():
        return {
            Slider.FSTOP.value:list(C.DEFAULT_FSTOP),
            Slider.GAMMA.value:list(C.DEFAULT_GAMMA),
            Slider.BLACKPOINT.value:list(C.DEFAULT_BLACKPOINT),
            Slider.WHITEPOINT.value:list(C.DEFAULT_WHITEPOINT),
            Slider.LIFT.value:list(C.DEFAULT_LIFT)}

    def update(self, var, value):
        if hasattr(self, var):
            setattr(self, var, value)

    def update_all(self, value):
        self.gain = value[Slider.FSTOP.value]
        self.gamma = value[Slider.GAMMA.value]
        self.blackpoint = value[Slider.BLACKPOINT.value]
        self.whitepoint = value[Slider.WHITEPOINT.value]
        self.lift = value[Slider.LIFT.value]

    def set_mute(self, value):
        self.mute = value

    def get(self):
        if self.mute:
            return Grade.default()
        else:
            return {
                Slider.FSTOP.value: self.gain,
                Slider.GAMMA.value: self.gamma,
                Slider.BLACKPOINT.value: self.blackpoint,
                Slider.WHITEPOINT.value:self.whitepoint,
                Slider.LIFT.value:self.lift}

    def get_actual(self):
        return {
                Slider.FSTOP.value: self.gain,
                Slider.GAMMA.value: self.gamma,
                Slider.BLACKPOINT.value: self.blackpoint,
                Slider.WHITEPOINT.value:self.whitepoint,
                Slider.LIFT.value:self.lift}

    def reset(self):
        self.gain = list(C.DEFAULT_FSTOP)
        self.gamma = list(C.DEFAULT_GAMMA)
        self.blackpoint = list(C.DEFAULT_BLACKPOINT)
        self.whitepoint = list(C.DEFAULT_WHITEPOINT)
        self.lift = list(C.DEFAULT_LIFT)


class ColorCorrection:
    def __init__(self):
        self.color_timer = ColorTimer()
        self.grade = Grade()

class Model(object):
    def get_default_color_timer(self):
        return ColorTimer.default()

    def get_default_grade(self):
        return Grade.default()


class ClipModel(Model):
    def __init__(self):
        self.__clip_cc = ColorCorrection()

    def set_color_timer_knob(self, knob, value):
        self.__clip_cc.color_timer.update(knob, value)

    def set_color_timer(self, value):
        self.__clip_cc.color_timer.update_all(value)

    def reset_color_timer(self):
        self.__clip_cc.color_timer.reset()

    def get_color_timer(self):
        return self.__clip_cc.color_timer.get()

    def mute_all(self, mute):
        self.__clip_cc.color_timer.set_mute(mute)
        self.__clip_cc.grade.set_mute(mute)

    def mute_color_timer(self, mute):
        self.__clip_cc.color_timer.set_mute(mute)

    def is_color_timer_muted(self):
        return self.__clip_cc.color_timer.mute

    def set_grade_knob(self, knob, value):
        self.__clip_cc.grade.update(knob, value)

    def set_grade(self, value):
        self.__clip_cc.grade.update_all(value)

    def reset_grade(self):
        self.__clip_cc.grade.reset()

    def get_grade(self):
        return self.__clip_cc.grade.get()

    def mute_grade(self, mute):
        self.__clip_cc.grade.set_mute(mute)

    def is_grade_muted(self):
        return self.__clip_cc.grade.mute

    def get_all(self):
        return {**self.__clip_cc.color_timer.get(), **self.__clip_cc.grade.get()}


class FrameModel(Model):
    def __init__(self):
        self.__frame_cc = {}

    def get_frames(self):
        return self.__frame_cc.keys()

    def set_color_timer_knob(self, frame, knob, value):
        if frame not in self.__frame_cc:
            self.__frame_cc[frame] = ColorCorrection()
        self.__frame_cc[frame].color_timer.update(knob, value)

    def set_color_timer(self, frame, value):
        if frame not in self.__frame_cc:
            self.__frame_cc[frame] = ColorCorrection()
        self.__frame_cc[frame].color_timer.update_all(value)

    def get_color_timer(self, frame):
        if frame in self.__frame_cc:
            return self.__frame_cc[frame].color_timer.get()
        return ColorTimer.default()

    def get_view_color_timer(self, frame):
        if frame in self.__frame_cc:
            return self.__frame_cc[frame].color_timer.get_actual()
        return ColorTimer.default()

    def reset_color_timer(self, frame):
        if frame in self.__frame_cc:
            self.__frame_cc[frame].color_timer.reset()

    def mute_all(self, mute):
        for frame in self.__frame_cc.keys():
            self.__frame_cc[frame].color_timer.set_mute(mute)
            self.__frame_cc[frame].grade.set_mute(mute)

    def mute_color_timer(self, frame, mute):
        if frame in self.__frame_cc:
            self.__frame_cc[frame].color_timer.set_mute(mute)

    def is_color_timer_muted(self, frame):
        if frame in self.__frame_cc:
            return self.__frame_cc[frame].color_timer.mute
        return False

    def set_grade_knob(self, frame, knob, value):
        if frame not in self.__frame_cc:
            self.__frame_cc[frame] = ColorCorrection()
        self.__frame_cc[frame].grade.update(knob, value)

    def set_grade(self, frame, value):
        if frame not in self.__frame_cc:
            self.__frame_cc[frame] = ColorCorrection()
        self.__frame_cc[frame].grade.update_all(value)

    def get_grade(self, frame):
        if frame in self.__frame_cc:
            return self.__frame_cc[frame].grade.get()
        return Grade.default()

    def get_view_grade(self, frame):
        if frame in self.__frame_cc:
            return self.__frame_cc[frame].grade.get_actual()
        return Grade.default()

    def reset_grade(self, frame):
        if frame in self.__frame_cc:
            self.__frame_cc[frame].grade.reset()

    def mute_grade(self, frame, mute):
        if frame in self.__frame_cc:
            self.__frame_cc[frame].grade.set_mute(mute)

    def is_grade_muted(self, frame):
        if frame in self.__frame_cc:
            return self.__frame_cc[frame].grade.mute
        return False

    def get_all(self, frame):
        if frame in self.__frame_cc:
            return {**self.__frame_cc[frame].grade.get(), **self.__frame_cc[frame].color_timer.get()}
        return {**ColorTimer.default(), **Grade.default()}


class RegionModel(Model):
    def __init__(self):
        self.__region_cc = {}

    def get_frames(self):
        return self.__region_cc.keys()

    def set_color_timer_knob(self, frame, guid, knob, value):
        if frame not in self.__region_cc:
            self.__region_cc[frame] = {}
        if guid not in self.__region_cc[frame]:
            self.__region_cc[frame][guid] = ColorCorrection()
        self.__region_cc[frame][guid].color_timer.update(knob, value)

    def set_color_timer(self, frame, guid, value):
        if frame not in self.__region_cc:
            self.__region_cc[frame] = {}
        if guid not in self.__region_cc[frame]:
            self.__region_cc[frame][guid] = ColorCorrection()
        self.__region_cc[frame][guid].color_timer.update_all(value)

    def reset_color_timer(self, frame, guid):
        if frame in self.__region_cc:
            if guid in self.__region_cc[frame]:
                self.__region_cc[frame][guid].color_timer.reset()

    def get_color_timer(self, frame, guid):
        if frame in self.__region_cc:
            if guid in self.__region_cc[frame]:
                return self.__region_cc[frame][guid].color_timer.get()
        return ColorTimer.default()

    def mute_all(self, mute):
        for frame in self.__region_cc.keys():
            for guid in self.__region_cc[frame]:
                self.__region_cc[frame][guid].color_timer.set_mute(mute)
                self.__region_cc[frame][guid].grade.set_mute(mute)

    def mute_color_timer(self, frame, guid, mute):
        if frame in self.__region_cc:
            if guid in self.__region_cc[frame]:
                self.__region_cc[frame][guid].color_timer.set_mute(mute)

    def is_color_timer_muted(self, frame, guid):
        if frame in self.__region_cc:
            if guid in self.__region_cc[frame]:
                return self.__region_cc[frame][guid].color_timer.mute
        return False

    def set_grade_knob(self, frame, guid, knob, value):
        if frame not in self.__region_cc:
            self.__region_cc[frame] = {}
        if guid not in self.__region_cc[frame]:
            self.__region_cc[frame][guid] = ColorCorrection()
        self.__region_cc[frame][guid].grade.update(knob, value)

    def set_grade(self, frame, guid, value):
        if frame not in self.__region_cc:
            self.__region_cc[frame] = {}
        if guid not in self.__region_cc[frame]:
            self.__region_cc[frame][guid] = ColorCorrection()
        self.__region_cc[frame][guid].grade.update_all(value)

    def reset_grade(self, frame, guid):
        if frame in self.__region_cc:
            if guid in self.__region_cc[frame]:
                self.__region_cc[frame][guid].grade.reset()

    def get_grade(self, frame, guid):
        if frame in self.__region_cc:
            if guid in self.__region_cc[frame]:
                return self.__region_cc[frame][guid].grade.get()
        return Grade.default()

    def get_all(self, frame, guid):
        if frame in self.__region_cc:
            if guid in self.__region_cc[frame]:
                return {**self.__region_cc[frame][guid].grade.get(), **self.__region_cc[frame][guid].color_timer.get()}
        return {**ColorTimer.default(), **Grade.default()}

    def mute_grade(self, frame, guid, mute):
        if frame in self.__region_cc:
            if guid in self.__region_cc[frame]:
                self.__region_cc[frame][guid].grade.set_mute(mute)

    def is_grade_muted(self, frame, guid):
        if frame in self.__region_cc:
            if guid in self.__region_cc[frame]:
                return self.__region_cc[frame][guid].grade.mute
        return False
