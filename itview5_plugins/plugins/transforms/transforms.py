import bisect
import numpy as np
from dataclasses import dataclass
from PySide2 import QtCore, QtGui, QtWidgets

from transforms.actions import Actions
from transforms.toolbar import TransformToolBar
import transforms.resources.resources
from rpa.session_state.transforms import \
    TransformData, TransformType, DynamicAttrs, StaticAttrs, MEDIA_FPS, \
    DYNAMIC_TRANSFORM_ATTRS, STATIC_TRANSFORM_ATTRS

INTERACTIVE_MODE = "interactive_mode"
INTERACTIVE_MODE_TRANSFORM = "transform"
INTERACTIVE_MODE_DYNAMIC_TRANSFORM = "dynamic_transform"


class Transforms(QtCore.QObject):
    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__session_api = self.__rpa.session_api
        self.__timeline_api = self.__rpa.timeline_api
        self.__viewport_api = self.__rpa.viewport_api

        self.__core_view = self.__main_window.get_core_view()
        self.__core_view.installEventFilter(self)

        self.__cguid = None
        self.__pguid = None
        self.__mouse_left_button_down = False
        self.__mouse_middle_button_down = False
        self.__mouse_right_button_down = False
        self.__mouse_down_location = None

        self.__actions = Actions()
        self.__toolbar = None

        self.__interactive_mode = self.__session_api.get_custom_session_attr(INTERACTIVE_MODE)
        dm = self.__session_api.delegate_mngr
        dm.add_post_delegate(self.__session_api.set_custom_session_attr, self.__update_custom_attrs)

        self.__pan_x = None
        self.__pan_y = None
        self.__scale_x = None
        self.__scale_y = None
        self.__center = None
        self.__start_vector = None
        self.__base_angle = 0.0

        self.__bounding_box_overlay = self.__viewport_api.create_opengl_overlay({
            "vertices": [[0,0], [1,0], [1,1], [0, 1]],
            "apply_image_transforms": False,
            "width": 1.0,
            "color": "#808080",
            "dashed": True,
            "opacity": 1.0,
            "is_visible": False
        })
        self.__transform_image_overlay = self.__viewport_api.create_opengl_overlay({
            "vertices": [[0,0], [1,0], [1,1], [0, 1], [0,0], [1,1], [1,0], [0,1]],
            "apply_image_transforms": True,
            "width": 1.0,
            "color": "#808080",
            "opacity": 1.0,
            "is_visible": False
        })

        self.__create_toolbar()
        self.__connect_signals()

    def __update_custom_attrs(self, out, attr_id, value):
        if attr_id == INTERACTIVE_MODE:
            self.__interactive_mode = value
            self.__set_overlays_visibility(self.__interactive_mode in (INTERACTIVE_MODE_DYNAMIC_TRANSFORM, INTERACTIVE_MODE_TRANSFORM))
            if self.__actions.toggle_dynamic_transform.isChecked():
                self.__actions.toggle_dynamic_transform.setChecked(False)
            if self.__actions.toggle_transform.isChecked():
                self.__actions.toggle_transform.setChecked(False)
            self.__core_view.unsetCursor()
            if value == INTERACTIVE_MODE_TRANSFORM:
                self.__actions.toggle_transform.setChecked(True)
                self.__update_toolbar()
            if value == INTERACTIVE_MODE_DYNAMIC_TRANSFORM:
                self.__actions.toggle_dynamic_transform.setChecked(True)
                self.__update_toolbar()
            self.__check_transform_key()

    def __set_overlays_visibility(self, visible):
        self.__viewport_api.set_opengl_overlay(self.__bounding_box_overlay, {"is_visible": visible})
        self.__viewport_api.set_opengl_overlay(self.__transform_image_overlay, {"is_visible": visible})

    def __create_toolbar(self):
        self.__toolbar = TransformToolBar(self.__actions)

        self.__main_window.addToolBarBreak(QtCore.Qt.BottomToolBarArea)
        self.__main_window.addToolBar(
            QtCore.Qt.BottomToolBarArea, self.__toolbar)

        self.__check_transform_key()

    def __connect_signals(self):
        def set_interactive_mode(mode):
            self.__session_api.set_custom_session_attr(INTERACTIVE_MODE, mode)

        self.__actions.toggle_transform.triggered.connect(
            lambda is_checked: set_interactive_mode(INTERACTIVE_MODE_TRANSFORM if is_checked else None))
        self.__actions.toggle_dynamic_transform.triggered.connect(
            lambda is_checked: set_interactive_mode(INTERACTIVE_MODE_DYNAMIC_TRANSFORM if is_checked else None))
        self.__actions.set_transform_key.triggered.connect(
            self.__set_transform_key)
        self.__actions.remove_transform_key.triggered.connect(
            self.__remove_transform_key)
        self.__actions.prev_key_frame.triggered.connect(lambda: self.__goto_nearest_key_frame(False))
        self.__actions.next_key_frame.triggered.connect(lambda: self.__goto_nearest_key_frame(True))
        self.__actions.crop_transforms.triggered.connect(
            self.__crop_transforms)
        self.__actions.reset_all.triggered.connect(
            self.__reset_all_transforms)

        self.__toolbar.SIG_SET_TRANSFORMATION.connect(
            self.__set_transformation)
        self.__toolbar.SIG_SET_MEDIA_FPS.connect(
            self.__set_media_fps)

        self.__session_api.SIG_FG_PLAYLIST_CHANGED.connect(
            self.__fg_playlist_changed)
        self.__session_api.SIG_CURRENT_CLIP_CHANGED.connect(
            self.__current_clip_changed)
        self.__session_api.SIG_ATTR_VALUES_CHANGED.connect(
            self.__attr_values_changed)

        self.__timeline_api.SIG_FRAME_CHANGED.connect(
            self.__frame_changed)

    def __get_current_playlist_clip(self):
        clip_id = self.__session_api.get_current_clip()
        if clip_id is None:
            return None
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        return playlist_id, clip_id

    def __set_media_fps(self, transform_type, value):
        if transform_type == TransformType.fps:
            clip_id = self.__session_api.get_current_clip()
            if not clip_id:
                return

            current_fps = self.__session_api.get_attr_value(
                clip_id, MEDIA_FPS)

            playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
            if current_fps != value:
                self.__session_api.set_attr_values(
                    [(playlist_id, clip_id, MEDIA_FPS, value)])

    def __set_transformation(self, transform_type, value):
        clip_id = self.__session_api.get_current_clip()
        if not clip_id:
            return
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        attr_id = None
        if self.__actions.toggle_dynamic_transform.isChecked():
            self.__set_transform_key()
        else:
            if transform_type == TransformType.rotate:
                attr_id = STATIC_TRANSFORM_ATTRS[0]
            elif transform_type == TransformType.pan_x:
                attr_id = STATIC_TRANSFORM_ATTRS[1]
            elif transform_type == TransformType.pan_y:
                attr_id = STATIC_TRANSFORM_ATTRS[2]
            elif transform_type == TransformType.zoom_x:
                attr_id = STATIC_TRANSFORM_ATTRS[3]
            elif transform_type == TransformType.zoom_y:
                attr_id = STATIC_TRANSFORM_ATTRS[4]

            self.__session_api.set_attr_values(
                [(playlist_id, clip_id, attr_id, value)])

    def __check_transform_key(self):
        enabled = self.__interactive_mode == INTERACTIVE_MODE_DYNAMIC_TRANSFORM
        self.__actions.set_transform_key.setEnabled(enabled)
        icon = QtGui.QPixmap(":set_key.png") if enabled \
            else QtGui.QPixmap(":set_key_disabled.png")
        self.__actions.set_transform_key.setIcon(QtGui.QIcon(icon))

    def __set_transform_key(self):
        self.__check_transform_key()

        clip_id = self.__session_api.get_current_clip()
        if not clip_id:
            return
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        attr_values_at = []
        src_frame = self.__get_current_clip_frame()
        transformations = self.__toolbar.get_transformations()

        for dynamic_attr_id, value in transformations.items():
            attr_values_at.append(
                (playlist_id, clip_id, dynamic_attr_id, src_frame, value))
        self.__session_api.set_attr_values_at(attr_values_at)

    def __remove_transform_key(self):
        clip_id = self.__session_api.get_current_clip()
        if not clip_id:
            return

        for_removal = []
        src_frame = self.__get_current_clip_frame()
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        for dynamic_attr_id in DYNAMIC_TRANSFORM_ATTRS:
            for_removal.append((playlist_id, clip_id, dynamic_attr_id, src_frame))
        self.__session_api.clear_attr_values_at(for_removal)

    def __get_clip_transform_keys(self, clip_id):
        clip_transform_keys = set()
        for attr_id in DYNAMIC_TRANSFORM_ATTRS:
            attr_keys = self.__session_api.get_attr_keys(clip_id, attr_id)
            for key in attr_keys:
                clip_transform_keys.add(key)

        transform_keys = [key for key in sorted(clip_transform_keys) if key != -1]
        return transform_keys

    def __find_prev_frame(self, current_frame, transform_keys):
        pos = bisect.bisect_left(transform_keys, current_frame)

        if pos == 0:
            return transform_keys[-1]
        else:
            return transform_keys[pos - 1]

    def __find_next_frame(self, current_frame, transform_keys):
        pos = bisect.bisect_right(transform_keys, current_frame)

        if pos == len(transform_keys):
            return transform_keys[0]
        else:
            return transform_keys[pos]

    def __goto_nearest_key_frame(self, forward=True):
        clip_id = self.__session_api.get_current_clip()
        if not clip_id:
            return

        current_frame = self.__timeline_api.get_current_frame()
        prev_frame = None
        clip_ids = self.__session_api.get_active_clips(playlist_id)
        if not clip_ids:
            return self.__session_api.get_clips(playlist_id)
        transform_keys = set()
        for clip_id in clip_ids:
            for attr_id in DYNAMIC_TRANSFORM_ATTRS:
                attr_keys = self.__session_api.get_attr_keys(clip_id, attr_id)
                for key in attr_keys:
                    [seq_frames] = self.__timeline_api.get_seq_frames(clip_id, [key])
                    seq_key = [seqs[0] for _, seqs in seq_frames] if seq_frames else []
                    transform_keys.add(seq_key)

        transform_keys = [key for key in sorted(transform_keys) if key != -1]
        if transform_keys:
            prev_frame = self.__find_next_frame(current_frame, transform_keys) if forward else self.__find_prev_frame(current_frame, transform_keys)

        if prev_frame and current_frame != prev_frame:
            self.__timeline_api.goto_frame(prev_frame)

    def __crop_transforms(self, enabled):
        icon = QtGui.QPixmap(":crop_transforms_off.png") if enabled \
            else QtGui.QPixmap(":crop_transforms_on.png")
        self.__actions.crop_transforms.setIcon(QtGui.QIcon(icon))

    def __reset_all_transforms(self):
        clip_id = self.__session_api.get_current_clip()
        if not clip_id:
            return
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        reset_attrs = []
        if self.__actions.toggle_dynamic_transform.isChecked():
            clip_transform_keys = \
                self.__get_clip_transform_keys(clip_id)

            for dynamic_attr_id in DYNAMIC_TRANSFORM_ATTRS:
                for key in clip_transform_keys:
                    reset_attrs.append((playlist_id, clip_id, dynamic_attr_id, key))
            self.__session_api.clear_attr_values_at(reset_attrs)

        else:
            attr_ids = STATIC_TRANSFORM_ATTRS
            attr_values = [TransformData.default_0,
                           TransformData.default_0,
                           TransformData.default_0,
                           TransformData.default_1,
                           TransformData.default_1]
            for attr_id, attr_value in zip(attr_ids, attr_values):
                reset_attrs.append((playlist_id, clip_id, attr_id, attr_value))
            self.__session_api.set_attr_values(reset_attrs)

        self.__session_api.set_attr_values(
                [(playlist_id, clip_id, MEDIA_FPS, TransformData.default_24)])

    def __fg_playlist_changed(self, playlist_id):
        clip_ids = self.__session_api.get_clips(playlist_id)
        if not clip_ids:
            self.__toolbar.clear_all()

    def __current_clip_changed(self, clip_id):
        if clip_id is None:
            return

        self.__update_toolbar()

        current_fps = \
            self.__session_api.get_attr_value(clip_id, MEDIA_FPS)
        fps = self.__toolbar.get_fps()

        if current_fps != fps:
            self.__toolbar.update_fps(current_fps)

    def __frame_changed(self, sequence_frame):
        # only applicable for dynamic transforms
        if self.__actions.toggle_dynamic_transform.isChecked():
            self.__update_toolbar()

    def __attr_values_changed(self, attr_values):
        static_transforms = {}
        dynamic_transforms = {}
        for attr_value in attr_values:
            playlist_id, clip_id, attr_id, value = attr_value

            if attr_id == MEDIA_FPS:
                self.__toolbar.update_fps(value)
                break

            if attr_id in STATIC_TRANSFORM_ATTRS:
                static_transforms[attr_id] = value

            if attr_id in DYNAMIC_TRANSFORM_ATTRS:
                src_frame = self.__get_current_clip_frame()
                value = self.__session_api.get_attr_value_at(
                    clip_id, attr_id, src_frame)
                dynamic_transforms[attr_id] = value

        if self.__actions.toggle_dynamic_transform.isChecked():
            if dynamic_transforms:
                self.__toolbar.update(dynamic_transforms)
        else:
            if static_transforms:
                self.__toolbar.update(static_transforms)

    def __update_toolbar(self):
        clip_id = self.__session_api.get_current_clip()
        if not clip_id:
            return
        src_frame = self.__get_current_clip_frame()

        current_transforms = {}

        if self.__actions.toggle_dynamic_transform.isChecked():
            for dynamic_attr_id in DYNAMIC_TRANSFORM_ATTRS:
                attr_value = self.__session_api.get_attr_value_at(
                    clip_id, dynamic_attr_id, src_frame)
                current_transforms[dynamic_attr_id] = attr_value
        else:
            for attr_id in STATIC_TRANSFORM_ATTRS:
                attr_value = self.__session_api.get_attr_value(
                    clip_id, attr_id)
                current_transforms[attr_id] = attr_value

        transformations = self.__toolbar.get_transformations()

        if set(current_transforms.items()) != set(transformations.items()):
            self.__toolbar.update(current_transforms)

    def __get_current_clip_frame(self):
        clip_frame = self.__timeline_api.get_clip_frames([self.__timeline_api.get_current_frame()])
        if not clip_frame:
            return -1
        else:
            [clip_frame] = clip_frame
            if type(clip_frame) is not tuple:
                return -1
            return clip_frame[1]

    def eventFilter(self, obj, event):
        if not (
        event.type() == QtCore.QEvent.MouseButtonPress or \
        event.type() == QtCore.QEvent.MouseMove or \
        event.type() == QtCore.QEvent.MouseButtonRelease):
            return False

        if self.__interactive_mode in \
                (INTERACTIVE_MODE_TRANSFORM,
                 INTERACTIVE_MODE_DYNAMIC_TRANSFORM):
            self.__core_view.setCursor(QtCore.Qt.OpenHandCursor)
            get_pos = lambda: (event.pos().x(), obj.height() - event.pos().y())
            self.__cguid = self.__session_api.get_current_clip()
            self.__pguid = self.__session_api.get_fg_playlist()

            if event.type() == QtCore.QEvent.MouseMove:
                self.__core_view.setCursor(QtCore.Qt.ClosedHandCursor)
                if self.__mouse_left_button_down:
                    self.__move(*get_pos())
                if self.__mouse_right_button_down:
                    self.__scale(*get_pos())
                if self.__mouse_middle_button_down:
                    if self.__start_vector is not None: self.__rotate(event.pos())
                return True

            if event.type() == QtCore.QEvent.MouseButtonPress:
                self.__mouse_down_location = get_pos()

                if event.button() == QtCore.Qt.LeftButton:
                    self.__pan_x, self.__pan_y = self.__get_pan()
                    self.__mouse_left_button_down = True
                elif event.button() == QtCore.Qt.MiddleButton:
                    self.__mouse_middle_button_down = True

                    # Calculate center of image
                    geometry = self.__viewport_api.get_current_clip_geometry()
                    x_coords, y_coords = zip(*geometry)
                    center_x = sum(x_coords) / len(x_coords)
                    center_y = sum(y_coords) / len(y_coords)
                    self.__center = (center_x, center_y)

                    self.__start_vector = self.__vector_from_center(event.pos())

                elif event.button() == QtCore.Qt.RightButton:
                    self.__scale_x, self.__scale_y = self.__get_zoom()
                    self.__mouse_right_button_down = True
                return True

            if event.type() == QtCore.QEvent.MouseButtonRelease:
                self.__mouse_left_button_down = False
                self.__mouse_middle_button_down = False
                self.__mouse_right_button_down = False
                self.__mouse_down_location = None
                if self.__start_vector is not None:
                    end_vector = self.__vector_from_center(event.pos())
                    delta_angle = self.__angle_between_vectors(self.__start_vector, end_vector)
                    self.__base_angle += delta_angle
                    self.__start_vector = None
                    self.__center = None

                self.__core_view.setCursor(QtCore.Qt.OpenHandCursor)
        return False

    def __vector_from_center(self, pos):
        v = (pos.x() - self.__center[0], pos.y() - self.__center[1])
        return v

    def __angle_between_vectors(self, v1, v2):
        x1, y1 = v1
        x2, y2 = v2
        dot = x1 * x2 + y1 * y2
        det = x1 * y2 - y1 * x2
        angle = np.degrees(np.arctan2(det, dot))
        return angle

    def __move(self, x, y):
        dx = x - self.__mouse_down_location[0]
        dy = y - self.__mouse_down_location[1]
        if self.__interactive_mode == INTERACTIVE_MODE_TRANSFORM:
            self.__session_api.set_attr_values(
                [(self.__pguid, self.__cguid, StaticAttrs.pan_x, dx + self.__pan_x),
                (self.__pguid, self.__cguid, StaticAttrs.pan_y, dy + self.__pan_y)])
        else:
            src_frame = self.__get_current_clip_frame()
            self.__session_api.set_attr_values_at(
                [(self.__pguid, self.__cguid, DynamicAttrs.pan_x, src_frame, dx + self.__pan_x),
                (self.__pguid, self.__cguid, DynamicAttrs.pan_y, src_frame, dy + self.__pan_y)])

    def __scale(self, x, y):
        dx = x - self.__mouse_down_location[0]
        dy = y - self.__mouse_down_location[1]
        scale = 1.0 + 0.01 * (dx - dy)
        if self.__interactive_mode == INTERACTIVE_MODE_TRANSFORM:
            self.__session_api.set_attr_values(
                [(self.__pguid, self.__cguid, StaticAttrs.zoom_x, abs(scale * self.__scale_x)),
                (self.__pguid, self.__cguid, StaticAttrs.zoom_y, abs(scale * self.__scale_y))])
        else:
            src_frame = self.__get_current_clip_frame()
            self.__session_api.set_attr_values_at(
                [(self.__pguid, self.__cguid, DynamicAttrs.zoom_x, src_frame, abs(scale * self.__scale_x)),
                (self.__pguid, self.__cguid, DynamicAttrs.zoom_y, src_frame, abs(scale * self.__scale_y))])

    def __rotate(self, pos):
        current_vector = self.__vector_from_center(pos)
        delta_angle = self.__angle_between_vectors(self.__start_vector, current_vector)
        angle = self.__base_angle + delta_angle

        if self.__interactive_mode == INTERACTIVE_MODE_TRANSFORM:
            self.__session_api.set_attr_values(
                [(self.__pguid, self.__cguid, StaticAttrs.rotation, angle % 360)])
        else:
            attr_id = DynamicAttrs.rotation
            src_frame = self.__get_current_clip_frame()
            self.__session_api.set_attr_values_at(
                [(self.__pguid, self.__cguid, DynamicAttrs.rotation, src_frame, angle % 360)])

    def __get_pan(self):
        if self.__interactive_mode == INTERACTIVE_MODE_TRANSFORM:
            x = self.__session_api.get_attr_value(
                    self.__cguid, StaticAttrs.pan_x)
            y = self.__session_api.get_attr_value(
                    self.__cguid, StaticAttrs.pan_y)
        if self.__interactive_mode == INTERACTIVE_MODE_DYNAMIC_TRANSFORM:
            src_frame = self.__get_current_clip_frame()
            x = self.__session_api.get_attr_value_at(
                    self.__cguid, DynamicAttrs.pan_x, src_frame)
            y = self.__session_api.get_attr_value_at(
                    self.__cguid, DynamicAttrs.pan_y, src_frame)
        return x, y

    def __get_zoom(self):
        if self.__interactive_mode == INTERACTIVE_MODE_TRANSFORM:
            x = self.__session_api.get_attr_value(
                    self.__cguid, StaticAttrs.zoom_x)
            y = self.__session_api.get_attr_value(
                    self.__cguid, StaticAttrs.zoom_y)
        if self.__interactive_mode == INTERACTIVE_MODE_DYNAMIC_TRANSFORM:
            src_frame = self.__get_current_clip_frame()
            x = self.__session_api.get_attr_value_at(
                    self.__cguid, DynamicAttrs.zoom_x, src_frame)
            y = self.__session_api.get_attr_value_at(
                    self.__cguid, DynamicAttrs.zoom_y, src_frame)
        return x, y