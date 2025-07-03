import os
from PySide2 import QtCore, QtWidgets
from rv import rvtypes
import rv.qtutils
import platform
import logging
import types
from logging.handlers import RotatingFileHandler
from rpa.rpa import Rpa
from rpa.widgets.session_manager.session_manager import SessionManager
from rpa.widgets.session_assistant.session_assistant import SessionAssistant
from rpa.widgets.timeline.timeline import TimelineController
from rpa.widgets.annotation.annotation import Annotation
from rpa.widgets.interactive_modes.interactive_modes import InteractiveModes
from rpa.widgets.color_corrector.controller import Controller as ColorCorrectorController
from rpa.widgets.background_modes.background_modes import BackgroundModes
from rpa.widgets.rpa_interpreter.rpa_interpreter import RpaInterpreter
from rpa.widgets.session_io.session_io import SessionIO
from rpa.widgets.media_path_overlay.media_path_overlay import MediaPathOverlay

from rpa.widgets.test_widgets.test_session_api import TestSessionApi
from rpa.widgets.test_widgets.test_timeline_api import TestTimelineApi
from rpa.widgets.test_widgets.test_viewport_api import TestViewportApi
from rpa.widgets.test_widgets.test_annotation_api import TestAnnotationApi
from rpa.widgets.test_widgets.test_color_api import TestColorApi
from rpa.widgets.test_widgets.test_delegate_mngr import TestDelegateMngr
from rpa.utils import default_connection_maker

def get_core_view(self):
    return self._core_view

