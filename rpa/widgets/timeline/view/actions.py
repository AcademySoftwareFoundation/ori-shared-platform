try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtWidgets import QAction
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QAction
from rpa.widgets.timeline.view import svg


class Actions(QtCore.QObject):
    SIG_PLAY_TOGGLED = QtCore.Signal(bool)
    SIG_PLAY_FORWARDS_TOGGLED = QtCore.Signal(bool)
    SIG_PLAY_BACKWARDS_TOGGLED = QtCore.Signal(bool)
    SIG_STEP_FORWARDS_TRIGGERED = QtCore.Signal()
    SIG_STEP_BACKWARDS_TRIGGERED = QtCore.Signal()
    SIG_MUTE_TOGGLED = QtCore.Signal(bool)
    SIG_VOLUME_CHANGED = QtCore.Signal(int)
    SIG_AUDIO_SCRUBBING_TOGGLED = QtCore.Signal(bool)
    SIG_PLAYBACK_MODE_CHANGED = QtCore.Signal(int)

    def __init__(self, main_window):
        super().__init__()
        self.__main_window = main_window

        self.__create_icons()

        self.step_forward_action = QAction("Step Forward")
        self.step_forward_action.setShortcut(QtGui.QKeySequence("Right"))
        self.step_forward_action.setIcon(self.__step_forward_icon)
        self.step_forward_action.triggered.connect(self.SIG_STEP_FORWARDS_TRIGGERED.emit)

        self.step_backward_action = QAction("Step Backward")
        self.step_backward_action.setShortcut(QtGui.QKeySequence("Left"))
        self.step_backward_action.setIcon(self.__step_backward_icon)
        self.step_backward_action.triggered.connect(self.SIG_STEP_BACKWARDS_TRIGGERED.emit)

        self.toggle_play_action = QAction("Play", self.__main_window)
        self.toggle_play_action.setShortcut(QtGui.QKeySequence("Space"))
        self.toggle_play_action.setCheckable(True)
        self.toggle_play_action.setChecked(False)
        self.toggle_play_action.triggered.connect(
            lambda state: self.SIG_PLAY_TOGGLED.emit(state)
        )

        self.toggle_play_forward_action = QAction("Play Forward")
        self.toggle_play_forward_action.setShortcut(QtGui.QKeySequence("Up"))
        self.toggle_play_forward_action.setCheckable(True)
        self.toggle_play_forward_action.setChecked(False)
        self.toggle_play_forward_action.triggered.connect(
            lambda state: self.SIG_PLAY_FORWARDS_TOGGLED.emit(state)
        )

        self.toggle_play_backward_action = QAction("Play Backward")
        self.toggle_play_backward_action.setShortcut(QtGui.QKeySequence("Down"))
        self.toggle_play_backward_action.setCheckable(True)
        self.toggle_play_backward_action.setChecked(False)
        self.toggle_play_backward_action.triggered.connect(
            lambda state: self.SIG_PLAY_BACKWARDS_TOGGLED.emit(state)
        )

        # Audio
        self.volume_button = QtWidgets.QToolButton()
        self.volume_button.setToolTip("Audio Volume")
        self.volume_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.volume_button.clicked.connect(self.__toggle_volume_slider)

        self.volume_menu = QtWidgets.QMenu()

        self.toggle_mute_action = QAction("Mute")
        self.toggle_mute_action.setShortcut(QtGui.QKeySequence("M"))
        self.toggle_mute_action.setCheckable(True)
        self.toggle_mute_action.triggered.connect(
            lambda checked: self.toggle_mute(checked, False))

        self.mute_checkbox = QtWidgets.QCheckBox("Mute", self.volume_menu)
        self.mute_action = QtWidgets.QWidgetAction(self.volume_menu)
        self.mute_action.setDefaultWidget(self.mute_checkbox)
        self.mute_checkbox.stateChanged.connect(self.toggle_mute_checkbox)

        self.volume_slider = \
            QtWidgets.QSlider(QtCore.Qt.Vertical, self.volume_menu)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.set_volume_action = QtWidgets.QWidgetAction(self.volume_menu)
        self.set_volume_action.setDefaultWidget(self.volume_slider)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.update_volume_button_icon(
            self.volume_slider.value(), self.mute_checkbox.isChecked())

        self.volume_menu.addAction(self.set_volume_action)
        self.volume_menu.addAction(self.mute_action)

        self.toggle_audio_scrubbing_action = \
            QAction("Audio Scrubbing")
        self.toggle_audio_scrubbing_action.setShortcut(
            QtGui.QKeySequence("Ctrl+Shift+R"))
        self.toggle_audio_scrubbing_action.setCheckable(True)
        self.toggle_audio_scrubbing_action.triggered.connect(
            lambda state: self.SIG_AUDIO_SCRUBBING_TOGGLED.emit(state)
        )

        # Playback Modes
        self.playback_repeat_action = QAction("Playback Repeat", checkable=True)
        self.playback_repeat_action.triggered.connect(self.set_playback_mode)
        self.playback_repeat_action.setChecked(True) # Default
        self.playback_once_action = QAction("Playback Once", checkable=True)
        self.playback_once_action.triggered.connect(self.set_playback_mode)
        self.playback_swing_action = QAction("Playback Swing", checkable=True)
        self.playback_swing_action.triggered.connect(self.set_playback_mode)
        playback_mode_ag = QActionGroup(self)
        playback_mode_ag.addAction(self.playback_repeat_action)
        playback_mode_ag.addAction(self.playback_once_action)
        playback_mode_ag.addAction(self.playback_swing_action)

    def __create_icons(self):
        color = "#ffe1e1"
        self.__pause_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(
            QtGui.QImage.fromData(
                svg.PAUSE_SVG.format(color).encode("utf-8"))))

        self.__play_forward_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(
            QtGui.QImage.fromData(
                svg.PLAY_FORWARD_SVG.format(color).encode("utf-8"))))

        self.__play_backward_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(
            QtGui.QImage.fromData(
                svg.PLAY_BACKWARD_SVG.format(color).encode("utf-8"))))

        self.__step_forward_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(
            QtGui.QImage.fromData(
                svg.STEP_FORWARD_SVG.format(color).encode("utf-8"))))

        self.__step_backward_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(
            QtGui.QImage.fromData(
                svg.STEP_BACKWARD_SVG.format(color).encode("utf-8"))))

        self.__off_volume_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(
            QtGui.QImage.fromData(
                svg.OFF_VOLUME_SVG.format(color).encode("utf-8"))))

        self.__low_volume_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(
            QtGui.QImage.fromData(
                svg.LOW_VOLUME_SVG.format(color).encode("utf-8"))))

        self.__mid_volume_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(
            QtGui.QImage.fromData(
                svg.MED_VOLUME_SVG.format(color).encode("utf-8"))))

        self.__high_volume_icon = QtGui.QIcon(QtGui.QPixmap.fromImage(
            QtGui.QImage.fromData(
                svg.HIGH_VOLUME_SVG.format(color).encode("utf-8"))))

    def set_play_status(self, playing, forward):
        self.toggle_play_action.setText("Pause" if playing else "Play")
        self.toggle_play_action.setIcon(
            self.__pause_icon if playing else (
                self.__play_forward_icon if forward else self.__play_backward_icon))
        self.toggle_play_action.setChecked(playing)
        self.toggle_play_forward_action.setText(
            "Pause" if playing and forward else "Play Forward")
        self.toggle_play_forward_action.setIcon(
            self.__pause_icon if playing and forward else self.__play_forward_icon)
        self.toggle_play_forward_action.setChecked(playing and forward)
        self.toggle_play_backward_action.setText(
            "Pause" if playing and not forward else "Play Backward")
        self.toggle_play_backward_action.setIcon(
            self.__pause_icon if playing and not forward else self.__play_backward_icon)
        self.toggle_play_backward_action.setChecked(playing and not forward)

    def toggle_mute(self, checked, emit_signal=True):
        self.blockSignals(True)
        self.mute_checkbox.setChecked(checked)
        self.update_volume_button_icon(self.volume_slider.value(), checked)
        self.blockSignals(False)
        if emit_signal:
            self.SIG_MUTE_TOGGLED.emit(checked)

    def toggle_mute_checkbox(self, state):
        checked = state == 2
        self.blockSignals(True)
        self.toggle_mute_action.setChecked(checked)
        self.update_volume_button_icon(self.volume_slider.value(), checked)
        self.blockSignals(False)
        self.SIG_MUTE_TOGGLED.emit(checked)

    def set_volume(self, volume, emit_signal=True):
        if self.volume_slider.value() != volume:
            self.blockSignals(True)
            self.volume_slider.setValue(volume)
            self.blockSignals(False)
        self.update_volume_button_icon(
            volume, self.mute_checkbox.isChecked())
        if emit_signal:
            self.SIG_VOLUME_CHANGED.emit(volume)

    def update_volume_button_icon(self, volume, muted):
        if muted or volume == 0:
            self.volume_button.setIcon(self.__off_volume_icon)
        elif volume < 34:
            self.volume_button.setIcon(self.__low_volume_icon)
        elif volume < 67:
            self.volume_button.setIcon(self.__mid_volume_icon)
        else:
            self.volume_button.setIcon(self.__high_volume_icon)

    def __toggle_volume_slider(self):
        pos = self.volume_button.mapToGlobal(
            self.volume_button.rect().topLeft())
        pos.setX(pos.x() - self.volume_menu.sizeHint().width() + \
                 self.volume_button.sizeHint().width())
        pos.setY(pos.y() - self.volume_menu.sizeHint().height())
        self.volume_menu.move(pos)
        self.volume_menu.show()

    def get_volume(self):
        return self.volume_slider.value()

    def get_mute_state(self):
        mute_state = self.mute_checkbox.isChecked()
        return True if mute_state else False

    def set_playback_mode(self):
        repeat = self.playback_repeat_action.isChecked()
        once = self.playback_once_action.isChecked()
        swing = self.playback_swing_action.isChecked()

        if repeat:
            mode = 0 # repeat
        elif once:
            mode = 1 # once
        elif swing:
            mode = 2 # swing

        self.SIG_PLAYBACK_MODE_CHANGED.emit(mode)
