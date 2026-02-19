import os
from PySide2 import QtCore
from rpa.widgets.timeline.timeline import TimelineController
from enum import Enum


class Timeline(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window
        self.__cmd_line_args = itview.cmd_line_args

        self.__timeline = TimelineController(self.__rpa, self.__main_window)

        self.__config_api = self.__rpa.config_api
        self.__create_playback_menubar()
        self.__load_preferences()

        self.__timeline.actions.step_forward_action.setProperty("hotkey_editor", True)
        self.__timeline.actions.step_backward_action.setProperty("hotkey_editor", True)
        self.__timeline.actions.toggle_play_action.setProperty("hotkey_editor", True)
        self.__timeline.actions.toggle_play_forward_action.setProperty("hotkey_editor", True)
        self.__timeline.actions.toggle_play_backward_action.setProperty("hotkey_editor", True)
        self.__timeline.actions.toggle_mute_action.setProperty("hotkey_editor", True)
        self.__timeline.actions.toggle_audio_scrubbing_action.setProperty("hotkey_editor", True)

        self.__main_window.SIG_INITIALIZED.connect(self.__post_init)
        self.__main_window.SIG_CLOSED.connect(self.__save_preferences)

    def __create_playback_menubar(self):
        plugins_menu = self.__main_window.get_plugins_menu()
        timeline_menu = plugins_menu.addMenu("Timeline")
        timeline_menu.setTearOffEnabled(True)
        for action in [
            self.__timeline.actions.step_backward_action,
            self.__timeline.actions.toggle_play_backward_action,
            self.__timeline.actions.toggle_play_action,
            self.__timeline.actions.toggle_play_forward_action,
            self.__timeline.actions.step_forward_action
        ]:
            timeline_menu.addAction(action)

        timeline_menu.addSeparator()
        timeline_menu.addAction(self.__timeline.actions.toggle_mute_action)
        timeline_menu.addAction(self.__timeline.actions.toggle_audio_scrubbing_action)
        timeline_menu.addSeparator()
        timeline_menu.addAction(self.__timeline.actions.playback_repeat_action)
        timeline_menu.addAction(self.__timeline.actions.playback_once_action)
        timeline_menu.addAction(self.__timeline.actions.playback_swing_action)
        timeline_menu.addSeparator()

        dm = self.__rpa.timeline_api.delegate_mngr
        dm.add_post_delegate(self.__rpa.timeline_api.set_playback_mode, self.__set_playback_mode)

    def __load_preferences(self):
        self.__config_api.beginGroup(PrefKey.PLUGIN.value)
        self.__config_api.beginGroup(PrefKey.AUDIO.value)

        audio_volume = \
            int(self.__config_api.value(PrefKey.VOLUME.value, 100))
        if audio_volume > 100 or audio_volume < 0:
            audio_volume = 100
        self.__timeline.actions.set_volume(audio_volume)

        mute_state = \
            self.__config_api.value(PrefKey.MUTE.value) in ("true", "1")
        self.__timeline.actions.toggle_mute(mute_state)

        self.__config_api.endGroup()
        self.__config_api.endGroup()

    def __save_preferences(self):
        self.__config_api.beginGroup(PrefKey.PLUGIN.value)
        self.__config_api.beginGroup(PrefKey.AUDIO.value)

        self.__config_api.setValue(
            PrefKey.VOLUME.value, self.__timeline.actions.get_volume())
        self.__config_api.setValue(
            PrefKey.MUTE.value, self.__timeline.actions.get_mute_state())

        self.__config_api.endGroup()
        self.__config_api.endGroup()

    def __post_init(self):
        pass
        # if self.__cmd_line_args.notimeline:
        #     self.__timeline.set_visible(False)

    def add_cmd_line_args(self, parser):
        group = parser.add_argument_group("Timeline")
        group.add_argument(
            '--ntl', '--notimeline',
            action='store_true',
            dest='notimeline',
            help='Do not show timeline and playback toolbar')

    def __set_playback_mode(self, out, mode):
        self.__timeline.actions.playback_repeat_action.setChecked(mode == 0)
        self.__timeline.actions.playback_once_action.setChecked(mode == 1)
        self.__timeline.actions.playback_swing_action.setChecked(mode == 2)


class PrefKey(Enum):
    PLUGIN = "timeline"
    AUDIO = "audio"
    VOLUME = "volume"
    MUTE = "mute"
    SCRUBBING = "scrubbing"