class RpaWidgetsMode(QtCore.QObject, rvtypes.MinorMode):

    def __init__(self):

        QtCore.QObject.__init__(self)
        rvtypes.MinorMode.__init__(self)

        self.__main_window = rv.qtutils.sessionWindow()
        app = QtWidgets.QApplication.instance()
        self.__rpa_core = app.rpa_core

        self.__rpa = Rpa(create_config(self.__main_window), create_logger())
        default_connection_maker.set_core_delegates_for_all_rpa(
            self.__rpa, self.__rpa_core)

        self.__rpa.session_api.get_attrs_metadata()

        self.__viewport_widget = self.__main_window.findChild(
            QtWidgets.QWidget, "no session")
        self.__rpa_core.viewport_api._set_viewport_widget(self.__viewport_widget)
        self.__main_window._core_view = self.__viewport_widget
        self.__main_window.get_core_view = types.MethodType(get_core_view, self.__main_window)

        self.__session_manager_dock = None
        self.__session_assistant_dock = None
        self.__timeline_toolbar = None
        self.__annotation = None
        self.__interactive_modes = None
        self.__color_corrector_dock = None
        self.__background_modes_dock = None
        self.__rpa_interpreter_dock = None
        self.__media_path_overlay_dock = None
        self.__session_io_dock = None

        self.__test_session_api_dock = None
        self.__test_timeline_api_dock = None
        self.__test_viewport_api_dock = None
        self.__test_annotation_api_dock = None
        self.__test_color_api_dock = None
        self.__test_delegate_manager_dock = None

        self.init("RpaMode", None, None,
            menu=[("Rpa", [
                ("Rpa Interpreter", self.__show_rpa_interpreter, "shift+ctrl+1", None),
                ("Session IO", self.__show_session_io, None, None),
                ("Session Manager", self.__show_session_manager, "shift+2", None),
                ("Session Assistant", self.__show_session_assistant, "shift+3", None),
                ("Timeline", self.__show_timeline, "shift+4", None),
                ("Annotation", self.__show_annotation, "shift+5", None),
                ("Interactive Modes", self.__show_interactive_modes, "shift+6", None),
                ("Color Corrector", self.__show_color_corrector, "shift+7", None),
                ("Background Modes", self.__show_background_modes, "shift+ctrl+8", None),
                ("Media Path Overlay", self.__show_media_path_overlay, None, None),
                ("RPA Tests", [
                    ("Session Api", self.__show_test_session_api, None, None),
                    ("Timeline Api", self.__show_test_timeline_api, None, None),
                    ("Viewport Api", self.__show_test_viewport_api, None, None),
                    ("Annotation Api", self.__show_test_annotation_api, None, None),
                    ("Color Api", self.__show_test_color_api, None, None),
                    ("Delegate Manager", self.__show_test_delegate_manager, None, None)
                ])
            ])])

    def __show_session_manager(self, event):
        event.reject()
        if not self.__is_init_done(): return

        if self.__session_manager_dock:
            self.__toggle_dock_visibility(self.__session_manager_dock)
            return

        self.__session_manager = SessionManager(self.__rpa, self.__main_window)
        self.__session_manager_dock = DockWidget(
            "Rpa Session Manager", self.__main_window)
        self.__session_manager_dock.setWidget(self.__session_manager.view)
        self.__main_window.addDockWidget(
            QtCore.Qt.BottomDockWidgetArea, self.__session_manager_dock)
        self.__session_manager_dock.show()

    def __show_session_assistant(self, event):
        event.reject()
        if not self.__is_init_done(): return

        if self.__session_assistant_dock:
            self.__toggle_dock_visibility(self.__session_assistant_dock)
            return

        self.__session_assistant = SessionAssistant(self.__rpa, self.__main_window)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        for action in self.__session_assistant.actions:
            button = QtWidgets.QPushButton(action.text())
            button.clicked.connect(action.trigger)
            layout.addWidget(button)
        widget.setLayout(layout)
        self.__session_assistant_dock = DockWidget(
            "Session Assistant", self.__main_window)
        self.__session_assistant_dock.setWidget(widget)
        self.__main_window.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, self.__session_assistant_dock)
        self.__session_assistant_dock.show()

    def __show_timeline(self, event):
        event.reject()
        if self.__timeline_toolbar:
            if self.__timeline_toolbar.isVisible(): self.__timeline_toolbar.set_visible(False)
            else: self.__timeline_toolbar.set_visible(True)
            return
        self.__timeline_toolbar = TimelineController(self.__rpa, self.__main_window)

    def __show_annotation(self, event):
        event.reject()
        if self.__annotation:
            if self.__annotation.tool_bar.isVisible():
                self.__annotation.tool_bar.hide()
            else:
                self.__annotation.tool_bar.show()
            return
        self.__annotation = Annotation(self.__rpa, self.__main_window)

    def __show_interactive_modes(self, event):
        event.reject()
        if self.__interactive_modes:
            if self.__interactive_modes.tool_bar.isVisible():
                self.__interactive_modes.tool_bar.hide()
            else:
                self.__interactive_modes.tool_bar.show()
            return
        self.__interactive_modes = InteractiveModes(self.__rpa, self.__main_window)

    def __show_color_corrector(self, event):
        event.reject()
        if not self.__is_init_done(): return

        if self.__color_corrector_dock:
            self.__toggle_dock_visibility(self.__color_corrector_dock)
            return

        self.__color_corrector = ColorCorrectorController(self.__rpa, self.__main_window)
        self.__color_corrector_dock = DockWidget(
            "Color Corrector", self.__main_window)
        self.__color_corrector_dock.setWidget(self.__color_corrector.view)
        self.__main_window.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, self.__color_corrector_dock)
        self.__color_corrector_dock.show()

    def __show_background_modes(self, event):
        event.reject()
        if not self.__is_init_done(): return

        if self.__background_modes_dock:
            self.__toggle_dock_visibility(self.__background_modes_dock)
            return

        self.__background_modes = BackgroundModes(self.__rpa, self.__main_window)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        for action in [
            self.__background_modes.actions.turn_off_background,            
            self.__background_modes.actions.wipe,
            self.__background_modes.actions.side_by_side,
            self.__background_modes.actions.top_to_bottom,
            self.__background_modes.actions.pip,
            self.__background_modes.actions.swap_background
        ]:
            button = QtWidgets.QPushButton(action.text())
            button.clicked.connect(action.trigger)
            layout.addWidget(button)
        widget.setLayout(layout)
        self.__background_modes_dock = DockWidget(
            "Background Modes", self.__main_window)
        self.__background_modes_dock.setWidget(widget)
        self.__main_window.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, self.__background_modes_dock)
        self.__background_modes_dock.show()

    def __show_media_path_overlay(self, event):
        event.reject()
        if not self.__is_init_done(): return

        if self.__media_path_overlay_dock:
            self.__toggle_dock_visibility(self.__media_path_overlay_dock)
            return

        self.__media_path_overlay = \
            MediaPathOverlay(self.__rpa, self.__main_window)

        self.__media_path_overlay_dock = \
            DockWidget("Media Path Overlay", self.__main_window)
        self.__media_path_overlay_dock.setWidget(self.__media_path_overlay)
        self.__main_window.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, self.__media_path_overlay_dock)
        self.__media_path_overlay_dock.show()

    def __show_rpa_interpreter(self, event):
        event.reject()
        if not self.__is_init_done(): return

        if self.__rpa_interpreter_dock:
            self.__toggle_dock_visibility(self.__rpa_interpreter_dock)
            return

        self.__rpa_interpreter = RpaInterpreter(self.__rpa, self.__main_window)

        self.__rpa_interpreter_dock = \
            DockWidget("Rpa Interpreter", self.__main_window)
        self.__rpa_interpreter_dock.setWidget(self.__rpa_interpreter)
        self.__main_window.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, self.__rpa_interpreter_dock)
        self.__rpa_interpreter_dock.show()

    def __show_session_io(self, event):
        event.reject()
        if not self.__is_init_done(): return

        if self.__session_io_dock:
            self.__toggle_dock_visibility(self.__session_io_dock)
            return

        self.__session_io = SessionIO(self.__rpa, self.__main_window)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        for action in self.__session_io.actions:
            button = QtWidgets.QPushButton(action.text())
            button.clicked.connect(action.trigger)
            layout.addWidget(button)
        widget.setLayout(layout)
        self.__session_io_dock = DockWidget("Session IO", self.__main_window)
        self.__session_io_dock.setWidget(widget)
        self.__main_window.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, self.__session_io_dock)
        self.__session_io_dock.show()

    def __show_test_session_api(self, event):
        event.reject()
        if not self.__is_init_done(): return
        if self.__test_session_api_dock:
            self.__toggle_dock_visibility(self.__test_session_api_dock)
            return

        self.__test_session_api = TestSessionApi(self.__rpa, self.__main_window)
        self.__test_session_api_dock = DockWidget(
            "Session Api Test", self.__main_window)
        self.__test_session_api_dock.setWidget(self.__test_session_api.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__test_session_api_dock)
        self.__test_session_api_dock.show()
        return False

    def __show_test_timeline_api(self, event):
        event.reject()
        if not self.__is_init_done(): return
        if self.__test_timeline_api_dock:
            self.__toggle_dock_visibility(self.__test_timeline_api_dock)
            return

        self.__test_timeline_api = TestTimelineApi(self.__rpa, self.__main_window)
        self.__test_timeline_api_dock = DockWidget(
            "Timeline Api Test", self.__main_window)
        self.__test_timeline_api_dock.setWidget(self.__test_timeline_api.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__test_timeline_api_dock)
        self.__test_timeline_api_dock.show()
        return False

    def __show_test_viewport_api(self, event):
        event.reject()
        if not self.__is_init_done(): return
        if self.__test_viewport_api_dock:
            self.__toggle_dock_visibility(self.__test_viewport_api_dock)
            return

        self.__test_viewport_api = TestViewportApi(self.__rpa, self.__main_window)
        self.__test_viewport_api_dock = DockWidget(
            "Viewport Api Test", self.__main_window)
        self.__test_viewport_api_dock.setWidget(self.__test_viewport_api.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__test_viewport_api_dock)
        self.__test_viewport_api_dock.show()
        return False

    def __show_test_annotation_api(self, event):
        event.reject()
        if not self.__is_init_done(): return
        if self.__test_annotation_api_dock:
            self.__toggle_dock_visibility(self.__test_annotation_api_dock)
            return

        self.__test_annotation_api = TestAnnotationApi(self.__rpa, self.__main_window)
        self.__test_annotation_api_dock = DockWidget(
            "Annotation Api Test", self.__main_window)
        self.__test_annotation_api_dock.setWidget(self.__test_annotation_api.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__test_annotation_api_dock)
        self.__test_annotation_api_dock.show()
        return False

    def __show_test_color_api(self, event):
        event.reject()
        if not self.__is_init_done(): return
        if self.__test_color_api_dock:
            self.__toggle_dock_visibility(self.__test_color_api_dock)
            return

        self.__test_color_api = TestColorApi(self.__rpa, self.__main_window)
        self.__test_color_api_dock = DockWidget(
            "Color Api Test", self.__main_window)
        self.__test_color_api_dock.setWidget(self.__test_color_api.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__test_color_api_dock)
        self.__test_color_api_dock.show()
        return False

    def __show_test_delegate_manager(self, event):
        event.reject()
        if not self.__is_init_done(): return
        if self.__test_delegate_manager_dock:
            self.__toggle_dock_visibility(self.__test_delegate_manager_dock)
            return

        self.__test_delegate_manager = TestDelegateMngr(self.__rpa, self.__main_window)
        self.__test_delegate_manager_dock = DockWidget(
            "Delegate Manager Test", self.__main_window)
        self.__test_delegate_manager_dock.setWidget(self.__test_delegate_manager.view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__test_delegate_manager_dock)
        self.__test_delegate_manager_dock.show()
        return False

    def __is_init_done(self):
        if self.__main_window and self.__rpa: return True

        elif self.__main_window and self.__rpa is None:

            return True
        return False

    def __toggle_dock_visibility(self, dock):
        if dock.isVisible(): dock.hide()
        else: dock.show()


