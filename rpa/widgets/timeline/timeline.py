import json
try:
    from PySide2 import QtCore, QtWidgets, QtGui
except ImportError:
    from PySide6 import QtCore, QtWidgets, QtGui
from rpa.widgets.timeline.view.range import TimelineRange
from rpa.widgets.timeline.view.actions import Actions
from rpa.widgets.timeline.view.slider import TimelineSlider
from rpa.widgets.timeline.model.timeline_datatypes import RangeScope, SliderScope
from rpa.session_state.transforms import DYNAMIC_TRANSFORM_ATTRS
from rpa.session_state.annotations import Stroke, Text, Annotation


TIMELINE_SELECTED_KEYS = "selected_timeline_keys"
MIME_TYPE_ANNOTATION_LIST = 'itview/annotations'


class TimelineController(QtWidgets.QToolBar):
    def __init__(self, rpa, parent_widget):
        super().__init__("Timeline Toolbar")
        self.setObjectName("Timeline Toolbar")

        self.__main_window = parent_widget
        self.__status_bar = self.__main_window.statusBar()

        self.__timeline_api = rpa.timeline_api
        self.__annotation_api = rpa.annotation_api
        self.__session_api = rpa.session_api
        self.__color_api = rpa.color_api
        self.__config_api = rpa.config_api

        self.__slider_scope = SliderScope()
        self.__range_scope = RangeScope()

        # session information
        self.__playlist_id = self.__session_api.get_fg_playlist()
        self.__clip_id = self.__session_api.get_current_clip()
        self.__playlist = None
        self.__current_fps = None
        self.__override_clip_fps = False
        self.__selected_keys = {}

        self.__create_playback_actions()
        self.__create_playback_toolbar()
        # self.__create_playback_menubar()
        self.__create_slider()
        self.addSeparator()
        self.__create_range_boxes()

        self.__annotation_api.SIG_MODIFIED.connect(self.__annotation_modified)

        self.__color_api.SIG_CCS_MODIFIED.connect(
            lambda clip_id, frame: self.__cc_modified())
        self.__color_api.SIG_CC_NODE_MODIFIED.connect(
            lambda clip_id, cc_id, node_index: self.__cc_modified())
        self.__color_api.SIG_CC_MODIFIED.connect(
            lambda clip_id, cc_id: self.__cc_modified())

        # playlist/timeline session api signals
        self.__session_api.SIG_FG_PLAYLIST_CHANGED.connect(self.__playlist_changed)
        self.__session_api.SIG_CURRENT_CLIP_CHANGED.connect(self.__clip_changed)
        self.__timeline_api.SIG_FRAME_CHANGED.connect(self.__frame_changed)
        self.__timeline_api.SIG_MODIFIED.connect(self.__update)

        self.__main_window.addToolBar(QtCore.Qt.BottomToolBarArea, self)

        copy_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+C"), self.__slider)
        copy_shortcut.setContext(QtCore.Qt.WidgetShortcut)
        copy_shortcut.activated.connect(self.__copy_annotations)

        cut_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+X"), self.__slider)
        cut_shortcut.setContext(QtCore.Qt.WidgetShortcut)
        cut_shortcut.activated.connect(self.__cut_annotations)

        paste_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+V"), self.__slider)
        paste_shortcut.setContext(QtCore.Qt.WidgetShortcut)
        paste_shortcut.activated.connect(self.__paste_annotations)

    def set_visible(self, visible):
        if visible:
            self.show()
            self.__tool_bar.show()
        else:
            self.hide()
            self.__tool_bar.hide()

    # Playback actions/toolbar
    def __create_playback_actions(self):
        self.actions = Actions(self.__main_window)
        self.actions.SIG_PLAY_TOGGLED.connect(
            lambda state: self.__play_toggled(state)
        )
        self.actions.SIG_PLAY_FORWARDS_TOGGLED.connect(
            lambda state: self.__timeline_api.set_playing_state(state, True)
        )
        self.actions.SIG_PLAY_BACKWARDS_TOGGLED.connect(
            lambda state: self.__timeline_api.set_playing_state(state, False)
        )
        self.actions.SIG_STEP_FORWARDS_TRIGGERED.connect(
            lambda: self.__timeline_api.goto_frame(self.__slider.get_current_time()+1)
        )
        self.actions.SIG_STEP_BACKWARDS_TRIGGERED.connect(
            lambda: self.__timeline_api.goto_frame(self.__slider.get_current_time()-1)
        )
        self.actions.SIG_MUTE_TOGGLED.connect(self.__timeline_api.set_mute)
        self.actions.SIG_VOLUME_CHANGED.connect(self.__timeline_api.set_volume)
        self.actions.SIG_AUDIO_SCRUBBING_TOGGLED.connect(
            lambda state: self.__timeline_api.enable_audio_scrubbing(state)
        )

        self.actions.SIG_PLAYBACK_MODE_CHANGED.connect(
            lambda mode: self.__timeline_api.set_playback_mode(mode))

        self.__timeline_api.SIG_PLAY_STATUS_CHANGED.connect(self.actions.set_play_status)
        self.__timeline_api.delegate_mngr.add_post_delegate(
            self.__timeline_api.set_volume, self.__post_set_volume)
        self.__timeline_api.delegate_mngr.add_post_delegate(
            self.__timeline_api.set_mute, self.__post_set_mute)
        self.actions.set_play_status(*self.__timeline_api.get_playing_state())
        self.actions.volume_slider.setValue(self.__timeline_api.get_volume())

    def __play_toggled(self, state):
        _, forward = self.__timeline_api.get_playing_state()
        self.__timeline_api.set_playing_state(state, forward)

    def __post_set_volume(self, out, volume):
        self.actions.set_volume(self.__timeline_api.get_volume(), emit_signal=False)

    def __post_set_mute(self, out, state):
        self.actions.toggle_mute(self.__timeline_api.is_mute(), emit_signal=False)

    def __create_playback_toolbar(self):
        self.__tool_bar = QtWidgets.QToolBar("Playback Toolbar")
        self.__tool_bar.setObjectName("Playback Toolbar")
        for action in [
            self.actions.step_backward_action,
            self.actions.toggle_play_backward_action,
            self.actions.toggle_play_forward_action,
            self.actions.step_forward_action
        ]:
            self.__tool_bar.addAction(action)

        self.__tool_bar.addWidget(self.actions.volume_button)
        self.__main_window.addToolBarBreak(QtCore.Qt.BottomToolBarArea)
        self.__main_window.addToolBar(
            QtCore.Qt.BottomToolBarArea, self.__tool_bar)

    # Timeline Slider
    def __create_slider(self):
        self.__slider: TimelineSlider = TimelineSlider(self, self.__slider_scope)
        self.__is_scrubbing = False
        self.__session_api.set_custom_session_attr("is_timeline_scrubbing", self.__is_scrubbing)
        sp = self.__slider.sizePolicy()
        sp.setHorizontalStretch(1)
        sp.setVerticalStretch(1)
        self.__slider.setSizePolicy(sp)
        self.__slider.setMinimumWidth(300)
        self.__slider.SIG_SLIDER_SCOPE_SELECTED.connect(self.__slider_scope_selected)
        self.__slider.SIG_CURRENT_TIME_CHANGED.connect(self.__slider_value_changed)
        self.__slider.SIG_SELECTED_KEYS_CHANGED.connect(self.__slider_selection_changed)
        self.__slider.SIG_SCRUBBING_STATE_CHANGED.connect(self.__slider_scrubbing_state_changed)
        self.__slider_scope_selected()
        self.addWidget(self.__slider)

    def __update_slider_current_frame(self):
        clip_mode = self.__slider_scope.is_clip_scope()
        current_frame = self.__timeline_api.get_current_frame()
        if clip_mode:
            [current_frame] = self.__convert_to_clip_frames([current_frame])
        self.__slider.set_current_time(current_frame)

    def __update_slider_range(self):
        if self.__playlist_id is None:
            return
        clip_mode = self.__slider_scope.is_clip_scope()
        left, right = self.__timeline_api.get_frame_range()
        if clip_mode:
            left = self.__session_api.get_attr_value(self.__clip_id, "key_in")
            right = self.__session_api.get_attr_value(self.__clip_id, "key_out")
        if left == right:
            right += 2
        self.__slider.set_range(left, right)

    def __update_slider_keys(self):
        self.__annotation_modified()
        self.__cc_modified()
        self.__transform_keys_modified()

    def __slider_value_changed(self, value):
        if self.__slider_scope.is_clip_scope():
            [value] = self.__timeline_api.get_seq_frames(self.__clip_id, [value])
        self.__timeline_api.goto_frame(value)

    def __slider_scope_selected(self):
        if self.__playlist_id is None:
            return
        self.__update_slider()

    def __slider_selection_changed(self):
        selected_keys = self.__slider.get_selected_keys()
        if not self.__selected_keys and not selected_keys: return
        clip_mode = self.__range_scope.is_clip_scope()
        if clip_mode:
            self.__selected_keys = {self.__session_api.get_current_clip(): list(selected_keys)}
        self.__session_api.set_custom_session_attr(TIMELINE_SELECTED_KEYS, self.__selected_keys)

    def __slider_scrubbing_state_changed(self, state):
        self.__is_scrubbing = state
        self.__session_api.set_custom_session_attr("is_timeline_scrubbing", self.__is_scrubbing)

    # Range boxes
    def __create_range_boxes(self):
        self.__timeline_range = TimelineRange(self, self.__range_scope)
        self.__timeline_range.SIG_START_FRAME_RANGE_CHANGED.connect(self.__range_start_changed)
        self.__timeline_range.SIG_CURR_FRAME_RANGE_CHANGED.connect(self.__range_cur_changed)
        self.__timeline_range.SIG_END_FRAME_RANGE_CHANGED.connect(self.__range_end_changed)
        self.__timeline_range.SIG_START_FRAME_EDITING_CANCELLED.connect(self.__update_range_key_in_out)
        self.__timeline_range.SIG_CURR_FRAME_EDITING_CANCELLED.connect(self.__update_range_current_frame)
        self.__timeline_range.SIG_END_FRAME_EDITING_CANCELLED.connect(self.__update_range_key_in_out)
        self.__timeline_range.SIG_RANGE_SCOPE_CHANGED.connect(self.__update_range)
        self.__timeline_range.SIG_RANGE_DISPLAY_MODE_CHANGED.connect(self.__update_range)
        self.addWidget(self.__timeline_range)

    def __range_start_changed(self, key_in):
        if not self.__playlist_id or not self.__clip_id:
            return
        if self.__range_scope.is_sequence_scope() or self.__range_scope.is_display_mode_timecode() \
                or self.__range_scope.is_display_mode_feet():
            return

        attr_values = [(self.__playlist_id, self.__clip_id, "key_in", key_in)]
        print(f'216 attr_values: {attr_values}')
        self.__session_api.set_attr_values(attr_values)

    def __range_cur_changed(self, frame):
        if not self.__playlist_id or not self.__clip_id:
            return
        if self.__range_scope.is_display_mode_timecode() or self.__range_scope.is_display_mode_feet():
            return
        if self.__range_scope.is_clip_scope():
            [frame] = self.__timeline_api.get_seq_frames(self.__clip_id, [frame])
            if not frame:
                return
        self.__timeline_api.goto_frame(frame)

    def __range_end_changed(self, key_out):
        if not self.__playlist_id or not self.__clip_id:
            return
        if self.__range_scope.is_sequence_scope() or self.__range_scope.is_display_mode_timecode() \
                or self.__range_scope.is_display_mode_feet():
            return

        attr_values = [(self.__playlist_id, self.__clip_id, "key_out", key_out)]
        self.__session_api.set_attr_values(attr_values)

    def __update_range_current_frame(self, sequence_frame=None, src_frame=None):
        if self.__playlist_id is None:
            return

        clip_mode = self.__range_scope.is_clip_scope()
        current_frame = src_frame if clip_mode else sequence_frame
        if not current_frame:
            current_frame = self.__timeline_api.get_current_frame()
            if clip_mode and self.__range_scope.is_display_mode_frame():
                [current_frame] = self.__convert_to_clip_frames([current_frame])
        if not self.__range_scope.is_display_mode_frame():
            [current_frame] = self.__convert_frames_display([current_frame],
                                                            clip_mode,
                                                            self.__range_scope.display_mode.value)
        self.__timeline_range.set_current_frame(current_frame)

    def __update_range_key_in_out(self):
        if self.__playlist_id is None:
            return
        clip_mode = self.__range_scope.is_clip_scope()
        if clip_mode and self.__range_scope.is_display_mode_frame():
            key_in = self.__session_api.get_attr_value(self.__clip_id, "key_in")
            key_out = self.__session_api.get_attr_value(self.__clip_id, "key_out")
            if not key_in and not key_out:
                key_in, key_out = 1, 1
        else:
            key_in, key_out = self.__timeline_api.get_frame_range()

        if not self.__range_scope.is_display_mode_frame():
            [key_in, key_out] = self.__convert_frames_display([key_in, key_out],
                                                                           clip_mode,
                                                                           self.__range_scope.display_mode.value)
        self.__timeline_range.set_range_key_in(key_in)
        self.__timeline_range.set_range_key_out(key_out)

    def __update_range_total(self):
        if self.__playlist_id is None:
            return

        key_in, key_out = self.__timeline_api.get_frame_range()
        total = key_out - key_in + 1
        if not self.__range_scope.is_display_mode_frame():
            # Since total is a difference, it's technically in global frame scope
            [total] = self.__convert_frames_display([total], False,
                                                    self.__range_scope.display_mode.value)
        self.__timeline_range.set_range_total(total)

    # Common methods for controlling slider and range
    def __update(self):
        self.__playlist_id = self.__session_api.get_fg_playlist()
        self.__clip_id = self.__session_api.get_current_clip()
        self.__update_range()
        self.__update_slider()

    def __update_range(self):
        self.__update_range_current_frame()
        self.__update_range_key_in_out()
        self.__update_range_total()

    def __update_slider(self):
        self.__update_slider_current_frame()
        self.__update_slider_range()
        self.__update_slider_keys()
        self.__transform_keys_modified()

    def __playlist_changed(self, playlist_id):
        self.__playlist_id = playlist_id
        self.__update()

    def __clip_changed(self, clip_id):
        self.__clip_id = clip_id
        if self.__slider_scope.is_clip_scope():
            self.__update_slider()
        if self.__range_scope.is_clip_scope():
            self.__update_range()

    def __attr_values_changed(self, attr_values):
        for attr_value in attr_values:
            playlist_id, clip_id, attr_id, value = attr_value
            if playlist_id != self.__playlist_id or clip_id != self.__clip_id:
                return

            if attr_id in DYNAMIC_TRANSFORM_ATTRS:
                self.__transform_keys_modified()

    def __frame_changed(self, sequence_frame):
        src_frame = None
        if self.__slider_scope.is_clip_scope() or self.__range_scope.is_clip_scope():
            [src_frame] = self.__convert_to_clip_frames([sequence_frame])
        self.__update_range_current_frame(sequence_frame=sequence_frame, src_frame=src_frame)
        if self.__is_scrubbing:
            return
        self.__slider.set_current_time(src_frame if self.__slider_scope.is_clip_scope() else sequence_frame)

    def __transform_keys_modified(self):
        clip_mode = self.__slider_scope.is_clip_scope()
        if clip_mode:
            clip_transform_keys = self.__get_clip_transform_keys()
            self.__slider.set_transform_keys(clip_transform_keys)
        else:
            seq_transform_keys = self.__get_seq_transform_keys()
            self.__slider.set_transform_keys(seq_transform_keys)

    def __get_clip_transform_keys(self):
        keys = []
        if self.__playlist_id is not None and self.__clip_id is not None:
            clip_transform_keys = set()
            for attr_id in DYNAMIC_TRANSFORM_ATTRS:
                attr_keys = self.__session_api.get_attr_keys(self.__clip_id, attr_id)
                for key in attr_keys:
                    clip_transform_keys.add(key)
            keys = [key for key in sorted(clip_transform_keys) if key != -1]
        return keys

    def __get_seq_transform_keys(self):
        keys = []
        seq_transform_keys = set()
        if self.__playlist_id is not None:
            clip_ids = self.__session_api.get_active_clips(self.__playlist_id)
            if not clip_ids:
                clip_ids = self.__session_api.get_clips(self.__playlist_id)
            for clip_id in clip_ids:
                for attr_id in DYNAMIC_TRANSFORM_ATTRS:
                    attr_keys = self.__session_api.get_attr_keys(clip_id, attr_id)
                    seq_transform_keys = seq_transform_keys.union(self.__timeline_api.get_seq_frames(clip_id, attr_keys))
            keys = [key for key in sorted(seq_transform_keys) if key != -1]
        return keys

    def __annotation_modified(self):
        clip_mode = self.__slider_scope.is_clip_scope()
        if clip_mode:
            annotation_rw_frames = self.__annotation_api.get_rw_frames(
                self.__clip_id
            )
            annotation_ro_frames = self.__annotation_api.get_ro_frames(
                self.__clip_id
            )
        else:
            clip_ids = self.__session_api.get_active_clips(
                self.__playlist_id
            )
            if len(clip_ids) == 0:
                clip_ids = self.__session_api.get_clips(self.__playlist_id)
            annotation_rw_frames = []
            annotation_ro_frames = []
            for clip_id in clip_ids:
                rw_frames = self.__annotation_api.get_rw_frames(clip_id)
                annotation_rw_frames += self.__timeline_api.get_seq_frames(clip_id, rw_frames)
                ro_frames = self.__annotation_api.get_ro_frames(clip_id)
                annotation_ro_frames += self.__timeline_api.get_seq_frames(clip_id, ro_frames)
        self.__slider.set_annotation_rw_keys(annotation_rw_frames)
        self.__slider.set_annotation_ro_keys(annotation_ro_frames)

    def __cc_modified(self):
        clip_mode = self.__slider_scope.is_clip_scope()
        if clip_mode:
            cc_rw_frames = self.__color_api.get_rw_frames(self.__clip_id)
            cc_ro_frames = self.__color_api.get_ro_frames(self.__clip_id)
        else:
            clip_ids = self.__session_api.get_active_clips(
                self.__playlist_id
            )
            if len(clip_ids) == 0:
                clip_ids = self.__session_api.get_clips(self.__playlist_id)
            cc_rw_frames = []
            cc_ro_frames = []
            for clip_id in clip_ids:
                rw_frames = self.__color_api.get_rw_frames(clip_id)
                cc_rw_frames += self.__timeline_api.get_seq_frames(clip_id, rw_frames)
                ro_frames = self.__color_api.get_ro_frames(clip_id)
                cc_ro_frames += self.__timeline_api.get_seq_frames(clip_id, ro_frames)
        self.__slider.set_cc_rw_keys(cc_rw_frames)
        self.__slider.set_cc_ro_keys(cc_ro_frames)

    def __copy_annotations(self):
        if not self.__selected_keys:
            return
        annotations = {}
        for clip_id, frames in self.__selected_keys.items():
            if not frames: continue
            if not self.__slider_scope.is_clip_scope():
                frames = self.__convert_to_clip_frames(frames)
            first = frames[0]
            for frame in frames:
                annos = []
                rw_annotation = self.__annotation_api.get_rw_annotation(clip_id, frame)
                if rw_annotation:
                    rw_annotation = rw_annotation.__getstate__()
                    annos.extend(rw_annotation["annotations"])
                ro_annotations = self.__annotation_api.get_ro_annotations(clip_id, frame)
                if ro_annotations:
                    for anno in ro_annotations:
                        anno = anno.__getstate__()
                        annos.extend(anno["annotations"])
                if annos:
                    annotations[frame-first] = annos
        if annotations:
            data = json.dumps(annotations)
            cb = QtWidgets.QApplication.clipboard()
            md = QtCore.QMimeData()
            md.setData(MIME_TYPE_ANNOTATION_LIST, data.encode('utf-8'))
            cb.setMimeData(md)
            self.__status_bar.showMessage("Annotations copied successfully!", 2000)

    def __paste_annotations(self):
        cb = QtWidgets.QApplication.clipboard()
        md = cb.mimeData()
        [current_frame] = self.__convert_to_clip_frames([self.__timeline_api.get_current_frame()])
        clip_id = self.__session_api.get_current_clip()
        if md is not None and md.hasFormat(MIME_TYPE_ANNOTATION_LIST):
            try:
                data = bytes(md.data(MIME_TYPE_ANNOTATION_LIST)).decode('utf-8')
                data = json.loads(data)
                for frame, annotations in data.items():
                    source_frame = current_frame + int(frame)
                    all_annos = []
                    for anno in annotations:
                        if anno["class"] == "Stroke":
                            all_annos.append(Stroke().__setstate__(anno))
                        if anno["class"] == "Text":
                            all_annos.append(Text().__setstate__(anno))
                    annotation = Annotation(annotations=all_annos)
                    self.__annotation_api.set_rw_annotations({clip_id: {source_frame: annotation}})
            except:
                self.__status_bar.showMessage("No compatible data in clipboard", 3000)

    def __cut_annotations(self):
        self.__copy_annotations()
        for clip_id, frames in self.__selected_keys.items():
            if not self.__slider_scope.is_clip_scope():
                frames = self.__convert_to_clip_frames(frames)
            for frame in frames:
                self.__annotation_api.delete_rw_annotation(clip_id, frame)
    def __convert_frames_display(self, frames, clip_mode, display_mode):
        def convert_func(frame):
            if display_mode == 2:
                return self.__frame_to_timecode(frame=frame, clip_mode=clip_mode)
            elif display_mode == 3:
                return self.__frame_to_feet(frame)
            else:
                return frame
        return list(map(convert_func, frames))

    def __frame_to_feet(self, frame):
        # Function to convert frames to feet. This was adapted from
        # cutlistthingy implementation
        return '{:.3f}'.format(frame/16.0)

    def __frame_to_timecode(self, frame: int, fps: int = 24, clip_mode=False) -> str:
        seconds, frame = divmod(frame, fps)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if clip_mode:
            hours+=1
        return f"{hours:02}:{minutes:02}:{seconds:02}.{frame:02}"

    def __convert_to_clip_frames(self, frames):
        clip_frames = self.__timeline_api.get_clip_frames(frames)
        return list(map(lambda t: t[1] if t else t, clip_frames))
