from PySide2 import QtWidgets, QtGui, QtCore
from review_plugin_api.widgets.color_corrector.widgets.striped_frame \
    import StripedFrame
from review_plugin_api.widgets.color_corrector.widgets \
    import mini_label_button, input_line_edit
from review_plugin_api.widgets.color_corrector._color_corrector.view.color_knob \
    import ColorKnob
from review_plugin_api.widgets.color_corrector._color_corrector.model \
    import Slider, SliderAttrs
from review_plugin_api.widgets.color_corrector._color_corrector \
    import constants as C
import review_plugin_api.widgets.color_corrector.\
    _color_corrector.view.resources.resources


class ColorCorrectionAndGrading(QtWidgets.QScrollArea):
    # ColorTimer
    SIG_OFFSET_CHANGED = QtCore.Signal(list)
    SIG_SLOPE_CHANGED = QtCore.Signal(list)
    SIG_POWER_CHANGED = QtCore.Signal(list)
    SIG_SAT_CHANGED = QtCore.Signal(float)
    SIG_MUTE_COLOR_TIMER = QtCore.Signal()
    SIG_RESET_COLOR_TIMER = QtCore.Signal()

    # Grade
    SIG_FSTOP_CHANGED = QtCore.Signal(list)
    SIG_GAMMA_CHANGED = QtCore.Signal(list)
    SIG_BLACKPOINT_CHANGED = QtCore.Signal(list)
    SIG_WHITEPOINT_CHANGED = QtCore.Signal(list)
    SIG_LIFT_CHANGED = QtCore.Signal(list)
    SIG_MUTE_GRADE = QtCore.Signal()
    SIG_RESET_GRADE = QtCore.Signal()

    def __init__(self, slider_attrs:SliderAttrs):
        super().__init__()
        self.__is_mute = False
        self.setWidgetResizable(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.__color_timer = ColorTimer(slider_attrs)
        self.__grade =Grade(slider_attrs)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.__color_timer)
        layout.addWidget(self.__grade)

        spacer = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(spacer)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setWidget(widget)

        self.__color_timer.SIG_OFFSET_CHANGED.connect(self.SIG_OFFSET_CHANGED)
        self.__color_timer.SIG_POWER_CHANGED.connect(self.SIG_POWER_CHANGED)
        self.__color_timer.SIG_SLOPE_CHANGED.connect(self.SIG_SLOPE_CHANGED)
        self.__color_timer.SIG_SAT_CHANGED.connect(self.SIG_SAT_CHANGED)

        self.__color_timer.SIG_MUTE_COLOR_TIMER.connect(self.SIG_MUTE_COLOR_TIMER)
        self.__color_timer.SIG_RESET_COLOR_TIMER.connect(self.SIG_RESET_COLOR_TIMER)

        self.__grade.SIG_FSTOP_CHANGED.connect(self.SIG_FSTOP_CHANGED)
        self.__grade.SIG_GAMMA_CHANGED.connect(self.SIG_GAMMA_CHANGED)
        self.__grade.SIG_BLACKPOINT_CHANGED.connect(self.SIG_BLACKPOINT_CHANGED)
        self.__grade.SIG_WHITEPOINT_CHANGED.connect(self.SIG_WHITEPOINT_CHANGED)
        self.__grade.SIG_LIFT_CHANGED.connect(self.SIG_LIFT_CHANGED)

        self.__grade.SIG_MUTE_GRADE.connect(self.SIG_MUTE_GRADE)
        self.__grade.SIG_RESET_GRADE.connect(self.SIG_RESET_GRADE)

    @property
    def color_timer(self):
        return self.__color_timer

    @property
    def grade(self):
        return self.__grade

    def mute_color_timer(self, mute):
        self.__color_timer.set_mute(mute)

    def mute_grade(self, mute):
        self.__grade.set_mute(mute)

    def mute_all(self, mute):
        self.__is_mute = mute
        self.mute_color_timer(mute)
        self.mute_grade(mute)

    def is_mute(self):
        return self.__is_mute


class RegionTab(ColorCorrectionAndGrading):

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


