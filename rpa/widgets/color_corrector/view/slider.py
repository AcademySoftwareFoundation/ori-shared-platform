import math
try:
    from PySide2 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
from rpa.widgets.sub_widgets import input_line_edit
from rpa.widgets.sub_widgets.slider_widget import SliderWidget
from rpa.widgets.color_corrector.utils import FormatNumber


def GetSliderArgsFromHints(hints):
    """
    Recognized hints:
        slidermin
        slidermax
        slidercenter
        sliderexponent
        slidergradient: name of a gradient to overlay on the slider
            (ex: 'CYAN_GRAY_RED')
        int
    """
    kwargs = {}

    minVal = float(hints.get('slidermin', 0.0))
    maxVal = float(hints.get('slidermax', 1.0))
    kwargs['range'] = sorted([minVal, maxVal])

    center = hints.get('slidercenter')
    if center is not None:
        kwargs['center'] = float(center)

    exponent = hints.get('sliderexponent')
    if exponent is not None:
        kwargs['axisExponent'] = float(exponent)

    # gradient = hints.get('slidergradient')
    # if gradient is not None:
    #     kwargs['gradient'] = gradient

    kwargs['integer'] = HintTrue('int', hints)

    return kwargs

def EvalLocalMath(s):
    g = {}
    g.update(math.__dict__)
    g['min'] = min
    g['max'] = max

    return eval(str(s), g)

def HintTrue(hintName, hints, default=None):
    """
    Return whether the named hint is true in the given hints.
    True values are case-insensitive strings "y", "yes", "true", "1", and "on",
        and non-strings which evaluate as boolean True.
    """
    if not hints:
        return False

    value = hints.get(hintName, default)
    if isinstance(value, str):
        return value.lower() in _HintTrueValues
    return bool(value)


class Slider(QtWidgets.QWidget):
    SIG_VALUE_CHANGED = QtCore.Signal(float)

    def __init__(self, hints, gradient=None, parent=None):
        super().__init__(parent)
        self.__hints = hints

        self.__input = input_line_edit.InputLineEdit(self)
        self.__slider = SliderWidget(self, fontScale=0.8, gradient=gradient, **GetSliderArgsFromHints(self.__hints))
        self.__slider.setFocusPolicy(QtCore.Qt.NoFocus)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.__input)
        layout.addWidget(self.__slider, 5)

        self.setLayout(layout)

        self.__slider.SIG_VALUE_CHANGED.connect(self.__slider_value_changed)
        self.__input.SIG_LOST_FOCUS.connect(self.__input_value_changed)

    @QtCore.Slot(object)
    def __slider_value_changed(self, value):
        input_value = FormatNumber(value)
        self.__input.blockSignals(True)
        self.__input.setText(input_value)
        self.__input.blockSignals(False)
        self.SIG_VALUE_CHANGED.emit(value)

    @QtCore.Slot()
    def __input_value_changed(self):
        value = EvalLocalMath(str(self.__input.text()))
        self.__slider.blockSignals(True)
        self.__slider.setValue(value)
        self.__slider.blockSignals(False)
        self.SIG_VALUE_CHANGED.emit(value)

    def getValue(self):
        return float(self.__slider.value())

    def setValue(self, value):
        self.__slider.blockSignals(True)
        self.__slider.setValue(value)
        self.__slider.blockSignals(False)
        input_value = FormatNumber(value)
        self.__input.blockSignals(True)
        self.__input.setText(input_value)
        self.__input.blockSignals(False)

    def reset(self):
        default = self.__hints.get('default')
        self.SIG_VALUE_CHANGED.emit(default)
