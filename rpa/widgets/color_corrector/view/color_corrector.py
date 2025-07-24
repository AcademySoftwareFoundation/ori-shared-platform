try:
    from PySide2 import QtWidgets, QtGui, QtCore
except ImportError:
    from PySide6 import QtWidgets, QtGui, QtCore

from rpa.widgets.sub_widgets.striped_frame import StripedFrame
from rpa.widgets.sub_widgets import mini_label_button

from rpa.widgets.color_corrector.view.color_knob import ColorKnob
from rpa.widgets.color_corrector.utils import Slider, SliderAttrs
from rpa.widgets.color_corrector import constants as C
from rpa.session_state.color_corrections import ColorTimer, Grade

import rpa.widgets.color_corrector.view.resources.resources


class ColorCorrectionAndGrading(QtWidgets.QScrollArea):

    # ColorTimer
    SIG_CREATE_COLORTIMER = QtCore.Signal(str) # cc_id
    SIG_OFFSET_CHANGED = QtCore.Signal(str, int, list)
    SIG_SLOPE_CHANGED = QtCore.Signal(str, int, list)
    SIG_POWER_CHANGED = QtCore.Signal(str, int, list)
    SIG_SAT_CHANGED = QtCore.Signal(str, int, float)
    SIG_MUTE_COLOR_TIMER = QtCore.Signal(str, int)
    SIG_RESET_COLOR_TIMER = QtCore.Signal(str, int)
    SIG_DELETE_COLOR_TIMER = QtCore.Signal(str, int)

    # Grade
    SIG_CREATE_GRADE = QtCore.Signal(str)  # cc_id
    SIG_FSTOP_CHANGED = QtCore.Signal(str, int, list)
    SIG_GAMMA_CHANGED = QtCore.Signal(str, int, list)
    SIG_BLACKPOINT_CHANGED = QtCore.Signal(str, int, list)
    SIG_WHITEPOINT_CHANGED = QtCore.Signal(str, int, list)
    SIG_LIFT_CHANGED = QtCore.Signal(str, int, list)
    SIG_MUTE_GRADE = QtCore.Signal(str, int)
    SIG_RESET_GRADE = QtCore.Signal(str, int)
    SIG_DELETE_GRADE = QtCore.Signal(str, int)

    # Region
    SIG_CREATE_REGION = QtCore.Signal(str) # cc_id
    SIG_DELETE_REGION = QtCore.Signal(str) # cc_id
    SIG_FALLOFF_CHANGED = QtCore.Signal(str, float) # cc_id, value

    def __init__(self, cc_id, name:str, type:str, slider_attrs:SliderAttrs):
        super().__init__()
        self.__cc_id = cc_id
        self.__name = name
        self.__type = type
        self.__is_mute = False
        self.__is_read_only = False
        self.__slider_attrs = slider_attrs
        self.setWidgetResizable(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.__create_colortimer_btn = QtWidgets.QPushButton("Create ColorTimer")
        self.__create_grade_btn = QtWidgets.QPushButton("Create Grade")
        self.__create_region_btn = QtWidgets.QPushButton("Add Region")

        layout = QtWidgets.QHBoxLayout()
        # TODO: hide these buttons due to incompatibility with itview4 and sync server
        # layout.addWidget(self.__create_colortimer_btn)
        # layout.addWidget(self.__create_grade_btn)
        # layout.addWidget(self.__create_region_btn)

        self.__main_layout = QtWidgets.QVBoxLayout()
        self.__main_layout.addStretch()
        self.__main_layout.addLayout(layout)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.__main_layout)
        self.setWidget(widget)

        self.__color_nodes = []
        self.__region = None

        self.__create_colortimer_btn.clicked.connect(lambda: self.SIG_CREATE_COLORTIMER.emit(self.__cc_id))
        self.__create_grade_btn.clicked.connect(lambda: self.SIG_CREATE_GRADE.emit(self.__cc_id))
        self.__create_region_btn.clicked.connect(lambda: self.SIG_CREATE_REGION.emit(self.__cc_id))

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def id(self):
        return self.__cc_id

    @id.setter
    def id(self, id):
        self.__cc_id = id

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    @property
    def nodes(self):
        return self.__color_nodes

    @property
    def region(self):
        return self.__region

    def get_node(self, index):
        return self.__color_nodes[index]

    def is_read_only(self):
        return self.__is_read_only

    def set_read_only(self, value):
        self.__is_read_only = value
        for node in self.__color_nodes:
            node.set_enabled(not value)
        if self.__region:
            self.__region.set_enabled(not value)
        self.__create_colortimer_btn.setEnabled(not value)
        self.__create_grade_btn.setEnabled(not value)
        self.__create_region_btn.setEnabled(not value)

    def mute(self, index, mute):
        node = self.__color_nodes[index]
        if not node: return
        if self.__is_read_only: return
        node.set_mute(mute)

    def mute_all(self, mute):
        self.__is_mute = mute
        if self.__is_read_only: return
        for node in self.__color_nodes:
            node.set_mute(mute)

    def is_mute(self):
        return self.__is_mute

    def create_region(self):
        self.__create_region_btn.setEnabled(False)
        self.__region = Region(self.__slider_attrs)
        self.__main_layout.insertWidget(0, self.__region)

        self.__region.SIG_FALLOFF_CHANGED.connect(lambda value: self.SIG_FALLOFF_CHANGED.emit(self.__cc_id, value))
        self.__region.SIG_DELETE_REGION.connect(lambda : self.SIG_DELETE_REGION.emit(self.__cc_id))
        if self.is_read_only():
            self.__region.set_enabled(False)

    def create_colortimer(self):
        color_timer = ColorTimer(self.__slider_attrs)
        index = len(self.__color_nodes)
        self.__color_nodes.append(color_timer)
        self.__main_layout.insertWidget(self.__main_layout.count()-2, color_timer)

        color_timer.SIG_OFFSET_CHANGED.connect(lambda value: self.SIG_OFFSET_CHANGED.emit(self.__cc_id, index, value))
        color_timer.SIG_POWER_CHANGED.connect(lambda value: self.SIG_POWER_CHANGED.emit(self.__cc_id, index, value))
        color_timer.SIG_SLOPE_CHANGED.connect(lambda value: self.SIG_SLOPE_CHANGED.emit(self.__cc_id, index, value))
        color_timer.SIG_SAT_CHANGED.connect(lambda value: self.SIG_SAT_CHANGED.emit(self.__cc_id, index, value))

        color_timer.SIG_MUTE_COLOR_TIMER.connect(lambda : self.SIG_MUTE_COLOR_TIMER.emit(self.__cc_id, index))
        color_timer.SIG_RESET_COLOR_TIMER.connect(lambda : self.SIG_RESET_COLOR_TIMER.emit(self.__cc_id, index))
        color_timer.SIG_DELETE_COLOR_TIMER.connect(lambda : self.SIG_DELETE_COLOR_TIMER.emit(self.__cc_id, index))

        if self.is_read_only():
            color_timer.set_enabled(False)

    def create_grade(self):
        grade = Grade(self.__slider_attrs)
        index = len(self.__color_nodes)
        self.__color_nodes.append(grade)
        self.__main_layout.insertWidget(self.__main_layout.count()-2, grade)

        grade.SIG_FSTOP_CHANGED.connect(lambda value: self.SIG_FSTOP_CHANGED.emit(self.__cc_id, index, value))
        grade.SIG_GAMMA_CHANGED.connect(lambda value: self.SIG_GAMMA_CHANGED.emit(self.__cc_id, index, value))
        grade.SIG_BLACKPOINT_CHANGED.connect(lambda value: self.SIG_BLACKPOINT_CHANGED.emit(self.__cc_id, index, value))
        grade.SIG_WHITEPOINT_CHANGED.connect(lambda value: self.SIG_WHITEPOINT_CHANGED.emit(self.__cc_id, index, value))
        grade.SIG_LIFT_CHANGED.connect(lambda value: self.SIG_LIFT_CHANGED.emit(self.__cc_id, index, value))

        grade.SIG_MUTE_GRADE.connect(lambda : self.SIG_MUTE_GRADE.emit(self.__cc_id, index))
        grade.SIG_RESET_GRADE.connect(lambda : self.SIG_RESET_GRADE.emit(self.__cc_id, index))
        grade.SIG_DELETE_GRADE.connect(lambda : self.SIG_DELETE_GRADE.emit(self.__cc_id, index))

        if self.is_read_only():
            grade.set_enabled(False)

    def set_node_values(self, index, node):
        node_widget = self.__color_nodes[index]
        if isinstance(node, ColorTimer):
            node_widget.set_offset(node.offset)
            node_widget.set_slope(node.slope)
            node_widget.set_power(node.power)
            node_widget.set_sat(node.saturation)
            if not self.__is_read_only: node_widget.set_mute(node.mute)
        if isinstance(node, Grade):
            node_widget.set_fstop(node.gain)
            node_widget.set_gamma(node.gamma)
            node_widget.set_blackpoint(node.blackpoint)
            node_widget.set_whitepoint(node.whitepoint)
            node_widget.set_lift(node.lift)
            if not self.__is_read_only: node_widget.set_mute(node.mute)

    def set_falloff(self, value):
        self.__region.set_falloff(value)

    def delete_node(self, index):
        node_widget = self.__color_nodes.pop(index)
        node_widget.deleteLater()
        self.__main_layout.removeWidget(node_widget)

    def delete_region(self):
        self.__region.deleteLater()
        self.__main_layout.removeWidget(self.__region)
        self.__region = None
        self.__create_region_btn.setEnabled(True)

    def clear_nodes(self):
        for node in self.__color_nodes:
            node.deleteLater()
            self.__main_layout.removeWidget(node)
        self.__color_nodes.clear()

    def reset(self):
        self.__cc_id = None
        self.__is_mute = False
        self.__is_read_only = False
        self.clear_nodes()
        self.clear_region()

    def clear_region(self):
        if self.__region is None: return
        self.delete_region()