class Header(QtWidgets.QWidget):
    SIG_MUTE_CLICKED = QtCore.Signal()
    SIG_RESET_CLICKED = QtCore.Signal()
    SIG_TOGGLE_VISIBILITY = QtCore.Signal(bool)

    def __init__(self, title:str, expand=False):
        super().__init__()

        self.__is_expanded = expand
        self.__forward_icon = ':forward_arrow.png'
        self.__down_icon = ':down_arrow.png'

        self.__expand_button = QtWidgets.QToolButton()
        self.__expand_button.setToolTip("Expand/Collapse")
        self.__expand_button.setIconSize(QtCore.QSize(20, 20))
        self.__expand_button.clicked.connect(self.__toggle_expand)
        self.__expand_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__expand_button.setIcon(
            QtGui.QIcon(QtGui.QPixmap(self.__forward_icon)))
        if self.__is_expanded:
            self.__expand_button.setIcon(
                QtGui.QIcon(QtGui.QPixmap(self.__down_icon)))

        strip_1 = StripedFrame()
        strip_1.setFixedHeight(2)
        strip_1.setFixedWidth(10)
        self.__mute_button = mini_label_button.MiniLabelButton("mute", self)
        reset_button = mini_label_button.MiniLabelButton("reset", self)
        strip_2 = StripedFrame()
        strip_2.setFixedHeight(2)

        self.__title_label = QtWidgets.QLabel(title)
        italicsFont = QtGui.QFont(self.font())
        italicsFont.setItalic(True)
        self.__title_label.setFont(italicsFont)
        mini_label_button.SetCompactWidgetWidth(self.__title_label)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.__expand_button)
        h_layout.addWidget(strip_1, 5)
        h_layout.addWidget(self.__mute_button, 0)
        h_layout.addWidget(reset_button, 0)
        h_layout.addWidget(strip_2, 5)
        h_layout.addWidget(self.__title_label, 0)
        self.setLayout(h_layout)

        self.__mute_button.SIG_CLICKED.connect(self.SIG_MUTE_CLICKED)
        reset_button.SIG_CLICKED.connect(self.SIG_RESET_CLICKED)

    def get_mute_btn(self):
        return self.__mute_button

    def update_icon_state(self, active):
        self.__forward_icon = ':forward_arrow_active.png' if active else ':forward_arrow.png'
        self.__down_icon = ':down_arrow_active.png' if active else ':down_arrow.png'
        icon = self.__down_icon if self.__is_expanded else self.__forward_icon
        self.__expand_button.setIcon(QtGui.QIcon(QtGui.QPixmap(icon)))
        if active:
            self.__title_label.setStyleSheet("QLabel {color: rgb(192, 158, 64);}")
        else:
            self.__title_label.setStyleSheet("QLabel {color: rgb(255, 255, 255);}")

    def __toggle_expand(self):
        self.__is_expanded = not self.__is_expanded
        icon = self.__down_icon if self.__is_expanded else self.__forward_icon
        self.__expand_button.setIcon(QtGui.QIcon(QtGui.QPixmap(icon)))
        self.SIG_TOGGLE_VISIBILITY.emit(self.__is_expanded)


