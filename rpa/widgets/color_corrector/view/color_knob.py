import math
try:
    from PySide2 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
from rpa.widgets.sub_widgets import input_line_edit
from rpa.widgets.color_corrector.view.color_panel import ColorPanel
from rpa.widgets.color_corrector.view.slider import Slider
from rpa.widgets.sub_widgets.striped_frame import StripedFrame
from rpa.widgets.color_corrector.utils import FormatNumber

import rpa.widgets.color_corrector.view.resources.resources

LABEL_WIDTH = 70


class RGBWidget(QtWidgets.QWidget):
    SIG_COLOR_CHANGED = QtCore.Signal(float, float, float)
    def __init__(self):
        super().__init__()
        self.__red = input_line_edit.InputLineEdit(self)
        self.__blue = input_line_edit.InputLineEdit(self)
        self.__green = input_line_edit.InputLineEdit(self)
        self.__red.setEnabled(False)
        self.__blue.setEnabled(False)
        self.__green.setEnabled(False)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        strip_1 = StripedFrame()
        strip_1.setFixedHeight(2)
        label = QtWidgets.QLabel(" (expand to edit) ")
        strip_2 = StripedFrame()
        strip_2.setFixedHeight(2)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.__red)
        layout.addWidget(self.__green)
        layout.addWidget(self.__blue)
        layout.addWidget(strip_1, 5)
        layout.addWidget(label)
        layout.addWidget(strip_2, 5)

        self.setLayout(layout)

    def set_red(self, value):
        self.__red.setText(FormatNumber(value))

    def set_green(self, value):
        self.__green.setText(FormatNumber(value))

    def set_blue(self, value):
        self.__blue.setText(FormatNumber(value))

    def set_color(self, rgb):
        self.set_red(rgb[0])
        self.set_green(rgb[1])
        self.set_blue(rgb[2])


class ColorKnob(QtWidgets.QWidget):
    """ Contains UI for a particular knob in color corrector widget (label, slider and color panel). """
    SIG_VALUE_CHANGED = QtCore.Signal(float)
    SIG_COLOR_CHANGED = QtCore.Signal(list)

    def __init__(self, name, hints, parent=None, is_color=True, width=LABEL_WIDTH):
        super().__init__(parent=parent)
        self.__name = name
        self.__hints = hints
        self.__label_width = width
        self.__is_color = is_color
        self.__is_default = True

        self.__current_value = None
        self.__current_rgb = []

        self.__label = QtWidgets.QLabel(self.__name, self)
        self.__label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.__label.setFixedWidth(self.__label_width)
        self.__label.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__slider = Slider(self.__hints)
        self.__slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__color_panel_button = QtWidgets.QToolButton()
        self.__color_panel_button.setToolTip("Color Panel")
        self.__color_panel_button.setCheckable(True)
        self.__color_panel_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__color_panel_button.setIcon(
            QtGui.QIcon(QtGui.QPixmap(':color_wheel_1.png'))
            )
        self.__color_panel_button.setIconSize(QtCore.QSize(20, 20))

        self.__rgb_widget = RGBWidget()
        self.__rgb_widget.hide()
        if self.__is_color:
            self.__color_panel = ColorPanel(self.__hints, self)
            self.__color_panel.hide()
        spacer = QtWidgets.QSpacerItem(
            30, 1, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.__label)
        layout.addWidget(self.__color_panel_button)
        if not self.__is_color:
            layout.addItem(spacer)
        layout.addWidget(self.__slider)
        layout.addWidget(self.__rgb_widget)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(layout)
        if self.__is_color: main_layout.addWidget(self.__color_panel)
        self.setLayout(main_layout)

        if self.__is_color:
            self.__slider.SIG_VALUE_CHANGED.connect(self.__modify_all_channels)
            self.__color_panel_button.clicked.connect(self.__toggle_color_panel)
            self.__color_panel.SIG_RED_SLIDER_CHANGED.connect(self.__red_changed)
            self.__color_panel.SIG_BLUE_SLIDER_CHANGED.connect(self.__blue_changed)
            self.__color_panel.SIG_GREEN_SLIDER_CHANGED.connect(self.__green_changed)
            self.__color_panel.SIG_CIRCLE_COLOR_CHANGED.connect(self.__circle_color_changed)
        else:
            self.__color_panel_button.hide()
            self.__slider.SIG_VALUE_CHANGED.connect(self.SIG_VALUE_CHANGED)

    def __toggle_color_panel(self):
        self.__color_panel.setVisible(not self.__color_panel.isVisible())
        if not self.__color_panel.isVisible():
            if len(set(self.__current_rgb)) == 1:
                self.__slider.show()
                self.__rgb_widget.hide()
            else:
                self.__slider.hide()
                self.__rgb_widget.show()

    def __circle_color_changed(self, rgb):
        self.SIG_COLOR_CHANGED.emit(rgb)

    def __modify_all_channels(self, value):
        self.__current_rgb = [value, value, value]
        self.SIG_COLOR_CHANGED.emit(self.__current_rgb)
        self.__color_panel.set_color(self.__current_rgb)
        self.__rgb_widget.set_color(self.__current_rgb)

    def __red_changed(self, r):
        self.__current_rgb[0] = r
        self.SIG_COLOR_CHANGED.emit(self.__current_rgb)

    def __blue_changed(self, b):
        self.__current_rgb[2] = b
        self.SIG_COLOR_CHANGED.emit(self.__current_rgb)

    def __green_changed(self, g):
        self.__current_rgb[1] = g
        self.SIG_COLOR_CHANGED.emit(self.__current_rgb)

    def set_color(self, rgb, is_default=False):
        """ This updates the sliders which has colors(rgb)
        as their value. This in turn updates the color panel, sliders
        and rgb widget. """
        self.__current_rgb = list(rgb)
        self.__rgb_widget.set_color(rgb)
        self.__color_panel.set_color(rgb)
        self.__slider.setValue(rgb[0])
        self.set_default(is_default)
        if not self.__color_panel.isVisible():
            if len(set(self.__current_rgb)) == 1:
                self.__slider.show()
                self.__rgb_widget.hide()
            else:
                self.__slider.hide()
                self.__rgb_widget.show()

    def set_value(self, value, is_default=False):
        """ This sets sliders which has either int/float
        as their value. """
        self.__slider.setValue(value)
        self.set_default(is_default)

    def set_default(self, default):
        self.__is_default = default
        if default:
            self.__label.setStyleSheet("QLabel {color: rgb(255, 255, 255);}")
        else:
            self.__label.setStyleSheet("QLabel {color: rgb(192, 158, 64);}")

    def is_default(self):
        return self.__is_default

    @property
    def value(self):
        if self.__current_rgb:
            return self.__current_rgb
        return self.__current_value
