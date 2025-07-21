import math

try:
    from PySide2 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide6 import QtGui, QtCore, QtWidgets

from rpa.widgets.image_controller.actions import Actions
from rpa.widgets.image_controller import constants as C
from rpa.widgets.image_controller.slider_toolbar import SliderToolBar


class ImageController(QtCore.QObject):
    def __init__(self, rpa, main_window):
        self.__rpa = rpa
        self.__main_window = main_window

        self.__session_api = self.__rpa.session_api
        self.__viewport_api = self.__rpa.viewport_api
        self.__color_api = self.__rpa.color_api

        self.__current_fstop_val = self.__color_api.get_fstop()
        self.__current_gamma_val = self.__color_api.get_gamma()
        self.__current_rotation_val = self.__viewport_api.get_rotation()

        self.actions = Actions()
        self.__create_tool_bar()
        self.__connect_signals()

    def __connect_signals(self):
        self.__color_api.delegate_mngr.add_post_delegate(
            self.__color_api.set_fstop, self.__post_set_fstop)
        self.__color_api.delegate_mngr.add_post_delegate(
            self.__color_api.set_gamma, self.__post_set_gamma)
        self.__viewport_api.delegate_mngr.add_post_delegate(
            self.__viewport_api.set_rotation, self.__post_set_rotation)

        # FStop
        self.actions.fstop_up.triggered.connect(self.__fstop_up)
        self.actions.fstop_down.triggered.connect(self.__fstop_down)
        self.actions.fstop_reset.triggered.connect(self.__fstop_reset)
        self.actions.fstop_pgup.triggered.connect(self.__fstop_pgup)
        self.actions.fstop_pgdown.triggered.connect(self.__fstop_pgdown)
        self.actions.fstop_slider.triggered.connect(lambda state:self.__toggle_fstop_slider(state))
        self.fstop_slider.SIG_SLIDER_VALUE_CHANGED.connect(self.__set_fstop_value)
        self.fstop_slider.SIG_RESET.connect(self.__fstop_reset)
        self.fstop_slider.SIG_TOOLBAR_VISIBLE.connect(self.__set_fstop_visibility)

        # Gamma
        self.actions.gamma_up.triggered.connect(self.__gamma_up)
        self.actions.gamma_down.triggered.connect(self.__gamma_down)
        self.actions.gamma_reset.triggered.connect(self.__gamma_reset)
        self.actions.gamma_slider.triggered.connect(lambda state:self.__toggle_gamma_slider(state))
        self.gamma_slider.SIG_SLIDER_VALUE_CHANGED.connect(self.__set_gamma_value)
        self.gamma_slider.SIG_RESET.connect(self.__gamma_reset)
        self.gamma_slider.SIG_TOOLBAR_VISIBLE.connect(self.__set_gamma_visibility)

        # Image Rotation
        self.actions.rotation_reset.triggered.connect(lambda: self.__update_rotation(0))
        self.actions.rotate_90.triggered.connect(lambda: self.__update_rotation(90))
        self.actions.rotate_180.triggered.connect(lambda: self.__update_rotation(180))
        self.actions.rotate_270.triggered.connect(lambda: self.__update_rotation(270))
        self.actions.rotate_up_10.triggered.connect(lambda: self.__update_rotation(self.__current_rotation_val + 10))
        self.actions.rotate_down_10.triggered.connect(lambda: self.__update_rotation(self.__current_rotation_val - 10))
        self.actions.rotation_slider.triggered.connect(lambda state:self.__toggle_image_rot_slider(state))
        self.image_rot_slider.SIG_SLIDER_VALUE_CHANGED.connect(self.__set_image_rot_value)
        self.image_rot_slider.SIG_RESET.connect(lambda: self.__update_rotation(0))
        self.image_rot_slider.SIG_TOOLBAR_VISIBLE.connect(self.__set_image_rot_visibility)

    def __create_tool_bar(self):
        self.fstop_slider = SliderToolBar(
                                    "FStop Control", "F-Stop",
                                    min_val=-10,
                                    max_val=10,
                                    value=0,
                                    interval=0.5)
        self.__main_window.addToolBar(
                QtCore.Qt.BottomToolBarArea, self.fstop_slider)
        self.fstop_slider.set_slider_value(self.__current_fstop_val)
        self.gamma_slider = SliderToolBar(
                                    "Gamma Control", "Gamma ",
                                    min_val=0,
                                    max_val=4,
                                    value=1,
                                    interval=0.1)
        self.__main_window.addToolBar(
                QtCore.Qt.BottomToolBarArea, self.gamma_slider)
        self.gamma_slider.set_slider_value(self.__current_gamma_val)

        self.image_rot_slider = SliderToolBar(
                                    "Image Rotation", "Rotation",
                                    min_val=-360,
                                    max_val=360,
                                    value=0,
                                    interval=90)
        self.__main_window.addToolBar(
                QtCore.Qt.BottomToolBarArea, self.image_rot_slider)
        self.gamma_slider.set_slider_value(self.__current_rotation_val)

    # FStop controls
    def __set_fstop_visibility(self):
        is_visible = self.fstop_slider.isVisible()
        self.actions.fstop_slider.setChecked(is_visible)
        self.__toggle_fstop_slider(is_visible)

    def __toggle_fstop_slider(self, state):
        if state:
            self.fstop_slider.show()
        else:
            self.fstop_slider.hide()

    def __set_fstop_value(self, value):
        if value is None: return
        self.__current_fstop_val = value
        self.__color_api.set_fstop(value)

    def __fstop_up(self):
        self.__current_fstop_val = self.__current_fstop_val + C.FSTOP_UP
        self.__color_api.set_fstop(self.__current_fstop_val)

    def __fstop_down(self):
        self.__current_fstop_val = self.__current_fstop_val - C.FSTOP_DOWN
        self.__color_api.set_fstop(self.__current_fstop_val)

    def __fstop_reset(self):
        self.__current_fstop_val = C.FSTOP_RESET
        self.__color_api.set_fstop(self.__current_fstop_val)

    def __fstop_pgup(self):
        self.__current_fstop_val = self.__current_fstop_val + C.FSTOP_PGUP
        self.__color_api.set_fstop(self.__current_fstop_val)

    def __fstop_pgdown(self):
        self.__current_fstop_val = self.__current_fstop_val - C.FSTOP_PGDOWN
        self.__color_api.set_fstop(self.__current_fstop_val)

  # Gamma controls
    def __set_gamma_visibility(self):
        is_visible = self.gamma_slider.isVisible()
        self.actions.gamma_slider.setChecked(is_visible)
        self.__toggle_gamma_slider(is_visible)

    def __toggle_gamma_slider(self, state):
        if state:
            self.gamma_slider.show()
        else:
            self.gamma_slider.hide()

    def __set_gamma_value(self, value):
        if value is None: return
        self.__current_gamma_val = value
        self.__color_api.set_gamma(value)

    def __gamma_up(self):
        val = self.__current_gamma_val
        self.__current_gamma_val = C.GAMMA_UP ** (round(math.log(val, C.GAMMA_UP)) + 1) if val > 0 else 0.01
        self.__color_api.set_gamma(self.__current_gamma_val)

    def __gamma_down(self):
        val = self.__current_gamma_val
        self.__current_gamma_val = C.GAMMA_DOWN ** (round(math.log(val, C.GAMMA_DOWN)) - 1) if val > 0 else val
        self.__color_api.set_gamma(self.__current_gamma_val)

    def __gamma_reset(self):
        self.__current_gamma_val = C.GAMMA_RESET
        self.__color_api.set_gamma(self.__current_gamma_val)

    # Image rotation
    def __set_image_rot_visibility(self):
        is_visible = self.image_rot_slider.isVisible()
        self.actions.rotation_slider.setChecked(is_visible)
        self.__toggle_image_rot_slider(is_visible)

    def __toggle_image_rot_slider(self, state):
        if state:
            self.image_rot_slider.show()
        else:
            self.image_rot_slider.hide()

    def __set_image_rot_value(self, angle):
        if angle is None: return
        self.__viewport_api.set_rotation(angle)

    def __update_rotation(self, angle):
        self.__viewport_api.set_rotation(angle)

    def __post_set_fstop(self, out, value):
        self.__current_fstop_val = value
        self.fstop_slider.set_slider_value(value)
        self.__viewport_api.display_msg("FStop: %.2f" % value)

    def __post_set_gamma(self, out, value):
        self.__current_gamma_val = value
        self.gamma_slider.set_slider_value(value)
        self.__viewport_api.display_msg("Gamma: %.2f" % value)

    def __post_set_rotation(self, out, angle):
        self.__current_rotation_val = angle
        self.image_rot_slider.set_slider_value(angle)
        self.__viewport_api.display_msg("Rotation: %d" % angle)