class Header(QtWidgets.QWidget):
    SIG_MUTE_CLICKED = QtCore.Signal()
    SIG_RESET_CLICKED = QtCore.Signal()
    SIG_DELETE_CLICKED = QtCore.Signal()
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
        self.__reset_button = mini_label_button.MiniLabelButton("reset", self)
        self.__delete_button = mini_label_button.MiniLabelButton("delete", self)
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
        h_layout.addWidget(self.__reset_button, 0)
        # TODO: hide these buttons due to incompatibility with itview4 and sync server
        #h_layout.addWidget(self.__delete_button, 0)
        h_layout.addWidget(strip_2, 5)
        h_layout.addWidget(self.__title_label, 0)
        self.setLayout(h_layout)

        self.__mute_button.SIG_CLICKED.connect(self.SIG_MUTE_CLICKED)
        self.__reset_button.SIG_CLICKED.connect(self.SIG_RESET_CLICKED)
        self.__delete_button.SIG_CLICKED.connect(self.SIG_DELETE_CLICKED)

    def get_mute_btn(self):
        return self.__mute_button

    def get_reset_btn(self):
        return self.__reset_button

    def get_delete_btn(self):
        return self.__delete_button

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

class Region(QtWidgets.QWidget):
    LABEL_WIDTH = 65

    SIG_FALLOFF_CHANGED = QtCore.Signal(float)
    SIG_DELETE_REGION = QtCore.Signal()

    def __init__(self, slider_attrs:SliderAttrs):
        super().__init__()
        strip_1 = StripedFrame()
        strip_1.setFixedHeight(2)
        strip_1.setFixedWidth(10)
        self.__delete_button = mini_label_button.MiniLabelButton("delete", self)
        strip_2 = StripedFrame()
        strip_2.setFixedHeight(2)

        title_label = QtWidgets.QLabel("Region")
        italicsFont = QtGui.QFont(self.font())
        italicsFont.setItalic(True)
        title_label.setFont(italicsFont)
        mini_label_button.SetCompactWidgetWidth(title_label)

        title_layout = QtWidgets.QHBoxLayout()
        # TODO: hide these buttons due to incompatibility with itview4 and sync server
        # title_layout.addWidget(strip_1, 5)
        # title_layout.addWidget(self.__delete_button, 0)
        title_layout.addWidget(strip_2, 5)
        title_layout.addWidget(title_label, 0)

        self.__falloff = ColorKnob(
            Slider.FALLOFF.value, slider_attrs.get_value(Slider.FALLOFF), is_color=False, width=self.LABEL_WIDTH)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addLayout(title_layout)
        layout.addWidget(self.__falloff)
        self.setLayout(layout)

        self.__falloff.setVisible(True)
        self.__falloff.SIG_VALUE_CHANGED.connect(self.SIG_FALLOFF_CHANGED)
        self.__delete_button.SIG_CLICKED.connect(self.SIG_DELETE_REGION)

    def set_falloff(self, falloff):
        self.__falloff.set_value(falloff, is_default=C.DEFAULT_FALLOFF==falloff)

    def get_falloff(self):
        return self.__falloff.value

    def set_enabled(self, value):
        self.setEnabled(value)


