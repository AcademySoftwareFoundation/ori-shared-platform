import functools
from PySide2 import QtWidgets, QtGui, QtCore
from review_plugin_api.widgets.color_corrector._color_corrector.view.color_knob \
    import ColorKnob
from review_plugin_api.widgets.color_corrector._color_corrector.view.group_node \
    import SpColorTimer, Grade
from review_plugin_api.widgets.color_corrector._color_corrector.model import \
    SliderName, SliderAttrs, RegionName, ColorCorrectType


class GroupLabel(QtWidgets.QLabel):
    def __init__(self, text:str):
        super().__init__()
        self.setText(text.capitalize())
        self.setForegroundRole(QtGui.QPalette.Light)
        self.setToolTip('Click to Reset')
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def enterEvent(self, event):
        self.setForegroundRole(QtGui.QPalette.HighlightedText)

    def leaveEvent(self, event):
        self.setForegroundRole(QtGui.QPalette.Light)


class ColorCorrectionAndGrading(QtWidgets.QScrollArea):
    # ColorTimer
    SIG_OFFSET_CHANGED = QtCore.Signal(list)
    SIG_SLOPE_CHANGED = QtCore.Signal(list)
    SIG_POWER_CHANGED = QtCore.Signal(list)
    SIG_SAT_CHANGED = QtCore.Signal(float)
    SIG_MUTE_COLOR_TIMER = QtCore.Signal(bool)
    SIG_RESET_COLOR_TIMER = QtCore.Signal()

    # Grade
    SIG_FSTOP_CHANGED = QtCore.Signal(list)
    SIG_GAMMA_CHANGED = QtCore.Signal(list)
    SIG_BLACKPOINT_CHANGED = QtCore.Signal(list)
    SIG_WHITEPOINT_CHANGED = QtCore.Signal(list)
    SIG_LIFT_CHANGED = QtCore.Signal(list)
    SIG_MUTE_GRADE = QtCore.Signal(bool)
    SIG_RESET_GRADE = QtCore.Signal()

    def __init__(self, slider_attrs:SliderAttrs):
        super().__init__()
        self.setWidgetResizable(True)

        self.__sp_color_timer = SpColorTimer(ColorCorrectType.CLIP, slider_attrs)
        self.__grade =Grade(ColorCorrectType.CLIP, slider_attrs)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.__sp_color_timer)
        layout.addWidget(self.__grade)

        spacer = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(spacer)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setWidget(widget)

        self.__sp_color_timer.SIG_OFFSET_CHANGED.connect(self.SIG_OFFSET_CHANGED)
        self.__sp_color_timer.SIG_POWER_CHANGED.connect(self.SIG_POWER_CHANGED)
        self.__sp_color_timer.SIG_SLOPE_CHANGED.connect(self.SIG_SLOPE_CHANGED)
        self.__sp_color_timer.SIG_SAT_CHANGED.connect(self.SIG_SAT_CHANGED)

        self.__sp_color_timer.SIG_MUTE_COLOR_TIMER.connect(self.SIG_MUTE_COLOR_TIMER)
        self.__sp_color_timer.SIG_RESET_COLOR_TIMER.connect(self.SIG_RESET_COLOR_TIMER)

        self.__grade.SIG_FSTOP_CHANGED.connect(self.SIG_FSTOP_CHANGED)
        self.__grade.SIG_GAMMA_CHANGED.connect(self.SIG_GAMMA_CHANGED)
        self.__grade.SIG_BLACKPOINT_CHANGED.connect(self.SIG_BLACKPOINT_CHANGED)
        self.__grade.SIG_WHITEPOINT_CHANGED.connect(self.SIG_WHITEPOINT_CHANGED)
        self.__grade.SIG_LIFT_CHANGED.connect(self.SIG_LIFT_CHANGED)

        self.__grade.SIG_MUTE_GRADE.connect(self.SIG_MUTE_GRADE)
        self.__grade.SIG_RESET_GRADE.connect(self.SIG_RESET_GRADE)

    @property
    def color_timer(self):
        return self.__sp_color_timer

    @property
    def grade(self):
        return self.__grade

    def mute(self, mute):
        if mute:
            self.__sp_color_timer.mute()
            self.__grade.mute()
        else:
            self.__sp_color_timer.unmute()
            self.__grade.unmute()


class RegionTab(ColorCorrectionAndGrading):
    SIG_LASSO_BORDER_CHECKBOX_CHECKED = QtCore.Signal(bool)

    def __init__(self, slider_attrs:SliderAttrs, name=None):
        super().__init__(slider_attrs)
        self.__name = name
        self.__cc_guid = None

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_cc_guid(self):
        return self.__cc_guid

    def set_cc_guid(self, guid):
        self.__cc_guid = guid

# class RegionTab(QtWidgets.QScrollArea):
#     SIG_REL_MONITOR_GAMMA_CHANGED = QtCore.Signal(float)
#     SIG_REL_MONITOR_BLACKPOINT_CHANGED = QtCore.Signal(float)
#     SIG_REL_MONITOR_WHITEPOINT_CHANGED = QtCore.Signal(float)
#     SIG_REL_MONITOR_FSTOP_CHANGED = QtCore.Signal(float)

