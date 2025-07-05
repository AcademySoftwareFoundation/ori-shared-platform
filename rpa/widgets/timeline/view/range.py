try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtWidgets import QAction
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QAction
from rpa.widgets.timeline.view.line_edit import TimelineLineEdit


class TimelineRange(QtWidgets.QToolBar):
    SIG_START_FRAME_RANGE_CHANGED = QtCore.Signal(int)  # key in frame
    SIG_CURR_FRAME_RANGE_CHANGED = QtCore.Signal(int)  # current frame
    SIG_END_FRAME_RANGE_CHANGED = QtCore.Signal(int)  # key out frame

    SIG_START_FRAME_EDITING_CANCELLED = QtCore.Signal()
    SIG_CURR_FRAME_EDITING_CANCELLED = QtCore.Signal()
    SIG_END_FRAME_EDITING_CANCELLED = QtCore.Signal()

    SIG_RANGE_SCOPE_CHANGED = QtCore.Signal()
    SIG_RANGE_DISPLAY_MODE_CHANGED = QtCore.Signal()

    def __init__(self, parent, range_scope):
        QtWidgets.QToolBar.__init__(self, parent)

        self.__number_validator = QtGui.QRegularExpressionValidator(
            QtCore.QRegularExpression("-?\\d+"), None)

        self.__range_scope = range_scope
        self.__range_scope_action_group = action_group = QActionGroup(self)
        self.__range_scope_seq_action = QAction("Sequence", action_group)
        self.__range_scope_seq_action.setCheckable(True)
        self.__range_scope_clip_action = QAction("Clip", action_group)
        self.__range_scope_clip_action.setCheckable(True)
        action_group.setExclusive(True)
        action_group.triggered.connect(self.__range_scope_selected)

        self.__range_display_mode_ag = action_group = QActionGroup(self)
        self.__range_display_mode_frames_action = QAction("Frames", action_group)
        self.__range_display_mode_frames_action.setCheckable(True)
        self.__range_display_mode_timecode_action = QAction("Timecode", action_group)
        self.__range_display_mode_timecode_action.setCheckable(True)
        self.__range_display_mode_feet_action = QAction("Feet", action_group)
        self.__range_display_mode_feet_action.setCheckable(True)
        action_group.setExclusive(True)
        action_group.triggered.connect(self.__range_display_mode_selected)

        self.__clip_position_actions = (self.__range_scope_seq_action,
                                        self.__range_scope_clip_action,
                                        'separator',
                                        self.__range_display_mode_frames_action,
                                        self.__range_display_mode_timecode_action,
                                        self.__range_display_mode_feet_action)

        self.__start_frame_text = self.__add_timeline_range_box(lambda: self.SIG_START_FRAME_EDITING_CANCELLED.emit(),
                                                                tooltip="Start Frame")
        self.__cur_frame_text = self.__add_timeline_range_box(lambda: self.SIG_CURR_FRAME_EDITING_CANCELLED.emit(),
                                                              tooltip="Current Frame")
        self.__end_frame_text = self.__add_timeline_range_box(lambda: self.SIG_END_FRAME_EDITING_CANCELLED.emit(),
                                                              tooltip="End Frame")
        self.__total_text = self.__add_timeline_range_box(None,
                                                          tooltip="Total")
        self.__enable_range_widget(self.__total_text, False)

        # Connecting range buttons signals
        self.__start_frame_text.editingFinished.connect(self.__range_start_changed)
        self.__cur_frame_text.editingFinished.connect(self.__range_cur_changed)
        self.__end_frame_text.editingFinished.connect(self.__range_end_changed)

        self.__load_defaults()

    def __add_timeline_range_box(self, cancelf, tooltip=None):
        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.setContentsMargins(4, 4, 4, 4)
        vbox_layout.setSpacing(0)

        edit = TimelineLineEdit(self.__clip_position_actions, cancelf)
        edit.setFixedHeight(edit.fontMetrics().ascent() + 8)
        if tooltip:
            edit.setToolTip(tooltip)
        edit.setValidator(self.__number_validator)
        vbox_layout.addWidget(edit)
        widget = QtWidgets.QWidget(self)
        widget.setLayout(vbox_layout)
        self.addWidget(widget)
        return edit

    def set_range_key_in(self, key_in):
        self.__start_frame_text.setText(str(key_in))

    def set_range_key_out(self, key_out):
        self.__end_frame_text.setText(str(key_out))

    def set_current_frame(self, current_frame):
        self.__cur_frame_text.setText(str(current_frame))

    def set_range_total(self, total):
        self.__total_text.setText(str(total))

    def __range_start_changed(self):
        if not self.__start_frame_text.isModified() or not self.__start_frame_text.hasAcceptableInput():
            return

        key_in = self.__get_clip_frame(self.__start_frame_text)
        self.SIG_START_FRAME_RANGE_CHANGED.emit(key_in)

    def __range_cur_changed(self):
        if not self.__cur_frame_text.isModified() or not self.__cur_frame_text.hasAcceptableInput():
            return

        frame = self.__get_clip_frame(self.__cur_frame_text)
        self.SIG_CURR_FRAME_RANGE_CHANGED.emit(frame)

    def __range_end_changed(self):
        if not self.__end_frame_text.isModified() or not self.__end_frame_text.hasAcceptableInput():
            return
        if self.__range_scope.is_sequence_scope() or self.__range_scope.is_display_mode_timecode() \
                or self.__range_scope.is_display_mode_feet():
            return

        key_out = self.__get_clip_frame(self.__end_frame_text)
        self.SIG_END_FRAME_RANGE_CHANGED.emit(key_out)

    def __range_scope_selected(self, action):
        if action is self.__range_scope_seq_action:
            self.__range_scope.set_sequence_scope()
            self.__enable_range_in_out(False)
            self.__enable_range_cur(self.__range_scope.is_display_mode_frame())
        if action is self.__range_scope_clip_action:
            self.__range_scope.set_clip_scope()
            self.__enable_range_in_out(self.__range_scope.is_display_mode_frame())
            self.__enable_range_cur(self.__range_scope.is_display_mode_frame())

        self.SIG_RANGE_SCOPE_CHANGED.emit()

    def __range_display_mode_selected(self, action):
        display_text = ' 00000 '
        if action is self.__range_display_mode_frames_action:
            self.__range_scope.set_display_mode_frame()
            self.__enable_range_in_out(self.__range_scope.is_clip_scope())
            self.__enable_range_cur(True)
            display_text = ' 00000 '
        if action is self.__range_display_mode_timecode_action:
            self.__range_scope.set_display_mode_timecode()
            self.__enable_range_in_out(False)
            self.__enable_range_cur(False)
            display_text = ' 00:00:00.00 '
        if action is self.__range_display_mode_feet_action:
            self.__range_scope.set_display_mode_feet()
            self.__enable_range_in_out(False)
            self.__enable_range_cur(False)
            display_text = ' 00000.000 '

        for range_edit in (self.__cur_frame_text,
                           self.__start_frame_text,
                           self.__end_frame_text,
                           self.__total_text):
            range_edit.set_width_mode(display_text)

        for range_edit in (self.__cur_frame_text,
                           self.__start_frame_text,
                           self.__end_frame_text):
            range_edit.set_tool_tip_mode(action.toolTip())

        self.SIG_RANGE_DISPLAY_MODE_CHANGED.emit()

    def __load_defaults(self):
        if self.__range_scope.is_sequence_scope():
            self.__range_scope_seq_action.setChecked(True)
            self.__range_scope_selected(self.__range_scope_seq_action)
        else:
            self.__range_scope_clip_action.setChecked(True)
            self.__range_scope_selected(self.__range_scope_clip_action)
        if self.__range_scope.is_display_mode_frame():
            self.__range_display_mode_frames_action.setChecked(True)
            self.__range_display_mode_selected(self.__range_display_mode_frames_action)
        elif self.__range_scope.is_display_mode_timecode():
            self.__range_display_mode_timecode_action.setChecked(True)
            self.__range_display_mode_selected(self.__range_display_mode_timecode_action)
        elif self.__range_scope.is_display_mode_feet():
            self.__range_display_mode_feet_action.setChecked(True)
            self.__range_display_mode_selected(self.__range_display_mode_feet_action)

    @staticmethod
    def __enable_range_widget(widget, enable):
        widget.setReadOnly(not enable)

        palette = QtGui.QPalette()
        if not enable:
            color = QtCore.Qt.darkGray
            palette.setColor(widget.backgroundRole(), color)

        widget.setPalette(palette)

    def __enable_range_in_out(self, enable):
        self.__enable_range_widget(self.__start_frame_text, enable)
        self.__enable_range_widget(self.__end_frame_text, enable)

    def __enable_range_cur(self, enable):
        self.__enable_range_widget(self.__cur_frame_text, enable)

    def __get_clip_frame(self, widget):
        v = str(widget.text())
        if v == "":
            return 0
        return int(v)
