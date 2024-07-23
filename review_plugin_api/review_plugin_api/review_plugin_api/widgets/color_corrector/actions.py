from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtWidgets import QAction, QActionGroup
from review_plugin_api.widgets.color_corrector import svg
from review_plugin_api.widgets.color_corrector import constants as C
import review_plugin_api.widgets.color_corrector.\
    _color_corrector.view.resources.resources


class Actions(QtCore.QObject):
    SIG_DRAW_SIZE_CHANGED = QtCore.Signal(object)
    SIG_ERASER_SIZE_CHANGED = QtCore.Signal(object)
    SIG_TEXT_SIZE_CHANGED = QtCore.Signal(object)

    def __init__(self):
        super().__init__()
        self.color = QAction("Color")
        self.__color_pixmap = QtGui.QPixmap(24, 24)

        self.__create_modes()

        self.color_corrector = QAction("Color Corrector")
        self.color_corrector.setShortcut(QtGui.QKeySequence("F9"))

    def __create_modes(self):
        self.toggle_rectangle_mode = QAction("Rectangle")
        self.toggle_rectangle_mode.setCheckable(True)
        self.toggle_rectangle_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":rectangle.png")))

        self.toggle_ellipse_mode = QAction("Ellipse")
        self.toggle_ellipse_mode.setCheckable(True)
        self.toggle_ellipse_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":ellipse.png")))

        self.toggle_lasso_mode = QAction("Lasso")
        self.toggle_lasso_mode.setCheckable(True)
        self.toggle_lasso_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":lasso.png")))

        modes = QActionGroup(self)
        modes.setExclusionPolicy(
            QActionGroup.ExclusionPolicy.ExclusiveOptional
        )
        for action in [
            self.toggle_rectangle_mode, self.toggle_ellipse_mode,
            self.toggle_lasso_mode
        ]:
            modes.addAction(action)
