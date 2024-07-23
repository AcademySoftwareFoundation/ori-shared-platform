from PySide2 import QtWidgets, QtGui, QtCore
from review_plugin_api.widgets.color_corrector._color_corrector.model \
    import SliderName, SliderAttrs, ColorCorrectType
from review_plugin_api.widgets.color_corrector.widgets.striped_frame \
    import StripedFrame
from review_plugin_api.widgets.color_corrector.widgets import mini_label_button, input_line_edit
from review_plugin_api.widgets.color_corrector._color_corrector.view.color_knob \
    import ColorKnob
import review_plugin_api.widgets.color_corrector.\
    _color_corrector.view.resources.resources


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


class SpColorTimer(QtWidgets.QWidget):
    LABEL_WIDTH = 65

    SIG_OFFSET_CHANGED = QtCore.Signal(list)
    SIG_SLOPE_CHANGED = QtCore.Signal(list)
    SIG_POWER_CHANGED = QtCore.Signal(list)
    SIG_SAT_CHANGED = QtCore.Signal(float)

    SIG_MUTE_COLOR_TIMER = QtCore.Signal(bool)
    SIG_RESET_COLOR_TIMER = QtCore.Signal()

    def __init__(self, color_correct_type:ColorCorrectType, slider_attrs:SliderAttrs):
        super().__init__()
        self.__is_muted = False
        self.__is_active = False

        visible = False
        self.__header = Header("ColorTimer", expand=visible)
        self.__header.SIG_TOGGLE_VISIBILITY.connect(self.__toggle_visibilty)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.__header)

        self.__offset = ColorKnob(
            SliderName.OFFSET.value, slider_attrs.get_value(SliderName.OFFSET), width=self.LABEL_WIDTH)
        self.__slope = ColorKnob(
            SliderName.SLOPE.value, slider_attrs.get_value(SliderName.SLOPE), width=self.LABEL_WIDTH)
        self.__power = ColorKnob(
            SliderName.POWER.value, slider_attrs.get_value(SliderName.POWER), width=self.LABEL_WIDTH)
        self.__sat = ColorKnob(
            SliderName.SAT.value, slider_attrs.get_value(SliderName.SAT), is_color=False, width=self.LABEL_WIDTH)

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

        self.__header.SIG_MUTE_CLICKED.connect(self.__toggle_mute)
        self.__header.SIG_RESET_CLICKED.connect(self.SIG_RESET_COLOR_TIMER)

    def is_muted(self):
        return self.__is_muted

    def mute(self):
        if self.__is_muted: return
        self.__toggle_mute()

    def unmute(self):
        if not self.__is_muted: return
        self.__toggle_mute()

    def __toggle_mute(self):
        self.__is_muted = not(self.__is_muted)
        self.__header.get_mute_btn().setChecked(self.__is_muted)
        self.__offset.setEnabled(not self.__is_muted)
        self.__slope.setEnabled(not self.__is_muted)
        self.__power.setEnabled(not self.__is_muted)
        self.__sat.setEnabled(not self.__is_muted)
        self.SIG_MUTE_COLOR_TIMER.emit(self.__is_muted)

    def __toggle_visibilty(self, visible):
        self.__offset.setVisible(visible)
        self.__slope.setVisible(visible)
        self.__power.setVisible(visible)
        self.__sat.setVisible(visible)

    def set_offset(self, offset, is_default=False):
        self.__offset.set_color(offset, is_default=is_default)
        self.__check_active_state()

    def set_slope(self, slope, is_default=False):
        self.__slope.set_color(slope, is_default=is_default)
        self.__check_active_state()

    def set_power(self, power, is_default=False):
        self.__power.set_color(power, is_default=is_default)
        self.__check_active_state()

    def set_sat(self, sat, is_default=False):
        self.__sat.set_value(sat, is_default=is_default)
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