def create_config(main_window):
    config = QtCore.QSettings("imageworks.com", "itview_5", main_window)
    config.beginGroup("itview")
    return config


def create_logger():
    if platform.system() == 'Windows':
        log_dir = os.path.join(os.environ["APPDATA"], "itview")
    elif platform.system() == 'Linux':
        log_dir = os.path.join(os.environ["HOME"], ".itview")
    else:
        raise Exception("Unsupported platform!")

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_filepath = os.path.join(log_dir, "itview5.log")

    itview5_logger = logging.getLogger("Itview5")
    itview5_logger.setLevel(logging.DEBUG)
    if not itview5_logger.handlers:
        handler = RotatingFileHandler(
            log_filepath, mode="a", maxBytes= 10 * 1024 * 1024, backupCount=5)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(pathname)s %(funcName)s %(lineno)d:\n %(asctime)s %(levelname)s %(message)s\n",
            datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        itview5_logger.addHandler(handler)
        itview5_logger.propagate = False
    itview5_logger.info("[RPA] Itview5 Logger Created")
    return itview5_logger


class DockWidget(QtWidgets.QDockWidget):
    def __init__(self, title , parent):
        super().__init__(title, parent)
        self.setFeatures(
            QtWidgets.QDockWidget.DockWidgetClosable | \
            QtWidgets.QDockWidget.DockWidgetMovable)


def createMode():
    return RpaWidgetsMode()
