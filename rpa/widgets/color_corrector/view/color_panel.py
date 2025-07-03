from PySide2 import QtCore, QtWidgets
from rpa.widgets.sub_widgets.color_circle import ColorCircle
from rpa.widgets.color_corrector.view.color_sliders import ColorSliders


class Rgb(object):

    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def update(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

    def get(self):
        return self.red, self.green, self.blue

    def get_copy(self):
        return Rgb(self.red, self.green, self.blue)

    def __eq__(self, other):
        if self.red == other.red and \
            self.green == other.green and \
            self.blue == other.blue:
            return True
        return False

class ColorPanel(QtWidgets.QWidget):

    SIG_RED_SLIDER_CHANGED = QtCore.Signal(float)
    SIG_GREEN_SLIDER_CHANGED = QtCore.Signal(float)
    SIG_BLUE_SLIDER_CHANGED = QtCore.Signal(float)

    SIG_CIRCLE_COLOR_CHANGED = QtCore.Signal(list)

    def __init__(self, hints, parent):
        super().__init__(parent=parent)
        self.__color_circle = ColorCircle(size=200)
        self.__color_sliders = ColorSliders(hints)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.__color_circle, alignment=QtCore.Qt.AlignVCenter)
        main_layout.addWidget(self.__color_sliders, alignment=QtCore.Qt.AlignVCenter)
        self.setLayout(main_layout)

        self.__color_circle.SIG_COLOR_CHANGED.connect(self.__circle_color_changed)
        self.__color_sliders.SIG_RED_SLIDER_CHANGED.connect(self.SIG_RED_SLIDER_CHANGED)
        self.__color_sliders.SIG_GREEN_SLIDER_CHANGED.connect(self.SIG_GREEN_SLIDER_CHANGED)
        self.__color_sliders.SIG_BLUE_SLIDER_CHANGED.connect(self.SIG_BLUE_SLIDER_CHANGED)

    def set_color(self, color):
        self.__color_sliders.set_color(color)
        self.__color_circle.blockSignals(True)
        self.__color_circle.setColor(Rgb(color[0], color[1], color[2]))
        self.__color_circle.blockSignals(False)

    def __circle_color_changed(self, color):
        self.SIG_CIRCLE_COLOR_CHANGED.emit([color.red, color.green, color.blue])
