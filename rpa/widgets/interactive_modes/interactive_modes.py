try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtWidgets import QAction
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QAction

from rpa.widgets.interactive_modes import constants as C
import rpa.widgets.interactive_modes.resources.resources


class InteractiveModes(QtCore.QObject):

    def __init__(self, rpa, main_window):
        self.__main_window = main_window
        self.__session_api = rpa.session_api

        self.__create_actions()
        self.__create_toolbar()

        dm = self.__session_api.delegate_mngr
        dm.add_post_delegate(self.__session_api.set_custom_session_attr, self.__update_custom_attrs)

    def __create_actions(self):
        def set_interactive_mode(mode):
            self.__session_api.set_custom_session_attr(C.INTERACTIVE_MODE, mode)

        self.__rectangle_mode = QAction("Rectangle")
        self.__rectangle_mode.setCheckable(True)
        self.__rectangle_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":rectangle.png")))
        self.__rectangle_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_RECTANGLE if is_checked else None))

        self.__ellipse_mode = QAction("Ellipse")
        self.__ellipse_mode.setCheckable(True)
        self.__ellipse_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":ellipse.png")))
        self.__ellipse_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_ELLIPSE if is_checked else None))

        self.__lasso_mode = QAction("Lasso")
        self.__lasso_mode.setCheckable(True)
        self.__lasso_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":lasso.png")))
        self.__lasso_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_LASSO if is_checked else None))

        self.pen_mode = QAction("Pen")
        self.pen_mode.setCheckable(True)
        self.pen_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(
                C.PEN.format(C.SVG_COLOR).encode("utf-8")))))
        self.pen_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_PEN if is_checked else None))

        self.line_mode = QAction("Line")
        self.line_mode.setCheckable(True)
        self.line_mode.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":line.png")))
        self.line_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_LINE if is_checked else None))

        self.multi_line_mode = QAction("Multi Line")
        self.multi_line_mode.setCheckable(True)
        self.multi_line_mode.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":multiline.png")))
        self.multi_line_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_MULTI_LINE if is_checked else None))

        self.__airbrush_mode = QAction("Airbrush")
        self.__airbrush_mode.setCheckable(True)
        self.__airbrush_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(
                C.AIRBRUSH.format(C.SVG_COLOR).encode("utf-8")))))
        self.__airbrush_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_AIRBRUSH if is_checked else None))

        self.__text_mode = QAction("Text")
        self.__text_mode.setCheckable(True)
        self.__text_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(
                C.TEXT.format(C.SVG_COLOR, 1.0).encode("utf-8")))))
        self.__text_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_TEXT if is_checked else None))

        self.hard_eraser_mode = QAction("Hard Eraser")
        self.hard_eraser_mode.setCheckable(True)
        self.hard_eraser_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(
                C.HARD_ERASER.format(C.SVG_COLOR).encode("utf-8")))))
        self.hard_eraser_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_HARD_ERASER if is_checked else None))

        self.__soft_eraser_mode = QAction("Soft Eraser")
        self.__soft_eraser_mode.setCheckable(True)
        self.__soft_eraser_mode.setIcon(
            QtGui.QIcon(QtGui.QPixmap.fromImage(QtGui.QImage.fromData(
                C.SOFT_ERASER.format(C.SVG_COLOR).encode("utf-8")))))
        self.__soft_eraser_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_SOFT_ERASER if is_checked else None))

        self.__move_mode = QAction("Move Annotations")
        self.__move_mode.setCheckable(True)
        self.__move_mode.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":hand.png")))
        self.__move_mode.setToolTip("Toggle moving annotations\nLMB: Pan\nMMB: Rotate\nRMB: Zoom")
        self.__move_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_MOVE if is_checked else None))

        self.transform_mode = QAction("Transform Mode")
        self.transform_mode.setCheckable(True)
        self.transform_mode.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":transforms.png")))
        self.transform_mode.setToolTip("Transform Mode\nLMB: Pan\nMMB: Rotate\nRMB: Zoom")
        self.transform_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_TRANSFORM if is_checked else None))

        self.dynamic_transform_mode = QAction("Dynamic Transform Mode")
        self.dynamic_transform_mode.setCheckable(True)
        self.dynamic_transform_mode.setIcon(
                QtGui.QIcon(QtGui.QPixmap(":transforms_dynamic.png")))
        self.dynamic_transform_mode.setToolTip("Dynamic Transform Mode\nLMB: Pan\nMMB: Rotate\nRMB: Zoom")
        self.dynamic_transform_mode.toggled.connect(
            lambda is_checked: set_interactive_mode(C.INTERACTIVE_MODE_DYNAMIC_TRANSFORM if is_checked else None))

    def __create_toolbar(self):
        self.tool_bar = QtWidgets.QToolBar()
        self.tool_bar.setWindowTitle("Interactive Toolbar")
        self.tool_bar.setObjectName(self.tool_bar.windowTitle())

        self.tool_bar.addAction(self.transform_mode)
        self.tool_bar.addAction(self.dynamic_transform_mode)

        self.tool_bar.addSeparator()

        self.tool_bar.addAction(self.__rectangle_mode)
        self.tool_bar.addAction(self.__ellipse_mode)
        self.tool_bar.addAction(self.__lasso_mode)

        self.tool_bar.addSeparator()

        self.tool_bar.addAction(self.pen_mode)
        self.tool_bar.addAction(self.line_mode)
        self.tool_bar.addAction(self.multi_line_mode)
        self.tool_bar.addAction(self.__airbrush_mode)
        self.tool_bar.addAction(self.__text_mode)

        self.tool_bar.addSeparator()

        self.tool_bar.addAction(self.hard_eraser_mode)
        self.tool_bar.addAction(self.__soft_eraser_mode)

        self.tool_bar.addSeparator()

        self.tool_bar.addAction(self.__move_mode)

        self.__main_window.addToolBarBreak(QtCore.Qt.BottomToolBarArea)
        self.__main_window.addToolBar(QtCore.Qt.BottomToolBarArea, self.tool_bar)

    def __update_custom_attrs(self, out, attr_id, value):
        if attr_id == C.INTERACTIVE_MODE:
            self.__update_interactive_mode(value)

    def __update_interactive_mode(self, mode):
        if  self.__rectangle_mode.isChecked() != (mode == C.INTERACTIVE_MODE_RECTANGLE):
            self.__rectangle_mode.blockSignals(True)
            self.__rectangle_mode.toggle()
            self.__rectangle_mode.blockSignals(False)
        if  self.__ellipse_mode.isChecked() != (mode == C.INTERACTIVE_MODE_ELLIPSE):
            self.__ellipse_mode.blockSignals(True)
            self.__ellipse_mode.toggle()
            self.__ellipse_mode.blockSignals(False)
        if  self.__lasso_mode.isChecked() != (mode == C.INTERACTIVE_MODE_LASSO):
            self.__lasso_mode.blockSignals(True)
            self.__lasso_mode.toggle()
            self.__lasso_mode.blockSignals(False)
        if  self.pen_mode.isChecked() != (mode == C.INTERACTIVE_MODE_PEN):
            self.pen_mode.blockSignals(True)
            self.pen_mode.toggle()
            self.pen_mode.blockSignals(False)
        if  self.line_mode.isChecked() != (mode == C.INTERACTIVE_MODE_LINE):
            self.line_mode.blockSignals(True)
            self.line_mode.toggle()
            self.line_mode.blockSignals(False)
        if  self.multi_line_mode.isChecked() != (mode == C.INTERACTIVE_MODE_MULTI_LINE):
            self.multi_line_mode.blockSignals(True)
            self.multi_line_mode.toggle()
            self.multi_line_mode.blockSignals(False)
        if self.__airbrush_mode.isChecked() != (mode == C.INTERACTIVE_MODE_AIRBRUSH):
            self.__airbrush_mode.blockSignals(True)
            self.__airbrush_mode.toggle()
            self.__airbrush_mode.blockSignals(False)
        if self.__text_mode.isChecked() != (mode == C.INTERACTIVE_MODE_TEXT):
            self.__text_mode.blockSignals(True)
            self.__text_mode.toggle()
            self.__text_mode.blockSignals(False)
        if self.hard_eraser_mode.isChecked() != (mode == C.INTERACTIVE_MODE_HARD_ERASER):
            self.hard_eraser_mode.blockSignals(True)
            self.hard_eraser_mode.toggle()
            self.hard_eraser_mode.blockSignals(False)
        if self.__soft_eraser_mode.isChecked() != (mode == C.INTERACTIVE_MODE_SOFT_ERASER):
            self.__soft_eraser_mode.blockSignals(True)
            self.__soft_eraser_mode.toggle()
            self.__soft_eraser_mode.blockSignals(False)
        if self.__move_mode.isChecked() != (mode == C.INTERACTIVE_MODE_MOVE):
            self.__move_mode.blockSignals(True)
            self.__move_mode.toggle()
            self.__move_mode.blockSignals(False)
        if self.transform_mode.isChecked() != (mode == C.INTERACTIVE_MODE_TRANSFORM):
            self.transform_mode.blockSignals(True)
            self.transform_mode.toggle()
            self.transform_mode.blockSignals(False)
        if self.dynamic_transform_mode.isChecked() != (mode == C.INTERACTIVE_MODE_DYNAMIC_TRANSFORM):
            self.dynamic_transform_mode.blockSignals(True)
            self.dynamic_transform_mode.toggle()
            self.dynamic_transform_mode.blockSignals(False)
