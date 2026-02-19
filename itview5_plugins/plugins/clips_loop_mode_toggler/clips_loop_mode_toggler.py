from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QAction
from itview.skin.widgets.itv_dock_widget import ItvDockWidget
from rpa.widgets.rpa_interpreter.rpa_interpreter import RpaInterpreter as _RpaInterpreter
from dataclasses import dataclass, fields
from typing import List, Optional


@dataclass
class ToggleLoopData:
    active_clips:Optional[List[str]]
    current_clip:Optional[str]
    current_frame:Optional[int]

    def clear(self):
        for f in fields(self):
            setattr(self, f.name, None)


class ClipsLoopModeToggler(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window
        self.__toggle_loop_data = ToggleLoopData(None, None, None)

        self.__toggle_action = QAction(text="Toggle Loop",  parent=self)
        self.__toggle_action.triggered.connect(self.__toggle_loop_mode)
        self.__toggle_action.setShortcut(QtGui.QKeySequence("O"))
        self.__toggle_action.setProperty("hotkey_editor", True)
        self.__main_window.addAction(self.__toggle_action)

    def __toggle_loop_mode(self):
        fg_playlist = self.__rpa.session_api.get_fg_playlist()
        active_clips = self.__rpa.session_api.get_active_clips(fg_playlist)
        current_clip = self.__rpa.session_api.get_current_clip()
        current_seq_frame = self.__rpa.timeline_api.get_current_frame()
        current_clip_frame = \
            self.__rpa.timeline_api.get_clip_frames([current_seq_frame])[0][1]

        if len(active_clips) > 1:
            self.__toggle_loop_data.active_clips = active_clips
            self.__toggle_loop_data.current_clip = current_clip
            self.__toggle_loop_data.current_frame = current_clip_frame

            self.__rpa.session_api.set_active_clips(fg_playlist, [current_clip])
            self.__rpa.session_api.set_current_clip(current_clip)

            seq_frame = self.__rpa.timeline_api.get_seq_frames(
                current_clip, [current_clip_frame])
            self.__rpa.timeline_api.goto_frame(seq_frame[0][1][0])

        elif len(active_clips) == 1 and self.__toggle_loop_data.active_clips is not None:
            self.__rpa.session_api.set_active_clips(
                fg_playlist, self.__toggle_loop_data.active_clips)
            self.__rpa.session_api.set_current_clip(
                self.__toggle_loop_data.current_clip)
            seq_frame = self.__rpa.timeline_api.get_seq_frames(
                self.__toggle_loop_data.current_clip,
                [self.__toggle_loop_data.current_frame])[0][1][0]
            self.__rpa.timeline_api.goto_frame(seq_frame)

            self.__toggle_loop_data.clear()
