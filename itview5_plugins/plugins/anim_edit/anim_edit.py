from PySide2 import QtCore, QtGui, QtWidgets
from itview.skin.widgets.itv_dock_widget import ItvDockWidget
from rpa.widgets.frame_editor.frame_editor import FrameEditor



class AnimEdit:

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__session_api = self.__rpa.session_api
        self.__timeline_api = self.__rpa.timeline_api
        self.__viewport_api = self.__rpa.viewport_api

        self.__frame_editor_widget = FrameEditor(self.__rpa, self.__main_window)
        self.__dock_widget = ItvDockWidget("AnimEdit", self.__main_window)
        self.__dock_widget.setWidget(self.__frame_editor_widget)
        self.__main_window.addDockWidget(
            QtCore.Qt.RightDockWidgetArea, self.__dock_widget)
        self.__dock_widget.hide()

        self.__create_actions()
        self.__connect_signals()
        self.__create_menu()

        self.__anim_edit_overlay_id = None
        self.__anim_edit_overlay = None

    def __create_actions(self):
        self.anim_edit_ui_action = self.__dock_widget.toggleViewAction()
        self.anim_edit_ui_action.setShortcut(QtGui.QKeySequence("F11"))
        self.anim_edit_ui_action.setProperty("hotkey_editor", True)

        self.hold_frame_action = QtWidgets.QAction("Hold Frame")
        self.hold_frame_action.setShortcut(QtGui.QKeySequence("Ctrl+Ins"))
        self.hold_frame_action.setProperty("hotkey_editor", True)

        self.drop_frame_action = QtWidgets.QAction("Drop Frame")
        self.drop_frame_action.setShortcut(QtGui.QKeySequence("Ctrl+Del"))
        self.drop_frame_action.setProperty("hotkey_editor", True)

        self.reset_frame_action = QtWidgets.QAction("Reset Frame Edits")

    def __connect_signals(self):
        self.__timeline_api.SIG_FRAME_CHANGED.connect(self.__update_anim_edit_overlay)
        self.__session_api.SIG_CURRENT_CLIP_CHANGED.connect(lambda: self.__update_anim_edit_overlay(None))
        self.__session_api.SIG_ATTR_VALUES_CHANGED.connect(self.__attr_value_changed)

        self.anim_edit_ui_action.triggered.connect(self.__toggle_anim_edit_ui)
        self.hold_frame_action.triggered.connect(lambda: self.__edit_frame(1))
        self.drop_frame_action.triggered.connect(lambda: self.__edit_frame(-1))
        self.reset_frame_action.triggered.connect(self.__reset_frames)

        self.__dock_widget.visibilityChanged.connect(
            lambda is_visible: self.__toggle_anim_edit_overlay(is_visible))
        self.__main_window.SIG_INITIALIZED.connect(self.__post_init)

    def __create_menu(self):
        plugins_menu = self.__main_window.get_plugins_menu()

        anim_edit_menu = QtWidgets.QMenu("AnimEdit", plugins_menu)
        anim_edit_menu.setTearOffEnabled(True)
        anim_edit_menu.addAction(self.anim_edit_ui_action)
        anim_edit_menu.addSeparator()
        anim_edit_menu.addAction(self.hold_frame_action)
        anim_edit_menu.addAction(self.drop_frame_action)
        anim_edit_menu.addSeparator()
        anim_edit_menu.addAction(self.reset_frame_action)
        anim_edit_menu.addSeparator()
        plugins_menu.addMenu(anim_edit_menu)

    def __post_init(self):
        self.__create_anim_edit_overlay()

    def __toggle_anim_edit_ui(self, checked:bool):
        if checked:
            self.__frame_editor_widget.reconnect_signals()
        else:
            self.__frame_editor_widget.disconnect_signals()
        self.__toggle_anim_edit_overlay(self.__dock_widget.isVisible())

    def __edit_frame(self, edit_type:int):
        if edit_type not in (-1, 1):
            return
        
        clip_id = self.__session_api.get_current_clip()
        if not clip_id:
            return
        
        current_frame = self.__timeline_api.get_current_frame()
        current_clip_frame = self.__timeline_api.get_clip_frames([current_frame])
        if current_clip_frame is not None:
            [current_clip_frame] = current_clip_frame
            current_local_frame = current_clip_frame[2]
            self.__session_api.edit_frames(clip_id, edit_type, current_local_frame, 1)

    def __reset_frames(self):
        self.__frame_editor_widget.reset_frames()

    def __attr_value_changed(self, attr_values):
        for attr_value in attr_values:
            playlist, clip, attr, value = attr_value
            if attr in ("timewarp_in", "timewarp_out", "timewarp_length"):
                self.__update_anim_edit_overlay(None)
                break

    def __create_anim_edit_overlay(self):
        self.__anim_edit_overlay = {
            "html": self.__get_anim_edit_html(None, None, None),
            "x": 0.1,
            "y": 0.8,
            "width": 240,
            "height": 80,
            "is_visible": True if self.__dock_widget.isVisible() else False
        }
        self.__anim_edit_overlay_id = \
            self.__viewport_api.create_html_overlay(self.__anim_edit_overlay)

    def __toggle_anim_edit_overlay(self, is_visible:bool):
        self.__viewport_api.set_html_overlay(
            self.__anim_edit_overlay_id, {"is_visible": is_visible})

    def __update_anim_edit_overlay(self, frame:int|None):
        if frame is None:
            frame = self.__timeline_api.get_current_frame()
        
        edit_state = ""
        seq_frames_hold = []
        seq_frames_drop = []
        clip_frame_values = None

        clip_id = self.__session_api.get_current_clip()
        if clip_id:
            seq_frames = self.__timeline_api.get_seq_frames(clip_id)
            clip_frames = self.__timeline_api.get_clip_frames()

            for i, (clip_frame, seqs) in enumerate(seq_frames):
                if len(seqs) > 1:
                    seq_frames_hold.extend(
                        [frame for frame in sorted(seqs[1:]) if frame > -1])

                if i == 0:
                    continue

                prev_clip_frame = int(seq_frames[i-1][0])
                if clip_frame - 1 != prev_clip_frame:
                    seq_frames_drop.append(seqs[0])
            
            start = self.__session_api.get_attr_value(clip_id, "media_start_frame")
            end = self.__session_api.get_attr_value(clip_id, "media_end_frame")
            first = seq_frames[0]
            last = seq_frames[-1]
            if start != first[0] and start < first[0]:
                seq_frames_drop.extend(first[1])
            if end != last[0] and end > last[0]:
                seq_frames_drop.extend(last[1])
    
            if frame in sorted(seq_frames_hold):
                edit_state = "H"
                at_clip_frame = self.__timeline_api.get_clip_frames([frame])
                if at_clip_frame:
                    clip_id, clip_frame, local_frame = at_clip_frame[0]
                    clip_frame_values = [clip_frame]
            elif frame in sorted(seq_frames_drop):
                edit_state = "D"
                range_clip_frame = self.__timeline_api.get_clip_frames([frame - 1, frame])
                if range_clip_frame:
                    range_start, range_end = range_clip_frame
                    if None not in (range_start, range_end) and last[0] != end and range_end[1] == last[0]:
                        clip_frame_values = list(range(range_end[1] + 1, end + 1))
                    elif None not in (range_start, range_end):
                        clip_frame_values = list(range(range_start[1] + 1, range_end[1]))
                    elif range_start is None:
                        clip_frame_values = list(range(start, range_end[1]))
                    else:
                        clip_frame_values = None
                    
            else:
                edit_state = ""
        else:
            return

        self.__viewport_api.set_html_overlay(
            self.__anim_edit_overlay_id,
            {"html": self.__get_anim_edit_html(frame, edit_state, clip_frame_values)})

    def __get_anim_edit_html(self, frame:int, edit_state:str, clip_frame_values:list):
        if frame is None:
            return f"<span style='color: yellow; font-size:16px; font-weight: semi-bold'>AnimEdit</span>"
        else:
            clip_frame_values_str = ", ".join(str(f) for f in clip_frame_values) if clip_frame_values else ""
            return f"<span style='color: yellow; font-size:16px; font-weight: semi-bold'>\
                AnimEdit<br>{edit_state}<br>{clip_frame_values_str}</span>"