class ColorTimer(QtWidgets.QWidget):
    LABEL_WIDTH = 65

    SIG_OFFSET_CHANGED = QtCore.Signal(list)
    SIG_SLOPE_CHANGED = QtCore.Signal(list)
    SIG_POWER_CHANGED = QtCore.Signal(list)
    SIG_SAT_CHANGED = QtCore.Signal(float)

    SIG_MUTE_COLOR_TIMER = QtCore.Signal()
    SIG_RESET_COLOR_TIMER = QtCore.Signal()

    def __init__(self, slider_attrs:SliderAttrs):
        super().__init__()
        self.__is_active = False

        visible = False
        self.__header = Header("ColorTimer", expand=visible)
        self.__header.SIG_TOGGLE_VISIBILITY.connect(self.__toggle_visibilty)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.__header)

        self.__offset = ColorKnob(
            Slider.OFFSET.value, slider_attrs.get_value(Slider.OFFSET), width=self.LABEL_WIDTH)
        self.__slope = ColorKnob(
            Slider.SLOPE.value, slider_attrs.get_value(Slider.SLOPE), width=self.LABEL_WIDTH)
        self.__power = ColorKnob(
            Slider.POWER.value, slider_attrs.get_value(Slider.POWER), width=self.LABEL_WIDTH)
        self.__sat = ColorKnob(
            Slider.SAT.value, slider_attrs.get_value(Slider.SAT), is_color=False, width=self.LABEL_WIDTH)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.__header)
        layout.addWidget(self.__offset)
        layout.addWidget(self.__slope)
        layout.addWidget(self.__power)
        layout.addWidget(self.__sat)
        self.setLayout(layout)

        self.__offset.setVisible(visible)
        self.__slope.setVisible(visible)
        self.__power.setVisible(visible)
        self.__sat.setVisible(visible)

        self.__offset.SIG_COLOR_CHANGED.connect(self.SIG_OFFSET_CHANGED)
        self.__slope.SIG_COLOR_CHANGED.connect(self.SIG_SLOPE_CHANGED)
        self.__power.SIG_COLOR_CHANGED.connect(self.SIG_POWER_CHANGED)
        self.__sat.SIG_VALUE_CHANGED.connect(self.SIG_SAT_CHANGED)

        self.__offset.SIG_COLOR_CHANGED.connect(self.set_offset)
        self.__slope.SIG_COLOR_CHANGED.connect(self.set_slope)
        self.__power.SIG_COLOR_CHANGED.connect(self.set_power)
        self.__sat.SIG_VALUE_CHANGED.connect(self.set_sat)

        self.__header.SIG_MUTE_CLICKED.connect(self.SIG_MUTE_COLOR_TIMER)
        self.__header.SIG_RESET_CLICKED.connect(self.SIG_RESET_COLOR_TIMER)

    def set_mute(self, mute):
        self.__header.get_mute_btn().setChecked(mute)
        self.__offset.setEnabled(not mute)
        self.__slope.setEnabled(not mute)
        self.__power.setEnabled(not mute)
        self.__sat.setEnabled(not mute)

    def __toggle_visibilty(self, visible):
        self.__offset.setVisible(visible)
        self.__slope.setVisible(visible)
        self.__power.setVisible(visible)
        self.__sat.setVisible(visible)

    def set_offset(self, offset):
        self.__offset.set_color(offset, is_default=list(C.DEFAULT_OFFSET)==offset)
        self.__check_active_state()

    def set_slope(self, slope):
        self.__slope.set_color(slope, is_default=list(C.DEFAULT_SLOPE)==slope)
        self.__check_active_state()

    def set_power(self, power):
        self.__power.set_color(power, is_default=list(C.DEFAULT_POWER)==power)
        self.__check_active_state()

    def set_sat(self, sat):
        self.__sat.set_value(sat, is_default=C.DEFAULT_SAT==sat)
        self.__check_active_state()

    def __check_active_state(self):
        current_active_state = self.__is_active
        self.__is_active = True
        if self.__offset.is_default() and \
            self.__slope.is_default() and \
                self.__power.is_default() and self.__sat.is_default():
            self.__is_active = False
        if current_active_state != self.__is_active:
            self.__header.update_icon_state(self.__is_active)

    def get_offset(self):
        return self.__offset.value

    def get_slope(self):
        return self.__slope.value

    def get_power(self):
        return self.__power.value

    def get_sat(self):
        return self.__sat.value

    def get_all(self):
        return {Slider.OFFSET.value: self.get_offset(),
                Slider.SLOPE.value: self.get_slope(),
                Slider.POWER.value: self.get_power(),
                Slider.SAT.value: self.get_sat()}

    def set_all(self, value):
        self.set_offset(value[Slider.OFFSET.value])
        self.set_slope(value[Slider.SLOPE.value])
        self.set_power(value[Slider.POWER.value])
        self.set_sat(value[Slider.SAT.value])


