from PySide2 import QtCore, QtWidgets
from rpa.widgets.color_corrector.view.clearing_slider_label import ClearingSliderLabel
from rpa.widgets.color_corrector.view.slider import Slider


class ColorConverter(object):

    @staticmethod
    def tmi_to_rgb(temperature, magenta, intensity):
        red = green = blue = 0

        if magenta == 0.0 and temperature == 0.0:
            red = green = blue = intensity
        else:
            green = ((3.0 * intensity) - (2.0 * magenta)) / 3.0
            red = ((6.0 * intensity) + (2.0 * magenta) - (3.0 * temperature)) / 6.0
            blue = red + temperature

        return red, green, blue

    @staticmethod
    def rgb_to_tmi(red, green, blue):
        temperature = blue - red
        magenta = (red + blue)/2.0 - green
        intensity = (red + green + blue)/3.0

        return temperature, magenta, intensity


class ColorSliders(QtWidgets.QWidget):
    SIG_RED_SLIDER_CHANGED = QtCore.Signal(float)
    SIG_GREEN_SLIDER_CHANGED = QtCore.Signal(float)
    SIG_BLUE_SLIDER_CHANGED = QtCore.Signal(float)

    def __init__(self, hints, parent=None):
        super().__init__(parent)
        self.__current_intensity = self.__default_intensity = hints.get('default')
        self.__intensity = Slider(hints, gradient='BLACK_GRAY_WHITE')
        self.__label_intensity = ClearingSliderLabel("I", tooltip="Intensity")
        self.__label_intensity.SIG_RESET_SLIDER.connect(self.__intensity.reset)

        self.__current_temperature = self.__default_temperature = 0
        self.__temperature = Slider(hints, gradient='YELLOW_BLUE')
        self.__label_temperature = ClearingSliderLabel("T", tooltip="Temperature")
        self.__label_temperature.SIG_RESET_SLIDER.connect(self.__temperature.reset)

        self.__current_magenta = self.__default_magenta = 0
        self.__magenta = Slider(hints, gradient='GREEN_MAGENTA')
        self.__label_magenta = ClearingSliderLabel("M", tooltip="Magenta")
        self.__label_magenta.SIG_RESET_SLIDER.connect(self.__magenta.reset)

        self.__default_red = hints.get('default')
        self.__red = Slider(hints, gradient='RED')
        self.__label_red = ClearingSliderLabel("R", tooltip="Red")
        self.__label_red.SIG_RESET_SLIDER.connect(self.__red.reset)

        self.__default_green = hints.get('default')
        self.__green = Slider(hints, gradient='GREEN')
        self.__label_green = ClearingSliderLabel("G", tooltip="Green")
        self.__label_green.SIG_RESET_SLIDER.connect(self.__green.reset)

        self.__default_blue = hints.get('default')
        self.__blue = Slider(hints, gradient='BLUE')
        self.__label_blue = ClearingSliderLabel("B", tooltip="Blue")
        self.__label_blue.SIG_RESET_SLIDER.connect(self.__blue.reset)

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.__label_intensity , 0, 0)
        layout.addWidget(self.__intensity, 0, 1)
        layout.addWidget(self.__label_temperature, 1, 0)
        layout.addWidget(self.__temperature, 1, 1)
        layout.addWidget(self.__label_magenta, 2, 0)
        layout.addWidget(self.__magenta, 2, 1)
        layout.addWidget(self.__label_red, 3, 0)
        layout.addWidget(self.__red, 3, 1)
        layout.addWidget(self.__label_green, 4, 0)
        layout.addWidget(self.__green, 4, 1)
        layout.addWidget(self.__label_blue, 5, 0)
        layout.addWidget(self.__blue, 5, 1)

        self.setLayout(layout)

        self.__red.SIG_VALUE_CHANGED.connect(self.SIG_RED_SLIDER_CHANGED)
        self.__green.SIG_VALUE_CHANGED.connect(self.SIG_GREEN_SLIDER_CHANGED)
        self.__blue.SIG_VALUE_CHANGED.connect(self.SIG_BLUE_SLIDER_CHANGED)
        self.__temperature.SIG_VALUE_CHANGED.connect(self.__set_current_temperature)
        self.__magenta.SIG_VALUE_CHANGED.connect(self.__set_current_magenta)
        self.__intensity.SIG_VALUE_CHANGED.connect(self.__set_current_intensity)

    def set_color(self, rgb):
        t, m, i = ColorConverter.rgb_to_tmi(
            rgb[0],
            rgb[1],
            rgb[2])
        self.set_red_slider(rgb[0])
        self.set_green_slider(rgb[1])
        self.set_blue_slider(rgb[2])
        self.set_temperature_slider(t)
        self.set_magenta_slider(m)
        self.set_intensity_slider(i)

    def __set_label_state(self, label, state=False):
        if state:
            label.setStyleSheet("QPushButton {color: rgb(255, 255, 255);}")
        else:
            label.setStyleSheet("QPushButton {color: rgb(192, 158, 64);}")

    def set_red_slider(self, value):
        self.__current_red = value
        self.__red.setValue(value)
        is_default = True if value == self.__default_red else False
        self.__set_label_state(self.__label_red, state=is_default)

    def set_green_slider(self, value):
        self.__current_green = value
        self.__green.setValue(value)
        is_default = True if value == self.__default_green else False
        self.__set_label_state(self.__label_green, state=is_default)

    def set_blue_slider(self, value):
        self.__current_blue = value
        self.__blue.setValue(value)
        is_default = True if value == self.__default_blue else False
        self.__set_label_state(self.__label_blue, state=is_default)

    def set_temperature_slider(self, value):
        self.__current_temperature = value
        self.__temperature.setValue(value)
        is_default = True if value == self.__default_temperature else False
        self.__set_label_state(self.__label_temperature, state=is_default)

    def set_magenta_slider(self, value):
        self.__current_magenta = value
        self.__magenta.setValue(value)
        is_default = True if value == self.__default_magenta else False
        self.__set_label_state(self.__label_magenta, state=is_default)

    def set_intensity_slider(self, value):
        self.__current_intensity = value
        self.__intensity.setValue(value)
        is_default = True if value == self.__default_intensity else False
        self.__set_label_state(self.__label_intensity, state=is_default)

    def __set_current_temperature(self, temperature):
        self.__current_temperature = temperature
        r, g, b = ColorConverter.tmi_to_rgb(
            self.__current_temperature,
            self.__current_magenta,
            self.__current_intensity)
        self.SIG_RED_SLIDER_CHANGED.emit(r)
        self.SIG_BLUE_SLIDER_CHANGED.emit(b)

    def __set_current_magenta(self, magenta):
        self.__current_magenta = magenta
        r, g, b = ColorConverter.tmi_to_rgb(
            self.__current_temperature,
            self.__current_magenta,
            self.__current_intensity)
        self.SIG_RED_SLIDER_CHANGED.emit(r)
        self.SIG_GREEN_SLIDER_CHANGED.emit(g)

    def __set_current_intensity(self, intensity):
        self.__current_intensity = intensity
        r, g, b = ColorConverter.tmi_to_rgb(
            self.__current_temperature,
            self.__current_magenta,
            self.__current_intensity)
        self.SIG_RED_SLIDER_CHANGED.emit(r)
        self.SIG_GREEN_SLIDER_CHANGED.emit(g)
        self.SIG_BLUE_SLIDER_CHANGED.emit(b)