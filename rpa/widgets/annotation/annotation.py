import numpy as np
import json
try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
from rpa.widgets.annotation.actions import Actions
from rpa.widgets.annotation.tool_bar import ToolBar
from rpa.widgets.annotation import svg
from rpa.widgets.annotation.color_picker.controller import Controller as ColorPickerController
from rpa.widgets.annotation.color_picker.model import Model as ColorPickerModel, Rgb
from rpa.widgets.annotation.color_picker.view.view import View as ColorPickerView
from rpa.widgets.annotation import constants as C

from rpa.session_state.annotations import Annotation as RpaAnnotation
from rpa.session_state.annotations import \
    Text, StrokeMode, StrokeBrush, StrokePoint, Stroke
from rpa.session_state.utils import \
    Color, Point, screen_to_itview, itview_to_screen
from functools import partial
from enum import Enum, auto


class Strokes(Enum):
    ROTATE    = 0
    TRANSLATE = 1
    SCALE     = 2


class Annotation(QtCore.QObject):
    def __init__(self, rpa, main_window):
        super().__init__()

        self.__rpa = rpa
        self.__main_window = main_window
        self.__status_bar = self.__main_window.statusBar()

        self.__annotation_api = self.__rpa.annotation_api
        self.__color_api = self.__rpa.color_api
        self.__timeline_api = self.__rpa.timeline_api
        self.__session_api = self.__rpa.session_api
        self.__viewport_api = self.__rpa.viewport_api
        self.__logger_api = self.__rpa.logger_api

        self.__core_view = self.__main_window.get_core_view()

        self.__text_line_edit = QtWidgets.QLineEdit(self.__core_view)
        self.__text_line_edit.installEventFilter(self)
        self.__text_line_edit.setVisible(False)

        self.__main_window.installEventFilter(self)

        self.__core_view.installEventFilter(self)
        self.actions = Actions()
        self.__color = Color(0.0, 1.0, 0.0, 1.0)
        self.__pen_width = 12
        self.__eraser_width = 12
        self.__text_size = 8
        self.actions.set_color(
            self.__color.r, self.__color.g, self.__color.b, self.__color.a)

        self.__connect_signals()
        self.__create_tool_bar()

        self.__interactive_mode = self.__session_api.get_custom_session_attr(C.INTERACTIVE_MODE)
        self.__mouse_down = False
        self.__pguid = None
        self.__cguid = None
        self.__source_frame = None
        self.__geometry = None
        self.__dimensions = None
        self.__text_position = None
        self.__text = Text()
        self.__mouse_left_button_down = False     # move uses only currently
        self.__mouse_right_button_down = False    # move uses only currently
        self.__mouse_middle_button_down = False
        self.__mouse_down_location = False

        self.__timeline_selected_keys = self.__session_api.get_custom_session_attr(C.TIMELINE_SELECTED_KEYS)
        dm = self.__session_api.delegate_mngr
        dm.add_post_delegate(self.__session_api.set_custom_session_attr, self.__update_custom_attrs)

        self.__last_point = None
        self.__timeline_api.SIG_FRAME_CHANGED.connect(self.__frame_changed)

    @QtCore.Slot()
    def __frame_changed(self):
        self.__last_point = None

    def show_text_line_edit(self, show:bool):
        self.__text_line_edit.clear()
        self.__text_line_edit.setVisible(show)
        if show:
            self.__text_line_edit.setFocus()

    def __update_custom_attrs(self, out, attr_id, value):
        if attr_id == C.INTERACTIVE_MODE:
            self.__interactive_mode = value
            self.__last_point = None
            if value != C.INTERACTIVE_MODE_TEXT:
                self.__disable_text_mode()
            if value == C.INTERACTIVE_MODE_MOVE and self.__core_view.cursor() != QtCore.Qt.OpenHandCursor:
                self.__core_view.setCursor(QtCore.Qt.OpenHandCursor)
            if value != C.INTERACTIVE_MODE_MOVE and self.__core_view.cursor() == QtCore.Qt.OpenHandCursor:
                self.__core_view.unsetCursor()
        if attr_id == C.TIMELINE_SELECTED_KEYS:
            self.__timeline_selected_keys = value

    def __connect_signals(self):
        self.actions.undo.triggered.connect(self.__undo)
        self.actions.redo.triggered.connect(self.__redo)
        self.actions.clear_frame.triggered.connect(self.__clear_frame)
        self.actions.show_annotations.triggered.connect(self.__toggle_annotation_visibility)
        self.actions.prev_annot_frame.triggered.connect(
            lambda: self.__goto_nearest_feedback_frame(forward=False)
        )
        self.actions.next_annot_frame.triggered.connect(
            lambda: self.__goto_nearest_feedback_frame(forward=True)
        )
        self.actions.cut_annotations.triggered.connect(self.__cut_annotations)
        self.actions.copy_annotations.triggered.connect(self.__copy_annotations)
        self.actions.paste_annotations.triggered.connect(self.__paste_annotations)

        self.actions.SIG_DRAW_SIZE_CHANGED.connect(
            lambda action: self.__set_pen_width(action.get_size())
            )
        self.actions.SIG_ERASER_SIZE_CHANGED.connect(
            lambda action: self.__set_eraser_width(action.get_size()))

        self.actions.SIG_TEXT_SIZE_CHANGED.connect(
            lambda action: self.__set_text_size(action.get_size()))

        self.__color_picker = ColorPickerController(
            ColorPickerModel(), ColorPickerView(self.__main_window))

        self.__color_picker.set_current_color(
            Rgb(self.__color.r, self.__color.g, self.__color.b))

        self.__color_picker.SIG_SET_CURRENT_COLOR.connect(
            lambda rgb : self.__set_color(rgb.red, rgb.green, rgb.blue, 1.0))
        self.actions.color.triggered.connect(lambda: self.__color_picker.show())

        for rpa_method in [
            self.__session_api.set_fg_playlist,
            self.__session_api.set_current_clip,
            self.__session_api.set_active_clips,
            self.__timeline_api.goto_frame,
            self.__timeline_api.set_playing_state
        ]:
            self.__session_api.delegate_mngr.add_pre_delegate(
                rpa_method, self.__disable_text_mode)

        for rpa_method in [
            self.__timeline_api.goto_frame,
            self.__timeline_api.set_playing_state
        ]:
            self.__timeline_api.delegate_mngr.add_pre_delegate(
                rpa_method, self.__disable_text_mode)

        for rpa_method in [
            self.__annotation_api.clear_frame,
            self.__annotation_api.undo,
            self.__annotation_api.redo,
        ]:
            self.__annotation_api.delegate_mngr.add_pre_delegate(
                rpa_method, self.__disable_text_mode)

        for rpa_method in [
            self.__viewport_api.scale_on_point,
            self.__viewport_api.set_scale,
            self.__viewport_api.flip_x,
            self.__viewport_api.flip_y,
            self.__viewport_api.fit_to_window,
            self.__viewport_api.fit_to_width,
            self.__viewport_api.fit_to_height,
        ]:
            self.__viewport_api.delegate_mngr.add_pre_delegate(
                rpa_method, self.__disable_text_mode)

        self.__rpa.viewport_api.delegate_mngr.add_post_delegate(
            self.__rpa.viewport_api.set_feedback_visibility,
            self.__feedback_visibility_delegate)

    def __set_pen_width(self, width):
        self.__pen_width = width

    def __set_eraser_width(self, width):
        self.__eraser_width = width

    def __set_text_size(self, size):
        self.__text_size = size
        if self.__viewport_api.is_text_cursor_set():
            self.__viewport_api.set_text_cursor(
                self.__text_position, self.__text_size)
            self.__set_text(self.__text_line_edit.text())

    def __set_text(self, text):
        if not self.__viewport_api.is_text_cursor_set(): return
        cguid = self.__session_api.get_current_clip()
        frame = self.__get_current_clip_frame()
        self.__annotation_api.set_text(
            cguid, frame, Text(
                text, self.__text_position, self.__color, self.__text_size))

    def __disable_text_mode(self, *args, **kwargs):
        self.__text_line_edit.clear()
        self.show_text_line_edit(False)
        if self.__viewport_api.is_text_cursor_set():
            self.__viewport_api.unset_text_cursor()
        self.__text = Text()
        self.__text_position = None

    def __get_resolution(self, playlist_id, clip_id):
        w, h = 0, 0
        resolution = self.__session_api.get_attr_value(clip_id, "resolution")
        w, h = resolution.split("x")
        w = int(w.strip())
        h = int(h.strip())
        return w, h

    def __append_point(self, interactive_mode, x, y, is_line=False):
        if interactive_mode == C.INTERACTIVE_MODE_MOVE:
            self.__core_view.setCursor(QtCore.Qt.ClosedHandCursor)
            if self.__mouse_left_button_down:
                self.__update_annotations(
                    Strokes.TRANSLATE, self.__mouse_down_location, (x,y))
            if self.__mouse_right_button_down:
                self.__update_annotations(
                    Strokes.SCALE, self.__mouse_down_location, (x,y))
            if self.__mouse_middle_button_down:
                self.__update_annotations(
                    Strokes.ROTATE, self.__mouse_down_location, (x,y))
            return
        mode = StrokeMode.PEN
        if interactive_mode in (
            C.INTERACTIVE_MODE_HARD_ERASER, C.INTERACTIVE_MODE_SOFT_ERASER):
            mode = StrokeMode.ERASER
        brush = StrokeBrush.CIRCLE
        if interactive_mode in (
            C.INTERACTIVE_MODE_AIRBRUSH, C.INTERACTIVE_MODE_SOFT_ERASER):
            brush = StrokeBrush.GAUSS
        width = self.__pen_width
        if interactive_mode in (
            C.INTERACTIVE_MODE_HARD_ERASER, C.INTERACTIVE_MODE_SOFT_ERASER):
            width = self.__eraser_width
        point = Point(*screen_to_itview(self.__geometry, x, y))
        self.__last_point = point if interactive_mode == C.INTERACTIVE_MODE_MULTI_LINE else None
        stroke_point = StrokePoint(
            mode=mode,
            brush=brush,
            width=width,
            color=self.__color,
            point=point)
        self.__annotation_api.append_transient_point(
            self.__cguid,
            self.__source_frame,
            "local",
            stroke_point,
            is_line=is_line)

    def __update_annotations(self, transform, old, new):
        if not self.__annotation: return

        # points in screen coordinates
        sold = Point(*old)
        snew = Point(*new)
        sdx, sdy = snew.x - sold.x, snew.y - sold.y

        # points in itview coordinates
        iold = Point(*screen_to_itview(self.__geometry, *old))
        inew = Point(*screen_to_itview(self.__geometry, *new))
        idx, idy = inew.x - iold.x, inew.y - iold.y

        new_annotation = self.__annotation.copy()
        if transform == Strokes.TRANSLATE:
            for annotation in new_annotation.annotations:
                if isinstance(annotation, Stroke):
                    for point in annotation.points:
                        point.x += idx
                        point.y += idy
        if transform == Strokes.SCALE:
            scale = 1.0 + 0.01 * (sdx - sdy)
            for annotation in new_annotation.annotations:
                if isinstance(annotation, Stroke):
                    annotation.width *= scale
                    for point in annotation.points:
                        x, y = point.x - iold.x, point.y - iold.y
                        x, y = x * scale, y * scale
                        point.x, point.y = x + iold.x, y + iold.y
        if transform == Strokes.ROTATE:
            angle = 0.25 * (sdy - sdx)
            sin = np.sin(np.radians(angle))
            cos = np.cos(np.radians(angle))
            for annotation in new_annotation.annotations:
                if isinstance(annotation, Stroke):
                    for point in annotation.points:
                        x, y = itview_to_screen(self.__geometry, point.x, point.y)
                        x -= sold.x; y -= sold.y
                        x, y = (x * cos) - (y * sin), (x * sin) + (y * cos)
                        x += sold.x; y += sold.y
                        point.x, point.y = screen_to_itview(self.__geometry, x, y)
        self.__annotation_api.set_rw_annotations(
            {self.__cguid: {self.__source_frame: new_annotation}})

    def eventFilter(self, obj, event):
        if obj == self.__text_line_edit:
            if event.type() == QtCore.QEvent.KeyPress and \
            event.key() == QtCore.Qt.Key_Escape:
                self.show_text_line_edit(False)
            return False

        if obj == self.__main_window:
            if event.type() == QtCore.QEvent.KeyPress and \
            event.key() == QtCore.Qt.Key_Escape:
                self.__last_point = None
            return False

        if event.type() == QtCore.QEvent.Leave:
            self.__annotation_api.set_pointer(None)

        if not (
        event.type() == QtCore.QEvent.MouseButtonPress or \
        event.type() == QtCore.QEvent.MouseMove or \
        event.type() == QtCore.QEvent.MouseButtonRelease):
            return False

        get_pos = lambda: (event.pos().x(), obj.height() - event.pos().y())
        self.__geometry = self.__viewport_api.get_current_clip_geometry()
        if self.__interactive_mode in (
            C.INTERACTIVE_MODE_PEN,
            C.INTERACTIVE_MODE_LINE,
            C.INTERACTIVE_MODE_MULTI_LINE,
            C.INTERACTIVE_MODE_AIRBRUSH,
            C.INTERACTIVE_MODE_HARD_ERASER,
            C.INTERACTIVE_MODE_SOFT_ERASER,
        ):
            if self.__geometry is not None:
                mode = StrokeMode.PEN
                if self.__interactive_mode in \
                    (C.INTERACTIVE_MODE_HARD_ERASER, C.INTERACTIVE_MODE_SOFT_ERASER):
                    mode = StrokeMode.ERASER
                brush = StrokeBrush.CIRCLE
                if self.__interactive_mode in \
                    (C.INTERACTIVE_MODE_AIRBRUSH, C.INTERACTIVE_MODE_SOFT_ERASER):
                    brush = StrokeBrush.GAUSS
                width = self.__pen_width
                if self.__interactive_mode in \
                    (C.INTERACTIVE_MODE_HARD_ERASER, C.INTERACTIVE_MODE_SOFT_ERASER):
                    width = self.__eraser_width
                point = Point(*screen_to_itview(self.__geometry, *get_pos()))
                stroke_point = StrokePoint(
                    mode=mode,
                    brush=brush,
                    width=width,
                    color=self.__color,
                    point=point)
                self.__annotation_api.set_pointer(stroke_point)

        interactive_mode = None
        if event.modifiers() == QtCore.Qt.NoModifier:
            interactive_mode = self.__interactive_mode
        if event.modifiers() == QtCore.Qt.ControlModifier:
            interactive_mode = C.INTERACTIVE_MODE_PEN
        if event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier:
            interactive_mode = C.INTERACTIVE_MODE_HARD_ERASER
        if event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier:
            interactive_mode = C.INTERACTIVE_MODE_LINE
        if event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.MetaModifier:
            interactive_mode = C.INTERACTIVE_MODE_MULTI_LINE
        if interactive_mode is None:
            return False

        is_line = interactive_mode in (C.INTERACTIVE_MODE_LINE, C.INTERACTIVE_MODE_MULTI_LINE)

        if self.__mouse_down and event.type() == QtCore.QEvent.MouseMove:
            self.__append_point(interactive_mode, *get_pos(), is_line=is_line)

        self.__source_frame = self.__get_current_clip_frame()
        # Text mode
        if interactive_mode == C.INTERACTIVE_MODE_TEXT and \
            event.type() == QtCore.QEvent.MouseButtonRelease:
                self.__text_position = Point(
                    *screen_to_itview(self.__geometry, *get_pos()))
                self.__viewport_api.set_text_cursor(
                    self.__text_position, self.__text_size)
                self.show_text_line_edit(True)
        if interactive_mode in (
            C.INTERACTIVE_MODE_PEN, C.INTERACTIVE_MODE_LINE, C.INTERACTIVE_MODE_MULTI_LINE,
            C.INTERACTIVE_MODE_AIRBRUSH, C.INTERACTIVE_MODE_HARD_ERASER, C.INTERACTIVE_MODE_SOFT_ERASER,
            C.INTERACTIVE_MODE_MOVE):
            if event.type() == QtCore.QEvent.MouseButtonPress:
                self.__pguid = self.__session_api.get_fg_playlist()
                self.__cguid = self.__session_api.get_current_clip()
                if None not in (self.__pguid, self.__cguid):
                    self.__mouse_down = True
                    self.__dimensions = self.__get_resolution(self.__pguid, self.__cguid)
                    if interactive_mode == C.INTERACTIVE_MODE_MOVE:
                        annotation = self.__annotation_api.get_rw_annotation(self.__cguid, self.__source_frame)
                        if annotation:
                            self.__annotation = RpaAnnotation().__setstate__(annotation.__getstate__())
                            self.__mouse_down_location = get_pos()
                            self.__viewport_api.set_cross_hair_cursor(
                                Point(*screen_to_itview(self.__geometry, *get_pos())))
                            if event.button() == QtCore.Qt.LeftButton:
                                self.__mouse_left_button_down = True
                            elif event.button() == QtCore.Qt.MiddleButton:
                                self.__mouse_middle_button_down = True
                            elif event.button() == QtCore.Qt.RightButton:
                                self.__mouse_right_button_down = True
                    if interactive_mode == C.INTERACTIVE_MODE_MULTI_LINE and self.__last_point:
                        x, y = itview_to_screen(self.__geometry, *self.__last_point.__getstate__())
                        self.__append_point(interactive_mode, x, y, is_line=is_line)
                    self.__append_point(interactive_mode, *get_pos(), is_line=is_line)

            if event.type() == QtCore.QEvent.MouseButtonRelease:
                if self.__mouse_down:
                    self.__mouse_down = False
                    self.__append_point(interactive_mode, *get_pos(), is_line=is_line)
                    stroke = self.__annotation_api.get_transient_stroke(self.__cguid, self.__source_frame, "local")
                    if stroke is not None:
                        self.__annotation_api.append_strokes(self.__cguid, self.__source_frame, [stroke])
                    self.__annotation_api.delete_transient_points(self.__cguid, self.__source_frame, "local")
                    if interactive_mode == C.INTERACTIVE_MODE_MOVE:
                        self.__annotation = None
                        self.__mouse_left_button_down = False
                        self.__mouse_middle_button_down = False
                        self.__mouse_right_button_down = False
                        self.__mouse_down_location = None
                        self.__core_view.setCursor(QtCore.Qt.OpenHandCursor)
                        self.__viewport_api.set_cross_hair_cursor(None)
        return False

    def __set_color(self, r, g, b, a):
        self.actions.set_color(r, g, b, a)
        self.__color = Color(r, g, b, a)
        if self.__viewport_api.is_text_cursor_set():
            self.__set_text(self.__text_line_edit.text())

    def __create_tool_bar(self):
        self.tool_bar = ToolBar(
            self.actions, self.__annotation_api, self.__pen_width,
            self.__eraser_width, self.__text_size)
        self.__main_window.addToolBarBreak(QtCore.Qt.BottomToolBarArea)
        self.__main_window.addToolBar(
            QtCore.Qt.BottomToolBarArea, self.tool_bar)
        self.__text_line_edit.textEdited.connect(
            lambda text: self.__set_text(text))

    def __undo(self):
        cguid = self.__session_api.get_current_clip()
        current_frame = self.__get_current_clip_frame()
        self.__annotation_api.undo(cguid, current_frame)

    def __redo(self):
        cguid = self.__session_api.get_current_clip()
        current_frame = self.__get_current_clip_frame()
        self.__annotation_api.redo(cguid, current_frame)

    def __clear_frame(self):
        cguid = self.__session_api.get_current_clip()
        current_frame = self.__get_current_clip_frame()
        self.__annotation_api.clear_frame(cguid, current_frame)

    def __feedback_visibility_delegate(self, out, category, value):
        if category == 1:
            self.actions.toggle_annotation_visibility(value)

    def __toggle_annotation_visibility(self):
        visible = self.__viewport_api.is_feedback_visible(1)
        if visible:
            self.__viewport_api.set_feedback_visibility(1, False)
        else:
            self.__viewport_api.set_feedback_visibility(1, True)

    def __copy_annotations(self):
        if not self.__timeline_selected_keys:
            return
        annotations = {}
        for clip_id, frames in self.__timeline_selected_keys.items():
            if not frames: continue
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
            md.setData(C.MIME_TYPE_ANNOTATION_LIST, data.encode('utf-8'))
            cb.setMimeData(md)
            self.__status_bar.showMessage("Annotations copied successfully!", 2000)

    def __paste_annotations(self):
        cb = QtWidgets.QApplication.clipboard()
        md = cb.mimeData()
        current_frame = self.__timeline_api.get_current_frame(clip_mode=True)
        clip_id = self.__session_api.get_current_clip()
        if md is not None and md.hasFormat(C.MIME_TYPE_ANNOTATION_LIST):
            try:
                data = bytes(md.data(C.MIME_TYPE_ANNOTATION_LIST)).decode('utf-8')
                data = json.loads(data)
                for frame, annotations in data.items():
                    source_frame = current_frame + int(frame)
                    all_annos = []
                    for anno in annotations:
                        if anno["class"] == "Stroke":
                            all_annos.append(Stroke().__setstate__(anno))
                        if anno["class"] == "Text":
                            all_annos.append(Text().__setstate__(anno))
                    annotation = RpaAnnotation(annotations=all_annos)
                    self.__annotation_api.set_rw_annotations(
                        {clip_id: {source_frame: annotation}})
            except:
                self.__status_bar.showMessage("No compatible data in clipboard", 3000)

    def __cut_annotations(self):
        self.__copy_annotations()
        for clip_id, frames in self.__timeline_selected_keys.items():
            for frame in frames:
                self.__annotation_api.delete_rw_annotation(clip_id, frame)
    def __goto_nearest_feedback_frame(self, forward):
        playlist_id = self.__session_api.get_fg_playlist()
        playlist_id = self.__session_api.get_fg_playlist()
        clip_id = self.__session_api.get_current_clip()
        if not playlist_id or not clip_id:
            return False
        current_frame = self.__get_current_clip_frame()
        clip_ids = self.__session_api.get_clips(playlist_id)
        num_of_clips = len(clip_ids)
        def get_unique_values(l1, l2):
            unique_values = set(l1).union(set(l2))
            return sorted(unique_values)
        for ii, i in enumerate(range(num_of_clips+1)):
            clip_index = (clip_ids.index(clip_id) + (i if forward else -i)) % num_of_clips
            new_clip_id = clip_ids[clip_index]
            annotation_frames = self.__annotation_api.get_rw_frames(new_clip_id) \
                                + self.__annotation_api.get_ro_frames(new_clip_id)
            cc_frames = self.__color_api.get_rw_frames(new_clip_id) \
                        + self.__color_api.get_ro_frames(new_clip_id)
            frames = get_unique_values(annotation_frames, cc_frames)
            if not frames: continue
            frames = frames if forward else reversed(frames)
            seq_frames = self.__timeline_api.get_seq_frames(new_clip_id, frames)
            for frame in seq_frames:
                if frame == -1:
                    continue
                if new_clip_id != clip_id:
                    self.__session_api.set_current_clip(new_clip_id)
                    self.__timeline_api.goto_frame(frame)
                    return False
                if forward:
                    if (ii == 0 and frame > current_frame) \
                            or (ii != 0 and frame < current_frame):
                        self.__timeline_api.goto_frame(frame)
                        return False
                else:
                    if (ii == 0 and frame < current_frame) \
                            or (ii != 0 and frame > current_frame):
                        self.__timeline_api.goto_frame(frame)
                        return False
        return True

    def __get_current_clip_frame(self):
        [clip_frame] = self.__timeline_api.get_clip_frames([self.__timeline_api.get_current_frame()])
        if type(clip_frame) is not tuple:
            return -1
        return clip_frame[1]
