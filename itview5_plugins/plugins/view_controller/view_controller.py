from PySide2 import QtCore, QtGui, QtWidgets
from view_controller.actions import Actions
import math


# Use to quantize float zoom level to nearest power-of-two
_FLT_MIN = 0.0000001
def _round_up_pow2(f):
    """
    Helper function to calculate closest power of 2 if f is rounded up
    :param f: value to round up
    :type f: float
    :return: rounded up to power of 2. If overflow happens, return f
    :rtype: float
    """
    try:
        return 2.0 ** math.ceil(math.log(f) / math.log(2) + _FLT_MIN)
    except OverflowError:
        return f


def _round_down_pow2(f):
    """
    Helper function to calculate closest power of 2 if f is rounded down
    :param f: value to round down
    :type f: float
    :return: rounded down to power of 2. If overflow happens, return f
    :rtype: float
    """
    try:
        return 2.0 ** math.floor(math.log(f) / math.log(2) - _FLT_MIN)
    except OverflowError:
        return f

INTERACTIVE_MODE = "interactive_mode"
INTERACTIVE_MODE_MOVE = "move"
INTERACTIVE_MODE_TRANSFORM = "transform"
INTERACTIVE_MODE_DYNAMIC_TRANSFORM = "dynamic_transform"


class ViewController(QtCore.QObject):
    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window
        self.__cmd_line_args = itview.cmd_line_args
        self.__plugin_manager_controller = itview.plugin_manager_controller

        self.__viewport_api = self.__rpa.viewport_api
        self.__session_api = self.__rpa.session_api
        self.__color_api = self.__rpa.color_api

        self.__mousewheel_mins = [0, 0]

        self.__core_view = self.__main_window.get_core_view()
        self.__core_view.installEventFilter(self)

        self.__actions = Actions()
        self.__connect_signals()
        self.__create_menu_bar()

        self.__panning_in_progress = False
        self.__interactive_mode = self.__rpa.session_api.get_custom_session_attr(INTERACTIVE_MODE)
        dm = self.__session_api.delegate_mngr
        dm.add_post_delegate(self.__session_api.set_custom_session_attr, self.__update_interactive_mode)

        self.__actions.reset_viewer.setProperty("hotkey_editor", True)
        self.__actions.fullscreen.setProperty("hotkey_editor", True)
        self.__actions.fit_to_window.setProperty("hotkey_editor", True)
        self.__actions.fit_to_width.setProperty("hotkey_editor", True)
        self.__actions.fit_to_height.setProperty("hotkey_editor", True)
        self.__actions.zoom_in.setProperty("hotkey_editor", True)
        self.__actions.zoom_out.setProperty("hotkey_editor", True)
        self.__actions.flip_x.setProperty("hotkey_editor", True)
        self.__actions.flip_y.setProperty("hotkey_editor", True)
        self.__actions.toggle_presentation_mode.setProperty("hotkey_editor", True)

        self.__main_window.SIG_INITIALIZED.connect(self.__post_init)

        dm = self.__viewport_api.delegate_mngr
        dm.add_post_delegate(self.__viewport_api.flip_x, self.__flip_x)
        dm.add_post_delegate(self.__viewport_api.flip_y, self.__flip_y)

    def __connect_signals(self):
        self.__actions.fullscreen.triggered.connect(lambda state:
                                                    self.toggle_fullscreen(state))
        self.__actions.fit_to_window.triggered.connect(lambda state:
                                                       self.__viewport_api.fit_to_window(state))
        self.__actions.fit_to_width.triggered.connect(lambda state:
                                                       self.__viewport_api.fit_to_width(state))
        self.__actions.fit_to_height.triggered.connect(lambda state:
                                                       self.__viewport_api.fit_to_height(state))

        self.__actions.zoom_in.triggered.connect(lambda:
                                                 self.__zoom_in())
        self.__actions.zoom_out.triggered.connect(lambda:
                                                  self.__zoom_out())
        self.__actions.flip_x.triggered.connect(lambda state:
                                                self.__viewport_api.flip_x(state))
        self.__actions.flip_y.triggered.connect(lambda state:
                                                self.__viewport_api.flip_y(state))
        self.__actions.reset_viewer.triggered.connect(self.__reset_viewer)

        self.__actions.toggle_presentation_mode.triggered.connect(
            self.__toggle_presentation_mode)

        def __set_zoom_mode(mode):
            return lambda: self.__viewport_api.set_scale(float(mode))

        for mode, action in self.__actions.zoom_modes.items():
            action.triggered.connect(__set_zoom_mode(mode))

    def __create_menu_bar(self):
        plugins_menu = self.__main_window.get_plugins_menu()
        view_control = plugins_menu.addMenu("View Controls")
        view_control.setTearOffEnabled(True)

        view_control.addAction(self.__actions.reset_viewer)
        view_control.addAction(self.__actions.fullscreen)

        fit_to_actions = [self.__actions.fit_to_window,
                          self.__actions.fit_to_width,
                          self.__actions.fit_to_height]
        for action in fit_to_actions:
            view_control.addAction(action)

        view_control.addSeparator()
        view_control.addAction(self.__actions.flip_x)
        view_control.addAction(self.__actions.flip_y)
        view_control.addSeparator()
        view_control.addAction(self.__actions.zoom_in)
        view_control.addAction(self.__actions.zoom_out)
        view_control.addSeparator()

        zoom_modes = view_control.addMenu("Zoom Modes")
        for action in self.__actions.zoom_modes.values():
            zoom_modes.addAction(action)

        view_control.addSeparator()
        view_control.addAction(self.__actions.toggle_presentation_mode)

    def __reset_viewer(self):
        self.__color_api.set_fstop(0.0)
        self.__color_api.set_gamma(1.0)
        # Reset to Color(RGB)
        self.__color_api.set_channel(4)

        self.__actions.flip_x.setChecked(False)
        self.__actions.flip_y.setChecked(False)

        fit_mode = self.__actions.fit_modes_radio.checkedAction()
        if fit_mode is None:
            self.__viewport_api.set_scale(1)
            self.__viewport_api.set_translation(0, 0)
        else:
            fit_mode.setChecked(False)
            fit_mode.trigger()
        self.__viewport_api.display_msg("Viewer is reset")

    def __zoom_in(self):
        current_zoom = self.__viewport_api.get_scale()
        new_zoom = _round_up_pow2(current_zoom[0])
        self.__viewport_api.set_scale(new_zoom)

    def __zoom_out(self):
        current_zoom = self.__viewport_api.get_scale()
        new_zoom = _round_down_pow2(current_zoom[0])
        self.__viewport_api.set_scale(new_zoom)

    def __update_interactive_mode(self, out, attr_id, value):
        if attr_id == INTERACTIVE_MODE:
            self.__interactive_mode = value

    def toggle_fullscreen(self, state):
        self.__main_window.toggle_fullscreen()

    def eventFilter(self, obj, event):
        if not (
                event.type() == QtCore.QEvent.MouseButtonPress or \
                event.type() == QtCore.QEvent.MouseMove or \
                event.type() == QtCore.QEvent.MouseButtonRelease or \
                event.type() == QtCore.QEvent.Wheel):
            return False

        get_pos = lambda: (event.pos().x(), obj.height() - event.pos().y())

        if self.__interactive_mode in \
                    (INTERACTIVE_MODE_MOVE,
                     INTERACTIVE_MODE_DYNAMIC_TRANSFORM,
                     INTERACTIVE_MODE_TRANSFORM):
            return False

        if event.type() == QtCore.QEvent.Wheel:
            self.__geometry = self.__viewport_api.get_current_clip_geometry()

            zoom_point = get_pos()
            delta = event.delta()
            speed = 2.0  # multiple values for different zoom types (keyboard, mouse, gesture)

            if delta > 0:
                if self.__mousewheel_mins[0] == 0:
                    self.__mousewheel_mins[0] = delta
                elif self.__mousewheel_mins[0] > delta:
                    self.__mousewheel_mins[0] = delta
                delta = delta / self.__mousewheel_mins[0]
            elif delta < 0:
                if self.__mousewheel_mins[1] == 0:
                    self.__mousewheel_mins[1] = delta
                elif self.__mousewheel_mins[1] < delta:
                    self.__mousewheel_mins[1] = delta
                delta = -delta / self.__mousewheel_mins[1]

            self.__vertical_lock = False
            self.__horizontal_lock = False
            self.__viewport_api.scale_on_point(
                zoom_point, delta, speed,
                self.__horizontal_lock, self.__vertical_lock)

        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.MidButton and event.modifiers() == QtCore.Qt.NoModifier:
                self.__panning_in_progress = True
                self.__viewport_api.start_drag(get_pos())
        if self.__panning_in_progress and event.type() == QtCore.QEvent.MouseMove:
            self.__viewport_api.drag(get_pos())
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.MidButton and event.modifiers() == QtCore.Qt.NoModifier:
                self.__panning_in_progress = False
                self.__viewport_api.end_drag()

        return False

    def __toggle_presentation_mode(self):
        self.__viewport_api.toggle_presentation_mode()

    def __post_init(self):
        pass
        # if self.__cmd_line_args.fullscreen:
        #     self.__actions.fullscreen.setChecked(True)
        #     self.toggle_fullscreen(True)

        # if self.__cmd_line_args.zoom is not None:
        #     scale = float(self.__cmd_line_args.zoom[0])
        #     self.__viewport_api.set_scale(scale)

    def add_cmd_line_args(self, parser):
        group = parser.add_argument_group("View Controls")
        group.add_argument(
            '--fs', '--fullscreen',
            action='store_true',
            dest='fullscreen',
            help='Start up in Fullscreen mode'
        )
        group.add_argument(
            '--z', '--zoom',
            action='store',
            metavar='SCALE',
            type=float,
            nargs=1,
            dest='zoom',
            help='Zoom in/out viewport to a factor of SCALE'
        )

    def __flip_x(self, out, state):
        self.__actions.flip_x.setChecked(state)

    def __flip_y(self, out, state):
        self.__actions.flip_y.setChecked(state)
