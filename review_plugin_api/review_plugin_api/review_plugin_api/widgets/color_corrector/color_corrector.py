from PySide2 import QtCore, QtGui, QtWidgets
from review_plugin_api.widgets.color_corrector.actions import Actions
from review_plugin_api.widgets.color_corrector.tool_bar import ToolBar
from review_plugin_api.widgets.color_corrector import svg
from review_plugin_api.widgets.color_corrector import constants as C
from review_plugin_api.widgets.color_corrector._color_corrector.controller \
    import Controller as ColorCorrectorController
from review_plugin_api.widgets.color_corrector._color_corrector.model \
    import RegionName


class ColorCorrector(QtCore.QObject):
    def __init__(self, review_plugin_api, main_window):
        super().__init__()
        self.__review_plugin_api = review_plugin_api
        self.__main_window = main_window
        self.__timeline_api = self.__review_plugin_api.timeline_api

        viewport_widget = self.__main_window.get_viewport_widget()
        viewport_widget.installEventFilter(self)
        self.__actions = Actions()
        self.__connect_signals()
        self.__create_tool_bar()

        self.__current_mask_mode = None
        self.__drawing_in_progress = False

    def toggle_show(self):
        if self.__color_corrector.is_visible():
            self.__color_corrector.hide()
            self.__tool_bar.hide()
        else:
            self.__color_corrector.show()
            self.__tool_bar.show()

    def __connect_signals(self):
        self.__actions.toggle_rectangle_mode.toggled.connect(
            lambda is_checked: \
                self.set_rectangle_mode() if is_checked else None)
        self.__actions.toggle_ellipse_mode.toggled.connect(
            lambda is_checked: \
                self.set_ellipse_mode() if is_checked else None)
        self.__actions.toggle_lasso_mode.toggled.connect(
            lambda is_checked: \
                self.set_lasso_mode() if is_checked else None)

        self.__color_corrector = \
            ColorCorrectorController(self.__review_plugin_api, self.__main_window)
        self.__actions.color_corrector.triggered.connect(
            lambda: self.__color_corrector.show())
        self.__color_corrector.show()

    def eventFilter(self, obj, event):
        if not (
        event.type() == QtCore.QEvent.MouseButtonPress or \
        event.type() == QtCore.QEvent.MouseMove or \
        event.type() == QtCore.QEvent.MouseButtonRelease):
            return False
        if self.__timeline_api.is_empty():
            return False
        get_pos = lambda: (event.pos().x(), obj.height() - event.pos().y())
        if self.__current_mask_mode and (self.is_rectangle_mode() or \
        self.is_ellipse_mode() or self.is_lasso_mode()):
            if event.type() == QtCore.QEvent.MouseButtonPress:
                self.__drawing_in_progress = True
                self.__color_corrector.new_shape(*get_pos(), self.__current_mask_mode)
            if self.__drawing_in_progress and event.type() == QtCore.QEvent.MouseMove:
                self.__color_corrector.append_to_shape(*get_pos(), self.__current_mask_mode)
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                self.__color_corrector.finish_shape(*get_pos(), self.__current_mask_mode)
                self.__drawing_in_progress = False

        return False

    def __create_tool_bar(self):
        self.__tool_bar = ToolBar(self.__actions)
        self.__main_window.addToolBarBreak(QtCore.Qt.BottomToolBarArea)
        self.__main_window.addToolBar(
            QtCore.Qt.RightToolBarArea, self.__tool_bar)

    def set_rectangle_mode(self):
        self.__current_mask_mode = RegionName.RECTANGLE

    def is_rectangle_mode(self):
        return self.__current_mask_mode == RegionName.RECTANGLE

    def set_ellipse_mode(self):
        self.__current_mask_mode = RegionName.ELLIPSE

    def is_ellipse_mode(self):
        return self.__current_mask_mode == RegionName.ELLIPSE

    def set_lasso_mode(self):
        self.__current_mask_mode = RegionName.LASSO

    def is_lasso_mode(self):
        return self.__current_mask_mode == RegionName.LASSO
