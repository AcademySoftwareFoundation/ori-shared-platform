from dataclasses import dataclass
from functools import partial
from PySide2 import QtCore, QtGui, QtWidgets
from rpa.session_state.transforms import \
    TransformData, TransformType, DYNAMIC_TRANSFORM_ATTRS, STATIC_TRANSFORM_ATTRS, SCALE_ATTRS


class CustomDoubleValidator(QtGui.QDoubleValidator):

    def validate(self, input, pos):
        state, new_input, new_pos = super().validate(input, pos)
        if "e" in input.lower():
            return QtGui.QDoubleValidator.Invalid, input, pos
        return state, new_input, new_pos


class CustomLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.clearFocus()
        super().keyPressEvent(event)


class CustomDoubleSpinBox(QtWidgets.QDoubleSpinBox):

    arrowValueChanged = QtCore.Signal()
    typingValueChanged = QtCore.Signal()

    def stepBy(self, steps):
        super().stepBy(steps)
        self.arrowValueChanged.emit()

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.typingValueChanged.emit()
            self.clearFocus()
        super().keyPressEvent(event)


class TransformToolBar(QtWidgets.QToolBar):

    SIG_SET_TRANSFORMATION = QtCore.Signal(str, float)
    SIG_SET_MEDIA_FPS = QtCore.Signal(str, float)

    def __init__(self, actions):
        super().__init__()

        self.setWindowTitle("Transform Toolbar")
        self.setObjectName(self.windowTitle())

        self.__actions = actions
        self.__dbl_validator = CustomDoubleValidator()

        self.addAction(self.__actions.toggle_transform)
        self.addAction(self.__actions.toggle_dynamic_transform)

        self.addSeparator()

        self.addAction(self.__actions.set_transform_key)
        self.addAction(self.__actions.remove_transform_key)

        self.addSeparator()

        self.addAction(self.__actions.prev_key_frame)
        self.addAction(self.__actions.next_key_frame)

        self.addSeparator()

        self.__create_fps_menu()
        self.addSeparator()
        self.__create_pan_menu()
        self.addSeparator()
        self.__create_rotate_menu()
        self.addSeparator()
        self.__create_zoom_menu()

        self.addSeparator()

        # TODO
        # self.addAction(self.__actions.crop_transforms)
        self.addAction(self.__actions.reset_all)

    def __create_fps_menu(self):
        self.__fps_label = QtWidgets.QLabel(" Clip FPS ")

        self.__fps_spin_box = CustomDoubleSpinBox()
        self.__fps_spin_box.setMaximumWidth(80)
        self.__fps_spin_box.setToolTip("Current Clip FPS")
        self.__fps_spin_box.setDecimals(1)
        self.__fps_spin_box.setSingleStep(1.0)
        self.__fps_spin_box.setMinimum(0.0)
        self.__fps_spin_box.arrowValueChanged.connect(
            lambda: self.__set_fps(
                TransformType.fps, self.__fps_spin_box.value()))
        self.__fps_spin_box.typingValueChanged.connect(
            lambda: self.__set_fps(
                TransformType.fps, self.__fps_spin_box.value()))

        self.__fps_reset_btn = QtWidgets.QToolButton()
        self.__fps_reset_btn.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":reset_property.png")))
        self.__fps_reset_btn.setMaximumWidth(25)
        self.__fps_reset_btn.setToolTip("Reset to default Clip FPS")
        self.__fps_reset_btn.clicked.connect(
            lambda: self.__set_fps(
                TransformType.fps, TransformData.default_24))

        self.addWidget(self.__fps_label)
        self.addWidget(self.__fps_spin_box)
        self.addWidget(self.__fps_reset_btn)

    def __create_rotate_menu(self):
        # Slider
        self.__rotate_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.__rotate_slider.setMinimumWidth(500)
        self.__rotate_slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__rotate_slider.setRange(0, 360)
        self.__rotate_slider.setTickInterval(10)
        self.__rotate_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.__rotate_slider.setValue(0)
        self.__rotate_slider.valueChanged.connect(
            partial(self.__normalize_rotation_and_set, TransformType.rotate))

        # Button & Menu
        self.__rotate_menu = QtWidgets.QMenu()

        self.__rotate_btn = QtWidgets.QToolButton()
        self.__rotate_btn.setText(" Rotate ")
        self.__rotate_btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.__rotate_btn.setMenu(self.__rotate_menu)

        rotate_layout = QtWidgets.QGridLayout()
        rotate_layout.addWidget(self.__rotate_slider)

        self.__rotate_widget = QtWidgets.QWidget()
        self.__rotate_widget.setContentsMargins(5, 5, 5, 5)
        self.__rotate_widget.setLayout(rotate_layout)

        rotate_wa = QtWidgets.QWidgetAction(self)
        rotate_wa.setDefaultWidget(self.__rotate_widget)
        self.__rotate_menu.addAction(rotate_wa)

        self.addWidget(self.__rotate_btn)

        # Text Box
        self.__rotate_line_edit = CustomLineEdit(self)
        self.__rotate_line_edit.setValidator(self.__dbl_validator)
        self.__rotate_line_edit.setMaximumWidth(75)
        self.__rotate_line_edit.returnPressed.connect(
            lambda: self.__normalize_rotation_and_set(
                TransformType.rotate,
                float(self.__rotate_line_edit.text())))

        # Reset
        self.__rotate_reset_btn = QtWidgets.QToolButton()
        self.__rotate_reset_btn.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":reset_property.png")))
        self.__rotate_reset_btn.setMaximumWidth(25)
        self.__rotate_reset_btn.setToolTip("Reset Rotation")
        self.__rotate_reset_btn.clicked.connect(
            lambda: self.__normalize_rotation_and_set(
                TransformType.rotate, TransformData.default_0))

        self.addWidget(self.__rotate_line_edit)
        self.addWidget(self.__rotate_reset_btn)

    def __create_pan_menu(self):
        # Sliders
        self.__pan_x_label = QtWidgets.QLabel(" X ")
        self.__pan_x_label_2 = QtWidgets.QLabel(" X ")
        self.__pan_x_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.__pan_x_slider.setMinimumWidth(500)
        self.__pan_x_slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__pan_x_slider.setRange(-1000, 1000)
        self.__pan_x_slider.setTickInterval(100)
        self.__pan_x_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.__pan_x_slider.valueChanged.connect(
            partial(self.__set_transformation, TransformType.pan_x))

        self.__pan_y_label = QtWidgets.QLabel(" Y ")
        self.__pan_y_label_2 = QtWidgets.QLabel(" Y ")
        self.__pan_y_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.__pan_y_slider.setMinimumWidth(500)
        self.__pan_y_slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__pan_y_slider.setRange(-1000, 1000)
        self.__pan_y_slider.setTickInterval(100)
        self.__pan_y_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.__pan_y_slider.valueChanged.connect(
            partial(self.__set_transformation, TransformType.pan_y))

        # Button & Menu
        self.__pan_menu = QtWidgets.QMenu()

        self.__pan_btn = QtWidgets.QToolButton()
        self.__pan_btn.setText(" Pan ")
        self.__pan_btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.__pan_btn.setMenu(self.__pan_menu)

        pan_layout = QtWidgets.QGridLayout()
        pan_layout.addWidget(self.__pan_x_label, 0, 0)
        pan_layout.addWidget(self.__pan_x_slider, 0, 1)
        pan_layout.addWidget(self.__pan_y_label, 1, 0)
        pan_layout.addWidget(self.__pan_y_slider, 1, 1)

        self.__pan_widget = QtWidgets.QWidget()
        self.__pan_widget.setContentsMargins(5, 5, 5, 5)
        self.__pan_widget.setLayout(pan_layout)

        pan_wa = QtWidgets.QWidgetAction(self)
        pan_wa.setDefaultWidget(self.__pan_widget)
        self.__pan_menu.addAction(pan_wa)

        # Text Boxes
        self.__pan_x_edit = CustomLineEdit(self)
        self.__pan_x_edit.setValidator(self.__dbl_validator)
        self.__pan_x_edit.setMaximumWidth(75)
        self.__pan_x_edit.returnPressed.connect(
            lambda: self.__set_transformation(
                TransformType.pan_x,
                float(self.__pan_x_edit.text())))

        self.__pan_y_edit = CustomLineEdit(self)
        self.__pan_y_edit.setValidator(self.__dbl_validator)
        self.__pan_y_edit.setMaximumWidth(75)
        self.__pan_y_edit.returnPressed.connect(
            lambda: self.__set_transformation(
                TransformType.pan_y,
                float(self.__pan_y_edit.text())))

        # Reset
        self.__pan_x_reset_btn = QtWidgets.QToolButton()
        self.__pan_x_reset_btn.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":reset_property.png")))
        self.__pan_x_reset_btn.setMaximumWidth(25)
        self.__pan_x_reset_btn.setToolTip("Reset Pan X")
        self.__pan_x_reset_btn.clicked.connect(
            lambda: self.__set_transformation(
                TransformType.pan_x, TransformData.default_0))

        self.__pan_y_reset_btn = QtWidgets.QToolButton()
        self.__pan_y_reset_btn.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":reset_property.png")))
        self.__pan_y_reset_btn.setMaximumWidth(25)
        self.__pan_y_reset_btn.setToolTip("Reset Pan Y")
        self.__pan_y_reset_btn.clicked.connect(
            lambda: self.__set_transformation(
                TransformType.pan_y, TransformData.default_0))

        self.addWidget(self.__pan_btn)
        self.addWidget(self.__pan_x_label_2)
        self.addWidget(self.__pan_x_edit)
        self.addWidget(self.__pan_x_reset_btn)
        self.addWidget(self.__pan_y_label_2)
        self.addWidget(self.__pan_y_edit)
        self.addWidget(self.__pan_y_reset_btn)

    def __create_zoom_menu(self):
        # Sliders
        self.__zoom_x_label = QtWidgets.QLabel(" X ")
        self.__zoom_x_label_2 = QtWidgets.QLabel(" X ")
        self.__zoom_x_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.__zoom_x_slider.setMinimumWidth(500)
        self.__zoom_x_slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__zoom_x_slider.setMinimum(-3 * TransformData.zoom_mult)
        self.__zoom_x_slider.setMaximum(+3 * TransformData.zoom_mult)
        self.__zoom_x_slider.setTickInterval(1)
        self.__zoom_x_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.__zoom_x_slider.valueChanged.connect(
            partial(self.__check_zoom_sync_and_set,
                    TransformType.zoom_x,
                    mult=1.0/TransformData.zoom_mult))

        self.__zoom_y_label = QtWidgets.QLabel(" Y ")
        self.__zoom_y_label_2 = QtWidgets.QLabel(" Y ")
        self.__zoom_y_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.__zoom_y_slider.setMinimumWidth(500)
        self.__zoom_y_slider.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__zoom_y_slider.setMinimum(-3 * TransformData.zoom_mult)
        self.__zoom_y_slider.setMaximum(+3 * TransformData.zoom_mult)
        self.__zoom_y_slider.setTickInterval(1)
        self.__zoom_y_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.__zoom_y_slider.valueChanged.connect(
            partial(self.__check_zoom_sync_and_set,
                    TransformType.zoom_y,
                    mult=1.0/TransformData.zoom_mult))

        # Zoom XY sync
        self.__zoom_link_btn = QtWidgets.QToolButton()
        self.__zoom_link_btn.setCheckable(True)
        self.__zoom_link_btn.setToolTip("Modify Zoom X and Y together")
        self.__zoom_link_btn.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":link.png")))
        self.__zoom_link_btn.setMaximumWidth(25)

        # Button & Menu
        self.__zoom_menu = QtWidgets.QMenu()

        self.__zoom_btn = QtWidgets.QToolButton()
        self.__zoom_btn.setText(" Zoom ")
        self.__zoom_btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.__zoom_btn.setMenu(self.__zoom_menu)

        zoom_layout = QtWidgets.QGridLayout()
        zoom_layout.addWidget(self.__zoom_x_label, 0, 0)
        zoom_layout.addWidget(self.__zoom_x_slider, 0, 1)
        zoom_layout.addWidget(self.__zoom_link_btn, 0, 3, 2, 1, QtCore.Qt.AlignVCenter)
        zoom_layout.addWidget(self.__zoom_y_label, 1, 0)
        zoom_layout.addWidget(self.__zoom_y_slider, 1, 1)

        self.__zoom_widget = QtWidgets.QWidget()
        self.__zoom_widget.setContentsMargins(5,5,5,5)
        self.__zoom_widget.setLayout(zoom_layout)

        zoom_wa = QtWidgets.QWidgetAction(self)
        zoom_wa.setDefaultWidget(self.__zoom_widget)
        self.__zoom_menu.addAction(zoom_wa)

        # Text Boxes
        self.__zoom_x_edit = CustomLineEdit(self)
        self.__zoom_x_edit.setValidator(self.__dbl_validator)
        self.__zoom_x_edit.setMaximumWidth(75)
        self.__zoom_x_edit.returnPressed.connect(
            lambda: self.__check_zoom_sync_and_set(
                TransformType.zoom_x,
                float(self.__zoom_x_edit.text())))

        self.__zoom_y_edit = CustomLineEdit(self)
        self.__zoom_y_edit.setValidator(self.__dbl_validator)
        self.__zoom_y_edit.setMaximumWidth(75)
        self.__zoom_y_edit.returnPressed.connect(
            lambda: self.__check_zoom_sync_and_set(
                TransformType.zoom_y,
                float(self.__zoom_y_edit.text())))

        # Reset
        self.__zoom_x_reset_btn = QtWidgets.QToolButton()
        self.__zoom_x_reset_btn.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":reset_property.png")))
        self.__zoom_x_reset_btn.setMaximumWidth(25)
        self.__zoom_x_reset_btn.setToolTip("Reset Zoom X")
        self.__zoom_x_reset_btn.clicked.connect(
            lambda: self.__check_zoom_sync_and_set(
                TransformType.zoom_x,
                TransformData.default_1))

        self.__zoom_y_reset_btn = QtWidgets.QToolButton()
        self.__zoom_y_reset_btn.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":reset_property.png")))
        self.__zoom_y_reset_btn.setMaximumWidth(25)
        self.__zoom_y_reset_btn.setToolTip("Reset Zoom Y")
        self.__zoom_y_reset_btn.clicked.connect(
            lambda: self.__check_zoom_sync_and_set(
                TransformType.zoom_y,
                TransformData.default_1))

        self.addWidget(self.__zoom_btn)
        self.addWidget(self.__zoom_x_label_2)
        self.addWidget(self.__zoom_x_edit)
        self.addWidget(self.__zoom_x_reset_btn)
        self.addWidget(self.__zoom_y_label_2)
        self.addWidget(self.__zoom_y_edit)
        self.addWidget(self.__zoom_y_reset_btn)

    def __normalize_rotation_and_set(self, transform_type, value):
        if value != 360:
            value = value % 360
            value = value if value >= 0 else value - 360
        self.__set_transformation(transform_type, value)

    def __check_zoom_sync_and_set(self, transform_type, value, mult=1.0):
        value = float(value) * mult
        if self.__zoom_link_btn.isChecked():
            self.__set_transformation(TransformType.zoom_x, value)
            self.__set_transformation(TransformType.zoom_y, value)
        else:
            self.__set_transformation(transform_type, value)

    def __set_transformation(self, transform_type, value):
        if transform_type == TransformType.rotate:
            self.__update_rotate_menu(value)
        if transform_type == TransformType.pan_x:
            self.__update_pan_x_menu(value)
        if transform_type == TransformType.pan_y:
            self.__update_pan_y_menu(value)
        if transform_type == TransformType.zoom_x:
            self.__update_zoom_x_menu(value)
        if transform_type == TransformType.zoom_y:
            self.__update_zoom_y_menu(value)

        self.SIG_SET_TRANSFORMATION.emit(transform_type, value)

    def __set_fps(self, transform_type, value):
        if transform_type != TransformType.fps:
            return

        self.SIG_SET_MEDIA_FPS.emit(transform_type, value)

        self.__fps_spin_box.blockSignals(True)
        self.__fps_spin_box.clearFocus()
        self.__fps_spin_box.blockSignals(False)

    def get_rotation_str(self):
        return self.__rotate_line_edit.text()

    def get_pan_x_str(self):
        return self.__pan_x_edit.text()

    def get_pan_y_str(self):
        return self.__pan_y_edit.text()

    def get_zoom_x_str(self):
        return self.__zoom_x_edit.text()

    def get_zoom_y_str(self):
        return self.__zoom_y_edit.text()

    def get_fps(self):
        return self.__fps_spin_box.value()

    def get_transformations(self):
        transformation_values = []

        transformation_values.append(self.get_rotation_str())
        transformation_values.append(self.get_pan_x_str())
        transformation_values.append(self.get_pan_y_str())
        transformation_values.append(self.get_zoom_x_str())
        transformation_values.append(self.get_zoom_y_str())

        if self.__actions.toggle_dynamic_transform.isChecked():
            attr_ids = DYNAMIC_TRANSFORM_ATTRS
        else:
            attr_ids = STATIC_TRANSFORM_ATTRS

        transformation_set = {}
        for attr_id, transform_value in zip(attr_ids, transformation_values):
            if transform_value != "":
                transform_value = float(transform_value)
            else:
                transform_value = self.__reassign_empty_value(attr_id)
            transformation_set[attr_id] = transform_value

        return transformation_set

    def __reassign_empty_value(self, attr_id):
        if attr_id in SCALE_ATTRS:
            transform = {attr_id:TransformData.default_1}
            default = TransformData.default_1
        else:
            transform = {attr_id:TransformData.default_0}
            default = TransformData.default_0
        self.update(transform)
        return default

    def update(self, transforms:dict):
        for attr_id, value in transforms.items():
            if attr_id not in \
                STATIC_TRANSFORM_ATTRS + DYNAMIC_TRANSFORM_ATTRS:
                continue

            if attr_id == STATIC_TRANSFORM_ATTRS[0] or \
                attr_id == DYNAMIC_TRANSFORM_ATTRS[0]:
                self.__update_rotate_menu(value)
            elif attr_id == STATIC_TRANSFORM_ATTRS[1] or \
                attr_id == DYNAMIC_TRANSFORM_ATTRS[1]:
                self.__update_pan_x_menu(value)
            elif attr_id == STATIC_TRANSFORM_ATTRS[2] or \
                attr_id == DYNAMIC_TRANSFORM_ATTRS[2]:
                self.__update_pan_y_menu(value)
            elif attr_id == STATIC_TRANSFORM_ATTRS[3] or \
                attr_id == DYNAMIC_TRANSFORM_ATTRS[3]:
                self.__update_zoom_x_menu(value)
            elif attr_id == STATIC_TRANSFORM_ATTRS[4] or \
                attr_id == DYNAMIC_TRANSFORM_ATTRS[4]:
                self.__update_zoom_y_menu(value)

    def update_fps(self, fps):
        self.__update_fps_menu(fps)

    def clear_all(self):
        self.blockSignals(True)
        self.__rotate_slider.setValue(0)
        self.__rotate_line_edit.clear()
        self.__pan_x_slider.setValue(0)
        self.__pan_x_edit.clear()
        self.__pan_y_slider.setValue(0)
        self.__pan_y_edit.clear()
        self.__zoom_x_slider.setValue(1.0)
        self.__zoom_x_edit.clear()
        self.__zoom_y_slider.setValue(1.0)
        self.__zoom_y_edit.clear()
        self.__fps_spin_box.setValue(self.__fps_spin_box.minimum())
        self.blockSignals(False)

    def __convert_to_formatted_float(self, value)->float:
        # value can be empty string, stringfied numbers, float or int
        if value is None:
            return

        if value == "":
            return value

        if isinstance(value, str) or isinstance(value, int):
            return float(value)

        if "." in str(value):
            decimal_points = len(str(value).split(".")[1])
            if decimal_points <= 4:
                return value

        return float(f"{value:.4f}")

    def __update_rotate_menu(self, rotation):

        rotation = self.__convert_to_formatted_float(rotation)
        current_rotation = self.__convert_to_formatted_float(self.get_rotation_str())
        current_slider = self.__convert_to_formatted_float(self.__rotate_slider.value())

        if current_rotation != rotation and rotation != "":
            self.__rotate_line_edit.blockSignals(True)
            self.__rotate_line_edit.setText(str(rotation))
            self.__rotate_line_edit.clearFocus()
            self.__rotate_line_edit.blockSignals(False)

        if current_slider != rotation and rotation != "":
            self.__rotate_slider.blockSignals(True)
            self.__rotate_slider.setValue(float(rotation))
            self.__rotate_slider.blockSignals(False)

    def __update_pan_x_menu(self, pan_x):

        pan_x = self.__convert_to_formatted_float(pan_x)
        current_pan_x = self.__convert_to_formatted_float(self.get_pan_x_str())
        current_slider = self.__convert_to_formatted_float(self.__pan_x_slider.value())

        if current_pan_x != pan_x and pan_x != "":
            self.__pan_x_edit.blockSignals(True)
            self.__pan_x_edit.setText(str(pan_x))
            self.__pan_x_edit.clearFocus()
            self.__pan_x_edit.blockSignals(False)

        if current_slider != pan_x and pan_x != "":
            self.__pan_x_slider.blockSignals(True)
            self.__pan_x_slider.setValue(float(pan_x))
            self.__pan_x_slider.blockSignals(False)

    def __update_pan_y_menu(self, pan_y):

        pan_y = self.__convert_to_formatted_float(pan_y)
        current_pan_y = self.__convert_to_formatted_float(self.get_pan_y_str())
        current_slider = self.__convert_to_formatted_float(self.__pan_y_slider.value())

        if current_pan_y != pan_y and pan_y != "":
            self.__pan_y_edit.blockSignals(True)
            self.__pan_y_edit.setText(str(pan_y))
            self.__pan_y_edit.clearFocus()
            self.__pan_y_edit.blockSignals(False)

        if current_slider != pan_y and pan_y != "":
            self.__pan_y_slider.blockSignals(True)
            self.__pan_y_slider.setValue(float(pan_y))
            self.__pan_y_slider.blockSignals(False)

    def __update_zoom_x_menu(self, zoom_x):

        zoom_x = self.__convert_to_formatted_float(zoom_x)
        current_zoom_x = self.__convert_to_formatted_float(self.get_zoom_x_str())
        current_zoom_y = self.__convert_to_formatted_float(self.get_zoom_y_str())
        current_slider = self.__convert_to_formatted_float(self.__zoom_x_slider.value())

        if current_zoom_x != zoom_x and zoom_x != "":
            self.__zoom_x_edit.blockSignals(True)
            self.__zoom_x_edit.setText(str(zoom_x))
            self.__zoom_x_edit.clearFocus()
            self.__zoom_x_edit.blockSignals(False)

        if current_slider != zoom_x and zoom_x != "":
            self.__zoom_x_slider.blockSignals(True)
            self.__zoom_x_slider.setValue(float(zoom_x * TransformData.zoom_mult))
            self.__zoom_x_slider.blockSignals(False)

        if self.__zoom_link_btn.isChecked():
            new_zoom_x = self.__convert_to_formatted_float(self.get_zoom_x_str())
            if current_zoom_y != new_zoom_x and new_zoom_x != "":
                self.__zoom_y_edit.blockSignals(True)
                self.__zoom_y_edit.setText(str(new_zoom_x))
                self.__zoom_y_edit.clearFocus()
                self.__zoom_y_edit.blockSignals(False)

                self.__zoom_y_slider.blockSignals(True)
                self.__zoom_y_slider.setValue(float(new_zoom_x * TransformData.zoom_mult))
                self.__zoom_y_slider.blockSignals(False)

    def __update_zoom_y_menu(self, zoom_y):

        zoom_y = self.__convert_to_formatted_float(zoom_y)
        current_zoom_x = self.__convert_to_formatted_float(self.get_zoom_x_str())
        current_zoom_y = self.__convert_to_formatted_float(self.get_zoom_y_str())
        current_slider = self.__convert_to_formatted_float(self.__zoom_y_slider.value())

        if current_zoom_y != zoom_y and zoom_y != "":
            self.__zoom_y_edit.blockSignals(True)
            self.__zoom_y_edit.setText(str(zoom_y))
            self.__zoom_y_edit.clearFocus()
            self.__zoom_y_edit.blockSignals(False)

        if current_slider != zoom_y and zoom_y != "":
            self.__zoom_y_slider.blockSignals(True)
            self.__zoom_y_slider.setValue(float(zoom_y * TransformData.zoom_mult))
            self.__zoom_y_slider.blockSignals(False)

        if self.__zoom_link_btn.isChecked():
            new_zoom_y = self.__convert_to_formatted_float(self.get_zoom_y_str())
            if current_zoom_x != new_zoom_y and new_zoom_y != "":
                self.__zoom_x_edit.blockSignals(True)
                self.__zoom_x_edit.setText(str(new_zoom_y))
                self.__zoom_x_edit.clearFocus()
                self.__zoom_x_edit.blockSignals(False)

                self.__zoom_x_slider.blockSignals(True)
                self.__zoom_x_slider.setValue(float(new_zoom_y * TransformData.zoom_mult))
                self.__zoom_x_slider.blockSignals(False)

    def __update_fps_menu(self, fps):
        if not fps:
            return

        fps = self.__convert_to_formatted_float(fps)
        current_fps = self.__convert_to_formatted_float(self.get_fps())

        if current_fps != fps:
            self.__fps_spin_box.blockSignals(True)
            self.__fps_spin_box.setValue(float(fps))
            self.__fps_spin_box.blockSignals(False)
