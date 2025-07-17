from PySide2 import QtGui, QtCore, QtWidgets
import rpa.widgets.image_controller.resources.resources


class SliderToolBar(QtWidgets.QToolBar):
    SIG_RESET = QtCore.Signal()
    SIG_SLIDER_VALUE_CHANGED = QtCore.Signal(float) # fstop value
    SIG_TOOLBAR_VISIBLE = QtCore.Signal()

    def __init__(self, title, name, min_val=0, max_val=4, value=0, interval=0.1):
        super().__init__()
        self.setWindowTitle(title)
        self.setObjectName(title)
        self.addWidget(QtWidgets.QLabel(name))

        self.__slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.__slider.setMinimumWidth(400)
        self.__slider.setMinimum(min_val*250)
        self.__slider.setMaximum(max_val*250)
        self.__slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.__slider.setTickInterval(int(interval*250))
        self.__slider.setSingleStep(int(interval*250))
        self.addWidget(self.__slider)

        self.__reset_btn = QtWidgets.QPushButton()
        self.__reset_btn.setIcon(QtGui.QIcon(QtGui.QPixmap(":reset.png")))
        self.__reset_btn.clicked.connect(self.SIG_RESET)
        self.addWidget(self.__reset_btn)

        self.__slider.setValue(int(value*250.0))
        self.__slider.sliderMoved.connect(self.__change_value)

    @QtCore.Slot(int)
    def __change_value(self, value):
        self.SIG_SLIDER_VALUE_CHANGED.emit(value/250.0)

    def set_slider_value(self, value):
        self.__slider.setValue(int(value*250.0))

    def showEvent(self, event):
        self.SIG_TOOLBAR_VISIBLE.emit()

    def hideEvent(self, event):
        self.SIG_TOOLBAR_VISIBLE.emit()
