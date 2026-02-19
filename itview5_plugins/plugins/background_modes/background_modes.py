from PySide2 import QtCore, QtWidgets, QtGui
from rpa.widgets.background_modes.background_modes \
    import BackgroundModes as RpaBackgroundModes
from rpa.session_state.annotations import Annotation
from rpa.session_state.color_corrections import ColorCorrection
import uuid
import os


class BackgroundModes(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__background_modes = RpaBackgroundModes(self.__rpa, self.__main_window)

        self.__background_modes.actions.pip.setProperty("hotkey_editor", True)        
        self.__background_modes.actions.side_by_side.setProperty("hotkey_editor", True)
        self.__background_modes.actions.top_to_bottom.setProperty("hotkey_editor", True)
        self.__background_modes.actions.swap_background.setProperty("hotkey_editor", True)
        self.__background_modes.actions.turn_off_background.setProperty("hotkey_editor", True)
        
        self.__create_menu_bar()

    def __create_menu_bar(self):
        plugins_menu = self.__main_window.get_plugins_menu()
        background_control = plugins_menu.addMenu("Background")
        background_control.setTearOffEnabled(True)

        background_control.addAction(self.__background_modes.actions.turn_off_background)
        background_control.addSeparator()        
        background_control.addAction(self.__background_modes.actions.wipe)
        background_control.addAction(self.__background_modes.actions.side_by_side)
        background_control.addAction(self.__background_modes.actions.top_to_bottom)
        background_control.addAction(self.__background_modes.actions.pip)
        background_control.addSeparator()
        background_control.addAction(self.__background_modes.actions.swap_background)

        mix_modes = background_control.addMenu("Mix Modes")
        mix_modes.addAction(self.__background_modes.actions.none_mix_mode)
        mix_modes.addAction(self.__background_modes.actions.add_mix_mode)
        mix_modes.addAction(self.__background_modes.actions.diff_mix_mode)
        mix_modes.addAction(self.__background_modes.actions.sub_mix_mode)
        mix_modes.addAction(self.__background_modes.actions.over_mix_mode)