#     SIG_OFFSET_RGB_CHANGED = QtCore.Signal(float)
#     SIG_OFFSET_R_CHANGED = QtCore.Signal(float)
#     SIG_OFFSET_G_CHANGED = QtCore.Signal(float)
#     SIG_OFFSET_B_CHANGED = QtCore.Signal(float)
#     SIG_SLOPE_RGB_CHANGED = QtCore.Signal(float)
#     SIG_SLOPE_R_CHANGED = QtCore.Signal(float)
#     SIG_SLOPE_G_CHANGED = QtCore.Signal(float)
#     SIG_SLOPE_B_CHANGED = QtCore.Signal(float)
#     SIG_POWER_RGB_CHANGED = QtCore.Signal(float)
#     SIG_POWER_R_CHANGED = QtCore.Signal(float)
#     SIG_POWER_G_CHANGED = QtCore.Signal(float)
#     SIG_POWER_B_CHANGED = QtCore.Signal(float)
#     SIG_SAT_RGB_CHANGED = QtCore.Signal(float)

#     SIG_MUTE_COLOR_TIMER = QtCore.Signal(bool)

#     def __init__(self, slider_attr_groups:SliderAttrGroups):
#         super().__init__()
#         self.__name = None
#         self.__cc_guid = None
#         self.setWidgetResizable(True)
#         self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

#         self.__region = Region(slider_attr_groups.get_value(SliderGroup.REGION))
#         self.__relative_monitor = Monitor(
#             f"Relative {ColorCorrectType.REGION.value} Monitor",
#             slider_attr_groups.get_value(SliderGroup.REL_MONITOR))
#         self.__sp_color_timer = SpColorTimer(ColorCorrectType.REGION, slider_attr_groups)

#         layout = QtWidgets.QVBoxLayout()
#         layout.addWidget(self.__region)
#         layout.addWidget(self.__relative_monitor)
#         layout.addWidget(self.__sp_color_timer)

#         widget = QtWidgets.QWidget()
#         widget.setLayout(layout)
#         self.setWidget(widget)

#         self.__relative_monitor.SIG_GAMMA_CHANGED.connect(self.SIG_REL_MONITOR_GAMMA_CHANGED)
#         self.__relative_monitor.SIG_BLACKPOINT_CHANGED.connect(self.SIG_REL_MONITOR_BLACKPOINT_CHANGED)
#         self.__relative_monitor.SIG_WHITEPOINT_CHANGED.connect(self.SIG_REL_MONITOR_WHITEPOINT_CHANGED)
#         self.__relative_monitor.SIG_FSTOP_CHANGED.connect(self.SIG_REL_MONITOR_FSTOP_CHANGED)

#         self.__sp_color_timer.SIG_OFFSET_RGB_CHANGED.connect(self.SIG_OFFSET_RGB_CHANGED)
#         self.__sp_color_timer.SIG_OFFSET_R_CHANGED.connect(self.SIG_OFFSET_R_CHANGED)
#         self.__sp_color_timer.SIG_OFFSET_G_CHANGED.connect(self.SIG_OFFSET_G_CHANGED)
#         self.__sp_color_timer.SIG_OFFSET_B_CHANGED.connect(self.SIG_OFFSET_B_CHANGED)
#         self.__sp_color_timer.SIG_POWER_RGB_CHANGED.connect(self.SIG_POWER_RGB_CHANGED)
#         self.__sp_color_timer.SIG_POWER_R_CHANGED.connect(self.SIG_POWER_R_CHANGED)
#         self.__sp_color_timer.SIG_POWER_G_CHANGED.connect(self.SIG_POWER_G_CHANGED)
#         self.__sp_color_timer.SIG_POWER_B_CHANGED.connect(self.SIG_POWER_B_CHANGED)
#         self.__sp_color_timer.SIG_SLOPE_RGB_CHANGED.connect(self.SIG_SLOPE_RGB_CHANGED)
#         self.__sp_color_timer.SIG_SLOPE_R_CHANGED.connect(self.SIG_SLOPE_R_CHANGED)
#         self.__sp_color_timer.SIG_SLOPE_G_CHANGED.connect(self.SIG_SLOPE_G_CHANGED)
#         self.__sp_color_timer.SIG_SLOPE_B_CHANGED.connect(self.SIG_SLOPE_B_CHANGED)
#         self.__sp_color_timer.SIG_SAT_RGB_CHANGED.connect(self.SIG_SAT_RGB_CHANGED)

#         self.__sp_color_timer.SIG_MUTE_COLOR_TIMER.connect(self.SIG_MUTE_COLOR_TIMER)

#     @property
#     def region(self):
#         return self.__region

#     @property
#     def relative_monitor(self):
#         return self.__relative_monitor

#     @property
#     def color_timer(self):
#         return self.__sp_color_timer

#     @property
#     def name(self):
#         return self.__name

#     def set_name(self, name):
#         self.__name = name

#     def mute(self, mute):
#         if not mute:
#             self.__relative_monitor.unmute()
#             self.__sp_color_timer.unmute()
#             return
#         self.__relative_monitor.mute()
#         self.__sp_color_timer.mute()

#     def set_cc_guid(self, guid):
#         self.__cc_guid = guid

#     def get_cc_guid(self):
#         return self.__cc_guid

#     def set_region(self, guid, falloff, cc):
#         self.set_cc_guid(guid)
#         self.__region.set_falloff_value(falloff)
#         self.__sp_color_timer.set_slider_values(cc)