import os
try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets
from rv import rvtypes, commands, runtime
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

        commands.setViewNode("defaultSequence")

        self.init("RpaMode", None, None,
            menu=[("RPA", [
                ("RPA Mode", self.__use_rpa_mode, None, None)
            ])])

    def __setup_rpa_session_mode(self):
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

        commands.deactivateMode("annotate_mode")
        commands.deactivateMode("session_manager")
        commands.clearSession()
        commands.setCursor(0)
        self.__rpa.session_api.clear()

        self.__session_io = SessionIO(self.__rpa, self.__main_window)
        self.__setup_rpa_menu(self.__main_window.menuBar())

        for toolbar in self.__main_window.findChildren(QtWidgets.QToolBar):
            if toolbar.objectName() in ["topToolBar", "bottomToolBar"]:
                toolbar.hide()

        for widget in self.__main_window.findChildren(QtWidgets.QWidget):
            if widget.objectName() == "session_manager":
                if widget.isVisible(): widget.hide()

        for widget in self.__main_window.findChildren(QtWidgets.QDockWidget):
            if widget.widget().objectName() == "annotationTool":
                if widget.isVisible(): widget.hide()

        commands.unbind("default", "global", 'key-down--control--S')
        commands.unbind("default", "global", 'key-down--control--s')
        commands.bind("default", "global", 'key-down--control--s', self._save_rpa_session, "Save RPA Session")

        commands.unbind("default", "global", 'key-down--control--o')
        commands.bind("default", "global", 'key-down--control--o', self._add_clips, "Add clips to FG playlist")

        commands.unbind("default", "global", 'mode-manager-toggle-mode')
        commands.unbind("default", "global", 'key-down--x')
        commands.bind("default", "global", 'key-down--x', self._show_session_manager, "Show/Hide RPA Session Manager")

        commands.unbind("default", "global", 'session-manager-load-ui')
        commands.unbind("default", "global", 'key-down--X')
        commands.bind("default", "global", 'key-down--X', self._show_session_manager, "Show/Hide RPA Session Manager")

        commands.unbind("default", "global", 'toggle-draw-panel')
        commands.bind("default", "global", 'toggle-draw-panel', self._show_annotation, "Show Annotation Tools")
        commands.unbind("default", "global", 'key-down--f10')
        commands.bind("default", "global", 'key-down--f10', self._show_annotation, "Show Annotation Tools")

        commands.unbind("default", "global", 'key-down--~')
        commands.unbind("default", "global", 'key-down--f2')
        commands.bind("default", "global", 'key-down--f2', self._show_timeline, "Show Timeline")

        app = QtWidgets.QApplication.instance()
        app.installEventFilter(self)
        self.__viewport_widget.installEventFilter(self)

        self.__session_manager_dock = None
        self.__session_assistant_dock = None
        self.__timeline_toolbar = None
        self.__annotation_dock = None
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

        self.__show_session_manager()
        self.__show_annotation()
        self.__hide_rv_timeline()
        self.__show_timeline()
        self.__show_color_corrector()

    def eventFilter(self, object, event):
        if isinstance(object, QtWidgets.QMenuBar) and \
        event.type() == QtCore.QEvent.Paint:
            self.__setup_rpa_menu(object)

        if isinstance(object, QtWidgets.QMenu) and \
        event.type() == QtCore.QEvent.Show:
            parent = object.parent()
            if parent is self.__main_window:
                self.__setup_rpa_menu(object)

        if isinstance(object, QtWidgets.QToolBar) and \
        object.objectName() in ["topToolBar", "bottomToolBar"]:
            object.hide()

        if isinstance(object, QtWidgets.QWidget) and \
        event.type() == QtCore.QEvent.Show:
            if object.objectName() == "session_manager":
                object.hide()

        if isinstance(object, QtWidgets.QDockWidget) and \
        event.type() == QtCore.QEvent.Show and \
        hasattr(object, "widget") and \
        object.widget().objectName() == "annotationTool":
            object.hide()

        if object is self.__viewport_widget:
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                self.__add_clips()
                return True
        return False

    def __setup_rpa_menu(self, menu):
        for action in menu.actions():
            if action and action.text() == "Control":
                sub_menu = action.menu()
                sub_actions =  sub_menu.actions()[:]
                for sub_action in sub_actions:
                    if sub_action.text() in [
                    "Next Marked Frame", "Prev Marked Frame",
                    "Matching Frame Of Next Source", "Matching Frame Of Previous Source"]:
                        sub_action.setShortcut("")
                        sub_menu.removeAction(sub_action)

            if action and action.text() == "Tools":
                sub_menu = action.menu()
                sub_actions =  sub_menu.actions()[:]
                for sub_action in sub_actions:
                    if sub_action.text() in [
                    "Default Views", "   Sequence", "   Replace", "   Over", "   Add",
                    "   Difference", "   Difference (Inverted)", "   Tile",
                    "Menu Bar", "Top View Toolbar", "Bottom View Toolbar",
                    "Session Manager", "Annotation", "Timeline"]:
                        sub_action.setShortcut("")
                        sub_menu.removeAction(sub_action)

            if action and action.text() == "Image":
                sub_menu = action.menu()
                sub_actions =  sub_menu.actions()[:]
                for sub_action in sub_actions:
                    if sub_action.text() in [
                    "Rotation", "Flip", "Flop",
                    "Cycle Stack Forward", "Cycle Stack Backward"]:
                        sub_action.setShortcut("")
                        sub_menu.removeAction(sub_action)

            if action and action.text() in [
            "File", "Edit", "RPA", "Annotation",
            "Sequence", "Stack", "Layout", ]:
                action_text = action.text()
                menu.removeAction(action)

                if action_text != "File": continue

                if "File(rpa)" not in [action.text() for action in menu.actions()]:
                    rpa_file_menu = QtWidgets.QMenu("File(rpa)", menu)

                    action = QtWidgets.QAction("Add Clips", parent=self.__main_window)
                    action.setShortcut("Ctrl+O")
                    action.triggered.connect(self.__add_clips)
                    rpa_file_menu.addAction(action)

                    action = QtWidgets.QAction("Save RPA Session            Ctrl+S", parent=self.__main_window)
                    action.triggered.connect(self.__save_rpa_session)
                    rpa_file_menu.addAction(action)

                    action = QtWidgets.QAction("Append RPA Session", parent=self.__main_window)
                    action.triggered.connect(self.__append_rpa_session)
                    rpa_file_menu.addAction(action)

                    action = QtWidgets.QAction("Replace RPA Session", parent=self.__main_window)
                    action.triggered.connect(self.__replace_rpa_session)
                    rpa_file_menu.addAction(action)

                    action_to_insert_before = menu.actions()[1]
                    menu.insertMenu(action_to_insert_before, rpa_file_menu)

                if "Widgets(rpa)" not in [action.text() for action in menu.actions()]:
                    rpa_file_menu = QtWidgets.QMenu("Widgets(rpa)", menu)

                    action = QtWidgets.QAction("Session Manager            X", parent=self.__main_window)
                    action.setShortcutContext(QtCore.Qt.ApplicationShortcut)
                    action.triggered.connect(self.__show_session_manager)
                    rpa_file_menu.addAction(action)

                    action = QtWidgets.QAction("Background Modes", parent=self.__main_window)
                    action.triggered.connect(self.__show_background_modes)
                    rpa_file_menu.addAction(action)

                    action = QtWidgets.QAction("Annotation Tools", parent=self.__main_window)
                    action.triggered.connect(self.__show_annotation)
                    action.setShortcut("F10")
                    rpa_file_menu.addAction(action)

                    action = QtWidgets.QAction("Color Corrector", parent=self.__main_window)
                    action.triggered.connect(self.__show_color_corrector)
                    rpa_file_menu.addAction(action)

                    action = QtWidgets.QAction("Timeline            F2", parent=self.__main_window)
                    action.triggered.connect(self.__show_timeline)
                    rpa_file_menu.addAction(action)

                    action = QtWidgets.QAction("Media Path Overlay", parent=self.__main_window)
                    action.triggered.connect(self.__show_media_path_overlay)
                    rpa_file_menu.addAction(action)

                    action = QtWidgets.QAction("Session Assistant", parent=self.__main_window)
                    action.triggered.connect(self.__show_session_assistant)
                    rpa_file_menu.addAction(action)

                    action = QtWidgets.QAction("RPA Interpreter", parent=self.__main_window)
                    action.triggered.connect(self.__show_rpa_interpreter)
                    rpa_file_menu.addAction(action)

                    # action = QtWidgets.QAction("Test Session API", parent=self.__main_window)
                    # action.triggered.connect(self.__show_test_session_api)
                    # rpa_file_menu.addAction(action)

                    # action = QtWidgets.QAction("Test Timeline API", parent=self.__main_window)
                    # action.triggered.connect(self.__show_test_timeline_api)
                    # rpa_file_menu.addAction(action)

                    # action = QtWidgets.QAction("Test Annotation API", parent=self.__main_window)
                    # action.triggered.connect(self.__show_test_annotation_api)
                    # rpa_file_menu.addAction(action)

                    # action = QtWidgets.QAction("Test Color API", parent=self.__main_window)
                    # action.triggered.connect(self.__show_test_color_api)
                    # rpa_file_menu.addAction(action)

                    # action = QtWidgets.QAction("Test Viewport API", parent=self.__main_window)
                    # action.triggered.connect(self.__show_test_viewport_api)
                    # rpa_file_menu.addAction(action)

                    # action = QtWidgets.QAction("Test Delegate Manager", parent=self.__main_window)
                    # action.triggered.connect(self.__show_test_delegate_manager)
                    # rpa_file_menu.addAction(action)

                    action_to_insert_before = menu.actions()[2]
                    menu.insertMenu(action_to_insert_before, rpa_file_menu)

        if menu is self.__main_window.menuBar():
            openrv_action = menu.actions()[0]
            openrv_action.setText("RPA Session - Open RV")

    def __use_rpa_mode(self, event):        
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.setWindowTitle("Warning")
        msg_box.setText(
            "You are about to use an <b><u>Experimental</u> RPA Session</b> instead of RV Session in RV!<br><br><br>"\
            "When you enter RPA mode the following happens,<br><br>"\
            "1) Your current <span style='color:red'>RV Session will be cleared</span>.<br><br>"\
            "2) Many <span style='color:red'>RV features/widgets will be replaced/disabled</span> to accomodate RPA Session.<br><br><br>"\
            "Kindly <u>save your RV Session if needed</u> before proceeding!<br><br><br>"\
            "Are you sure you want enter RPA Mode ?"
        )
        msg_box.setStandardButtons(
            QtWidgets.QMessageBox.Ok|QtWidgets.QMessageBox.No)
        result = msg_box.exec_()
        if result == QtWidgets.QMessageBox.Ok:
            self.__setup_rpa_session_mode()

    def _save_rpa_session(self, event):        
        self.__save_rpa_session()

    def __save_rpa_session(self):
        self.__session_io.save_session_action.trigger()

    def __append_rpa_session(self):
        self.__session_io.append_session_action.trigger()

    def __replace_rpa_session(self):
        self.__session_io.replace_session_action.trigger()

    def _add_clips(self, event):        
        self.__add_clips()

    def __add_clips(self):
        paths, what = QtWidgets.QFileDialog.getOpenFileNames(
            self.__main_window,
            "Open Media",
            "",
            "",
            options=QtWidgets.QFileDialog.DontUseNativeDialog)
        if len(paths) == 0:
            return
        fg_playlist = self.__rpa.session_api.get_fg_playlist()
        selected_clips = \
            self.__rpa.session_api.get_active_clips(fg_playlist)
        if len(selected_clips) == 0:
            self.__rpa.session_api.create_clips(fg_playlist, paths)
        else:
            last_selected_clip = selected_clips[-1]
            clips = self.__rpa.session_api.get_clips(fg_playlist)
            index = clips.index(last_selected_clip) + 1
            self.__rpa.session_api.create_clips(fg_playlist, paths, index)

    def _show_session_manager(self, event):        
        self.__show_session_manager()

    def __show_session_manager(self):
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

    def __show_session_assistant(self):
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

    def _show_timeline(self, event):        
        self.__show_timeline()

    def __hide_rv_timeline(self):
        is_timeline_shown = runtime.eval(
            "use rvui;"
            "rvui.timelineShown();",[])
        if is_timeline_shown == "2":
            runtime.eval(
                "use rvui;"
                "rvui.toggleTimeline();",[])

    def __show_timeline(self):
        if self.__timeline_toolbar:
            self.__hide_rv_timeline()
            if self.__timeline_toolbar.isVisible():
                self.__timeline_toolbar.set_visible(False)
            else:
                self.__timeline_toolbar.set_visible(True)
            return
        self.__timeline_toolbar = TimelineController(self.__rpa, self.__main_window)

    def _show_annotation(self, event):        
        self.__show_annotation()

    def __show_annotation(self):
        if not self.__is_init_done(): return

        if self.__annotation_dock:
            self.__toggle_dock_visibility(self.__annotation_dock)
            return

        annotation = Annotation(self.__rpa, self.__main_window)
        annotation.tool_bar.setOrientation(QtCore.Qt.Vertical)
        interactive_modes = InteractiveModes(self.__rpa, self.__main_window)
        interactive_modes.tool_bar.setOrientation(QtCore.Qt.Vertical)
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(annotation.tool_bar)
        layout.addWidget(interactive_modes.tool_bar)
        widget.setLayout(layout)

        self.__annotation_dock = DockWidget(
            "Annotation Tools", self.__main_window)
        self.__annotation_dock.setWidget(widget)
        self.__main_window.addDockWidget(
            QtCore.Qt.LeftDockWidgetArea, self.__annotation_dock)
        self.__annotation_dock.show()

    def __show_color_corrector(self):
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

    def __show_background_modes(self):
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

        mix_modes_sep = QtWidgets.QLabel("Mix Modes")
        layout.addWidget(mix_modes_sep)
        for action in [
            self.__background_modes.actions.none_mix_mode,
            self.__background_modes.actions.add_mix_mode,
            self.__background_modes.actions.diff_mix_mode,
            self.__background_modes.actions.sub_mix_mode,
            self.__background_modes.actions.over_mix_mode,
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

    def __show_media_path_overlay(self,):
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

    def __show_rpa_interpreter(self):
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

    def __show_test_session_api(self):
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

    def __show_test_timeline_api(self):
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

    def __show_test_viewport_api(self):
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

    def __show_test_annotation_api(self):
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

    def __show_test_color_api(self):
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

    def __show_test_delegate_manager(self):
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
    elif platform.system() == 'Linux' or platform.system() == 'Darwin':
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
