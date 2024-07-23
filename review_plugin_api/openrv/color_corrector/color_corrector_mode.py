from PySide2 import QtCore, QtWidgets
from rv import rvtypes
from mapper import Mapper
from review_plugin_api.widgets.color_corrector.color_corrector import ColorCorrector


def get_core_view(obj):
    return obj.__viewport_widget


class ColorCorrectorMode(QtCore.QObject, rvtypes.MinorMode):

    def __init__(self):
        QtCore.QObject.__init__(self)
        rvtypes.MinorMode.__init__(self)
        self.__color_corrector = None

        self.__main_window = None
        app = QtWidgets.QApplication.instance()
        app.installEventFilter(self)

        self.init(
            "ColorCorrectorMode",
            [], [],
            [
                ("ReviewPluginApi",
                [("Color Corrector", self.__toggle_color_corrector, "alt+c", None)])])

    def eventFilter(self, o, e):
        if self.__main_window is None and \
        isinstance(o, QtWidgets.QMainWindow):
            self.__main_window = o
            viewport_widget = self.__main_window.findChild(
                QtWidgets.QWidget, "no session")
            setattr(self.__main_window, "__viewport_widget", viewport_widget)
            setattr(
                self.__main_window, "get_viewport_widget",
                lambda: getattr(self.__main_window, "__viewport_widget"))
        return False

    def __toggle_color_corrector(self, event):
        if self.__color_corrector:
            self.__color_corrector.toggle_show()
        else:
            mapper = Mapper.get_instance()
            review_plugin_api = mapper.get_review_plugin_api()

            self.__color_corrector = ColorCorrector(
                review_plugin_api, self.__main_window)

            dock_widgets = self.__main_window.findChildren(
                QtWidgets.QDockWidget)
            for dock_widget in dock_widgets:
                if dock_widget.windowTitle() == "Draw":
                    draw_widget = dock_widget
                    break
            else:
                draw_widget = None


def createMode():
    return ColorCorrectorMode()