class ColorTimer(QtWidgets.QWidget):
    LABEL_WIDTH = 65

    SIG_OFFSET_CHANGED = QtCore.Signal(list)
    SIG_SLOPE_CHANGED = QtCore.Signal(list)
    SIG_POWER_CHANGED = QtCore.Signal(list)
    SIG_SAT_CHANGED = QtCore.Signal(float)

    SIG_MUTE_COLOR_TIMER = QtCore.Signal()
    SIG_RESET_COLOR_TIMER = QtCore.Signal()
    SIG_DELETE_COLOR_TIMER = QtCore.Signal()

    def __init__(self, slider_attrs:SliderAttrs):
        super().__init__()
        self.type = "colortimer"
        self.__is_active = False

        visible = False
        self.__header = Header("ColorTimer", expand=visible)
        self.__header.SIG_TOGGLE_VISIBILITY.connect(self.__toggle_visibilty)

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

        self.__header.SIG_MUTE_CLICKED.connect(self.SIG_MUTE_COLOR_TIMER)
        self.__header.SIG_RESET_CLICKED.connect(self.SIG_RESET_COLOR_TIMER)
        self.__header.SIG_DELETE_CLICKED.connect(self.SIG_DELETE_COLOR_TIMER)

    def set_mute(self, mute):
        self.__header.get_mute_btn().setChecked(mute)
        self.__offset.setEnabled(not mute)
        self.__slope.setEnabled(not mute)
        self.__power.setEnabled(not mute)
        self.__sat.setEnabled(not mute)

    def set_enabled(self, value):
        self.__header.get_mute_btn().setEnabled(value)
        self.__header.get_reset_btn().setEnabled(value)
        self.__header.get_delete_btn().setEnabled(value)
        self.__offset.setEnabled(value)
        self.__slope.setEnabled(value)
        self.__power.setEnabled(value)
        self.__sat.setEnabled(value)

    def __toggle_visibilty(self, visible):
        self.__offset.setVisible(visible)
        self.__slope.setVisible(visible)
        self.__power.setVisible(visible)
        self.__sat.setVisible(visible)

    def set_offset(self, offset):
        self.__offset.set_color(offset, is_default=list(C.DEFAULT_OFFSET)==list(offset))
        self.__check_active_state()

    def set_slope(self, slope):
        self.__slope.set_color(slope, is_default=list(C.DEFAULT_SLOPE)==list(slope))
        self.__check_active_state()

    def set_power(self, power):
        self.__power.set_color(power, is_default=list(C.DEFAULT_POWER)==list(power))
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
    SIG_DELETE_GRADE = QtCore.Signal()

    def __init__(self, slider_attrs:SliderAttrs):
        super().__init__()
        self.__is_active = False
        self.type = "grade"

        visible = False
        self.__header = Header("Grade", expand=visible)
        self.__header.SIG_TOGGLE_VISIBILITY.connect(self.__toggle_visibilty)

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

        self.__header.SIG_MUTE_CLICKED.connect(self.SIG_MUTE_GRADE)
        self.__header.SIG_RESET_CLICKED.connect(self.SIG_RESET_GRADE)
        self.__header.SIG_DELETE_CLICKED.connect(self.SIG_DELETE_GRADE)

    def set_mute(self, mute):
        self.__header.get_mute_btn().setChecked(mute)
        self.__fstop.setEnabled(not mute)
        self.__gamma.setEnabled(not mute)
        self.__blackpoint.setEnabled(not mute)
        self.__whitepoint.setEnabled(not mute)
        self.__lift.setEnabled(not mute)

    def set_enabled(self, value):
        self.__header.get_mute_btn().setEnabled(value)
        self.__header.get_reset_btn().setEnabled(value)
        self.__header.get_delete_btn().setEnabled(value)
        self.__fstop.setEnabled(value)
        self.__gamma.setEnabled(value)
        self.__blackpoint.setEnabled(value)
        self.__whitepoint.setEnabled(value)
        self.__lift.setEnabled(value)

    def __toggle_visibilty(self, visible):
        self.__fstop.setVisible(visible)
        self.__gamma.setVisible(visible)
        self.__blackpoint.setVisible(visible)
        self.__whitepoint.setVisible(visible)
        self.__lift.setVisible(visible)

    def set_fstop(self, fstop):
        self.__fstop.set_color(fstop, is_default=list(C.DEFAULT_FSTOP)==list(fstop))
        self.__check_active_state()

    def set_gamma(self, gamma):
        self.__gamma.set_color(gamma, is_default=list(C.DEFAULT_GAMMA)==list(gamma))
        self.__check_active_state()

    def set_blackpoint(self, blackpoint):
        self.__blackpoint.set_color(blackpoint, is_default=list(C.DEFAULT_BLACKPOINT)==list(blackpoint))
        self.__check_active_state()

    def set_whitepoint(self, whitepoint):
        self.__whitepoint.set_color(whitepoint, is_default=list(C.DEFAULT_WHITEPOINT)==list(whitepoint))
        self.__check_active_state()

    def set_lift(self, lift):
        self.__lift.set_color(lift, is_default=list(C.DEFAULT_LIFT)==list(lift))
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