class Grade(QtWidgets.QWidget):
    LABEL_WIDTH = 65

    SIG_FSTOP_CHANGED = QtCore.Signal(list)
    SIG_GAMMA_CHANGED = QtCore.Signal(list)
    SIG_BLACKPOINT_CHANGED = QtCore.Signal(list)
    SIG_WHITEPOINT_CHANGED = QtCore.Signal(list)
    SIG_LIFT_CHANGED = QtCore.Signal(list)

    SIG_MUTE_GRADE = QtCore.Signal()
    SIG_RESET_GRADE = QtCore.Signal()

    def __init__(self, slider_attrs:SliderAttrs):
        super().__init__()
        self.__is_active = False

        visible = False
        self.__header = Header("Grade", expand=visible)
        self.__header.SIG_TOGGLE_VISIBILITY.connect(self.__toggle_visibilty)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.__header)

        self.__fstop = ColorKnob(
            Slider.FSTOP.value, slider_attrs.get_value(Slider.FSTOP), width=self.LABEL_WIDTH)
        self.__gamma = ColorKnob(
            Slider.GAMMA.value, slider_attrs.get_value(Slider.GAMMA), width=self.LABEL_WIDTH)
        self.__blackpoint = ColorKnob(
            Slider.BLACKPOINT.value, slider_attrs.get_value(Slider.BLACKPOINT), width=self.LABEL_WIDTH)
        self.__whitepoint = ColorKnob(
            Slider.WHITEPOINT.value, slider_attrs.get_value(Slider.WHITEPOINT), width=self.LABEL_WIDTH)
        self.__lift = ColorKnob(
            Slider.LIFT.value, slider_attrs.get_value(Slider.LIFT), width=self.LABEL_WIDTH)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.__header)
        layout.addWidget(self.__fstop)
        layout.addWidget(self.__gamma)
        layout.addWidget(self.__blackpoint)
        layout.addWidget(self.__whitepoint)
        layout.addWidget(self.__lift)
        self.setLayout(layout)

        self.__fstop.setVisible(visible)
        self.__gamma.setVisible(visible)
        self.__blackpoint.setVisible(visible)
        self.__whitepoint.setVisible(visible)
        self.__lift.setVisible(visible)

        self.__fstop.SIG_COLOR_CHANGED.connect(self.SIG_FSTOP_CHANGED)
        self.__gamma.SIG_COLOR_CHANGED.connect(self.SIG_GAMMA_CHANGED)
        self.__blackpoint.SIG_COLOR_CHANGED.connect(self.SIG_BLACKPOINT_CHANGED)
        self.__whitepoint.SIG_COLOR_CHANGED.connect(self.SIG_WHITEPOINT_CHANGED)
        self.__lift.SIG_COLOR_CHANGED.connect(self.SIG_LIFT_CHANGED)

        self.__fstop.SIG_COLOR_CHANGED.connect(self.set_fstop)
        self.__gamma.SIG_COLOR_CHANGED.connect(self.set_gamma)
        self.__blackpoint.SIG_COLOR_CHANGED.connect(self.set_blackpoint)
        self.__whitepoint.SIG_COLOR_CHANGED.connect(self.set_whitepoint)
        self.__lift.SIG_COLOR_CHANGED.connect(self.set_lift)

        self.__header.SIG_MUTE_CLICKED.connect(self.SIG_MUTE_GRADE)
        self.__header.SIG_RESET_CLICKED.connect(self.SIG_RESET_GRADE)

    def set_mute(self, mute):
        self.__header.get_mute_btn().setChecked(mute)
        self.__fstop.setEnabled(not mute)
        self.__gamma.setEnabled(not mute)
        self.__blackpoint.setEnabled(not mute)
        self.__whitepoint.setEnabled(not mute)
        self.__lift.setEnabled(not mute)

    def __toggle_visibilty(self, visible):
        self.__fstop.setVisible(visible)
        self.__gamma.setVisible(visible)
        self.__blackpoint.setVisible(visible)
        self.__whitepoint.setVisible(visible)
        self.__lift.setVisible(visible)

    def set_fstop(self, fstop):
        self.__fstop.set_color(fstop, is_default=list(C.DEFAULT_FSTOP)==fstop)
        self.__check_active_state()

    def set_gamma(self, gamma):
        self.__gamma.set_color(gamma, is_default=list(C.DEFAULT_GAMMA)==gamma)
        self.__check_active_state()

    def set_blackpoint(self, blackpoint):
        self.__blackpoint.set_color(blackpoint, is_default=list(C.DEFAULT_BLACKPOINT)==blackpoint)
        self.__check_active_state()

    def set_whitepoint(self, whitepoint):
        self.__whitepoint.set_color(whitepoint, is_default=list(C.DEFAULT_WHITEPOINT)==whitepoint)
        self.__check_active_state()

    def set_lift(self, lift):
        self.__lift.set_color(lift, is_default=list(C.DEFAULT_LIFT)==lift)
        self.__check_active_state()

    def __check_active_state(self):
        current_active_state = self.__is_active
        self.__is_active = True
        if self.__fstop.is_default() and \
            self.__gamma.is_default() and \
                self.__blackpoint.is_default() and self.__whitepoint.is_default() and self.__lift.is_default():
            self.__is_active = False
        if current_active_state != self.__is_active:
            self.__header.update_icon_state(self.__is_active)

    def get_fstop(self):
        return self.__fstop.value

    def get_gamma(self):
        return self.__gamma.value

    def get_blackpoint(self):
        return self.__blackpoint.value

    def get_whitepoint(self):
        return self.__whitepoint.value

    def get_lift(self):
        return self.__lift.value

    def get_all(self):
        return {Slider.FSTOP.value: self.get_fstop(),
                Slider.GAMMA.value: self.get_gamma(),
                Slider.BLACKPOINT.value: self.get_blackpoint(),
                Slider.WHITEPOINT.value: self.get_whitepoint(),
                Slider.LIFT.value: self.get_lift()}

    def set_all(self, value):
        self.set_fstop(value[Slider.FSTOP.value])
        self.set_gamma(value[Slider.GAMMA.value])
        self.set_blackpoint(value[Slider.BLACKPOINT.value])
        self.set_whitepoint(value[Slider.WHITEPOINT.value])
        self.set_lift(value[Slider.LIFT.value])