class Grade(QtWidgets.QWidget):
    LABEL_WIDTH = 65

    SIG_FSTOP_CHANGED = QtCore.Signal(list)
    SIG_GAMMA_CHANGED = QtCore.Signal(list)
    SIG_BLACKPOINT_CHANGED = QtCore.Signal(list)
    SIG_WHITEPOINT_CHANGED = QtCore.Signal(list)
    SIG_LIFT_CHANGED = QtCore.Signal(list)

    SIG_MUTE_GRADE = QtCore.Signal(bool)
    SIG_RESET_GRADE = QtCore.Signal()

    def __init__(self, color_correct_type:ColorCorrectType, slider_attrs:SliderAttrs):
        super().__init__()
        self.__is_muted = False
        self.__is_active = False

        visible = False
        self.__header = Header("Grade", expand=visible)
        self.__header.SIG_TOGGLE_VISIBILITY.connect(self.__toggle_visibilty)
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.__header)

        self.__fstop = ColorKnob(
            SliderName.FSTOP.value, slider_attrs.get_value(SliderName.FSTOP), width=self.LABEL_WIDTH)
        self.__gamma = ColorKnob(
            SliderName.GAMMA.value, slider_attrs.get_value(SliderName.GAMMA), width=self.LABEL_WIDTH)
        self.__blackpoint = ColorKnob(
            SliderName.BLACKPOINT.value, slider_attrs.get_value(SliderName.BLACKPOINT), width=self.LABEL_WIDTH)
        self.__whitepoint = ColorKnob(
            SliderName.WHITEPOINT.value, slider_attrs.get_value(SliderName.WHITEPOINT), is_color=False, width=self.LABEL_WIDTH)
        self.__lift = ColorKnob(
            SliderName.LIFT.value, slider_attrs.get_value(SliderName.LIFT), is_color=False, width=self.LABEL_WIDTH)

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

        self.__header.SIG_MUTE_CLICKED.connect(self.__toggle_mute)
        self.__header.SIG_RESET_CLICKED.connect(self.SIG_RESET_GRADE)

    def is_muted(self):
        return self.__is_muted

    def mute(self):
        if self.__is_muted: return
        self.__toggle_mute()

    def unmute(self):
        if not self.__is_muted: return
        self.__toggle_mute()

    def __toggle_mute(self):
        self.__is_muted = not(self.__is_muted)
        self.__header.get_mute_btn().setChecked(self.__is_muted)
        self.__fstop.setEnabled(not self.__is_muted)
        self.__gamma.setEnabled(not self.__is_muted)
        self.__blackpoint.setEnabled(not self.__is_muted)
        self.__whitepoint.setEnabled(not self.__is_muted)
        self.__list.setEnabled(not self.__is_muted)
        self.SIG_MUTE_GRADE.emit(self.__is_muted)

    def __toggle_visibilty(self, visible):
        self.__fstop.setVisible(visible)
        self.__gamma.setVisible(visible)
        self.__blackpoint.setVisible(visible)
        self.__whitepoint.setVisible(visible)
        self.__lift.setVisible(visible)

    def set_fstop(self, fstop, is_default=False):
        self.__fstop.set_color(fstop, is_default=is_default)
        self.__check_active_state()

    def set_gamma(self, gamma, is_default=False):
        self.__gamma.set_color(gamma, is_default=is_default)
        self.__check_active_state()

    def set_blackpoint(self, blackpoint, is_default=False):
        self.__blackpoint.set_color(blackpoint, is_default=is_default)
        self.__check_active_state()

    def set_whitepoint(self, whitepoint, is_default=False):
        self.__whitepoint.set_color(whitepoint, is_default=is_default)
        self.__check_active_state()

    def set_lift(self, lift, is_default=False):
        self.__lift.set_color(lift, is_default=is_default)
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

    def get_fstop_value(self):
        return self.__fstop.value

    def get_gamma_value(self):
        return self.__gamma.value

    def get_blackpoint_value(self):
        return self.__blackpoint.value

    def get_whitepoint_value(self):
        return self.__whitepoint.value

    def get_lift_value(self):
        return self.__lift.value
