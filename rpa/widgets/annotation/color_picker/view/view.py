"""
View for Color Picker
"""

from PySide2 import QtCore, QtGui, QtWidgets

from rpa.widgets.sub_widgets.color_circle import ColorCircle

from rpa.widgets.annotation.color_picker.view.eye_dropper import EyeDropper
from rpa.widgets.annotation.color_picker.view.color_monitor import ColorMonitor
from rpa.widgets.annotation.color_picker.view.color_sliders import ColorSliders
from rpa.widgets.annotation.color_picker.view.palette import BasicPalette
from rpa.widgets.annotation.color_picker.view.palette import RecentPalette
from rpa.widgets.annotation.color_picker.view.palette import CustomPalette
from rpa.widgets.annotation.color_picker.model import Rgb


class View(QtWidgets.QDialog):

    RED = 0
    GREEN = 1
    BLUE = 2
    TEMPERATURE = 3
    MAGENTA = 4
    INTENSITY = 5
    SATURATION = 6
    COLOR_CIRCLE = 7

    SIG_EYE_DROPPER_ENABLED = QtCore.Signal(bool)
    SIG_EYE_DROPPER_SIZE_NAME_CHANGED = QtCore.Signal(str)

    SIG_RED_SLIDER_CHANGED = QtCore.Signal(float)
    SIG_GREEN_SLIDER_CHANGED = QtCore.Signal(float)
    SIG_BLUE_SLIDER_CHANGED = QtCore.Signal(float)
    SIG_TEMPERATURE_SLIDER_CHANGED = QtCore.Signal(float)
    SIG_MAGENTA_SLIDER_CHANGED = QtCore.Signal(float)
    SIG_INTENSITY_SLIDER_CHANGED = QtCore.Signal(float)
    SIG_SATURATION_SLIDER_CHANGED = QtCore.Signal(float)

    SIG_SET_CURRENT_COLOR = QtCore.Signal(object)
    SIG_CLEAR_RECENT_COLORS = QtCore.Signal()
    SIG_CLEAR_CUSTOM_COLORS = QtCore.Signal()
    SIG_ADD_CUSTOM_COLOR = QtCore.Signal()
    SIG_SET_FAV_COLOR = QtCore.Signal(int)
    SIG_CLEAR_FAV_COLORS = QtCore.Signal()

    SIG_SHIFT_KEY_PRESSED = QtCore.Signal(bool)
    SIG_CLOSE = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Color Picker')
        self.setFixedSize(660, 620)

        self.__eye_dropper = EyeDropper()
        self.__color_monitor = ColorMonitor()
        self.__color_circle = ColorCircle()
        self.__color_sliders = ColorSliders()
        self.__basic_palette = BasicPalette()
        self.__recent_palette = RecentPalette()
        self.__custom_palette = CustomPalette()

        layout = QtWidgets.QGridLayout()
        layout.setHorizontalSpacing(20)
        layout.setContentsMargins(20, 0, 10, 20)

        layout.addWidget(self.__eye_dropper, 0, 0, alignment=QtCore.Qt.AlignRight)
        layout.addWidget(self.__color_monitor, 0, 1, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.__color_circle, 1, 0, alignment=QtCore.Qt.AlignVCenter)
        layout.addWidget(self.__color_sliders, 1, 1, 1, 1, alignment=QtCore.Qt.AlignVCenter)
        layout.addWidget(self.__basic_palette, 2, 0, 2, 1, alignment=QtCore.Qt.AlignVCenter)
        layout.addWidget(self.__recent_palette, 2, 1, alignment=QtCore.Qt.AlignVCenter)
        layout.addWidget(self.__custom_palette, 3, 1, alignment=QtCore.Qt.AlignVCenter)

        self.setLayout(layout)

        self.__eye_dropper.SIG_EYE_DROPPER_ENABLED.connect(self.SIG_EYE_DROPPER_ENABLED)
        self.__eye_dropper.SIG_EYE_DROPPER_SIZE_NAME_CHANGED.connect(
            self.SIG_EYE_DROPPER_SIZE_NAME_CHANGED
        )

        self.__color_sliders.SIG_RED_SLIDER_CHANGED.connect(self.SIG_RED_SLIDER_CHANGED)
        self.__color_sliders.SIG_GREEN_SLIDER_CHANGED.connect(self.SIG_GREEN_SLIDER_CHANGED)
        self.__color_sliders.SIG_BLUE_SLIDER_CHANGED.connect(self.SIG_BLUE_SLIDER_CHANGED)
        self.__color_sliders.SIG_TEMPERATURE_SLIDER_CHANGED.connect(self.SIG_TEMPERATURE_SLIDER_CHANGED)
        self.__color_sliders.SIG_MAGENTA_SLIDER_CHANGED.connect(self.SIG_MAGENTA_SLIDER_CHANGED)
        self.__color_sliders.SIG_INTENSITY_SLIDER_CHANGED.connect(self.SIG_INTENSITY_SLIDER_CHANGED)
        self.__color_sliders.SIG_SATURATION_SLIDER_CHANGED.connect(self.SIG_SATURATION_SLIDER_CHANGED)

        self.__basic_palette.SIG_TILE_CLICKED.connect(self.SIG_SET_CURRENT_COLOR)

        self.__recent_palette.SIG_TILE_CLICKED.connect(self.SIG_SET_CURRENT_COLOR)
        self.__recent_palette.SIG_CLEAR_COLORS.connect(self.SIG_CLEAR_RECENT_COLORS)

        self.__custom_palette.SIG_TILE_CLICKED.connect(self.SIG_SET_CURRENT_COLOR)
        self.__custom_palette.SIG_CLEAR_CUSTOM_COLORS.connect(self.SIG_CLEAR_CUSTOM_COLORS)
        self.__custom_palette.SIG_ADD_CUSTOM_COLOR.connect(self.SIG_ADD_CUSTOM_COLOR)
        self.__custom_palette.SIG_SET_FAV_COLOR.connect(self.SIG_SET_FAV_COLOR)
        self.__custom_palette.SIG_CLEAR_FAV_COLORS.connect(self.SIG_CLEAR_FAV_COLORS)

        self.__color_circle.SIG_COLOR_CHANGED.connect(self.SIG_SET_CURRENT_COLOR)
        self.SIG_SHIFT_KEY_PRESSED.connect(self.__color_circle.SIG_CONSTRAINT_HV)

        self.__color_monitor.SIG_SET_CURRENT_COLOR.connect(self.SIG_SET_CURRENT_COLOR)

    def enable_eye_dropper(self, enable):
        self.__eye_dropper.enable_eye_dropper(enable)

    def set_eye_dropper_sample_size(self, index):
        self.__eye_dropper.set_eye_dropper_sample_size(index)

    def set_eye_dropper_sample_sizes(self, sample_sizes):
        self.__eye_dropper.set_eye_dropper_sample_sizes(sample_sizes)

    def set_current_color(self, color):
        self.__color_sliders.set_current_red(color.red)
        self.__color_sliders.set_current_green(color.green)
        self.__color_sliders.set_current_blue(color.blue)
        self.__color_sliders.set_current_temperature(color.temperature)
        self.__color_sliders.set_current_magenta(color.magenta)
        self.__color_sliders.set_current_intensity(color.intensity)
        self.__color_sliders.set_current_saturation(color.saturation)
        self.__color_sliders.set_saturation_end_color(Rgb(color.red, color.green, color.blue))
        self.__color_monitor.set_current_color(Rgb(color.red, color.green, color.blue))
        self.__color_circle.setColor(Rgb(color.red, color.green, color.blue))

    def set_recent_colors(self, colors):
        self.__recent_palette.update_colors(colors)

    def set_custom_colors(self, colors):
        self.__custom_palette.update_custom_colors(colors)

    def set_fav_color(self, index, rgb):
        self.__custom_palette.set_fav_color(index, rgb)

    def set_fav_colors(self, colors):
        self.__custom_palette.set_fav_colors(colors)

    def clear_fav_colors(self, colors):
        self.__custom_palette.clear_fav_colors(colors)

    def set_fav_color_tool_tip(self, index, tool_tip):
        self.__custom_palette.set_fav_color_tool_tip(index, tool_tip)

    def set_starting_color(self, rgb):
        self.__color_monitor.set_starting_color(rgb)

    def set_color_slider_delta(self, delta):
        self.__color_sliders.set_color_slider_delta(delta)

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Shift:
            self.SIG_SHIFT_KEY_PRESSED.emit(True)
        super().keyPressEvent(ev)

    def keyReleaseEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Shift:
            self.SIG_SHIFT_KEY_PRESSED.emit(False)
        super().keyReleaseEvent(ev)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.SIG_CLOSE.emit()
