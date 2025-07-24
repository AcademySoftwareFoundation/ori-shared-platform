import time
from collections import namedtuple
from contextlib import contextmanager
from functools import partial
try:
    from PySide2 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets


class SplitterHandle(QtWidgets.QSplitterHandle):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)

        self.__hovered = False
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if self.__hovered:
            painter.fillRect(self.rect(), QtGui.QColor('lightgray'))

    def enterEvent(self, event):
        self.__hovered = True
        self.update()

    def leaveEvent(self, event):
        self.__hovered = False
        self.update()


class Splitter(QtWidgets.QSplitter):

    SplitterAnimation = namedtuple(
        'SplitterAnimation', ['start_sizes', 'target_sizes', 'anim_end'])

    PLAYLIST_PANEL_INDEX = 0
    CLIPS_TABLE_INDEX = 1

    ANIM_LENGTH = 120
    PLAYLIST_PANEL_DEFAULT_SIZE = 200

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__ignore_child_event = False
        self.__animating = False
        self.__animation_timer = None
        self.__target_sizes = None
        self.__opened_panel_size = Splitter.PLAYLIST_PANEL_DEFAULT_SIZE

        self.__add_toggle_button()

        self.splitterMoved.connect(self.__splitter_moved)

    def createHandle(self):
        handle = SplitterHandle(self.orientation(), self)
        return handle

    def resizeEvent(self, event):
        self.__toggle_button.setGeometry(
            10,
            event.size().height() - self.__toggle_button.height() - 10,
            self.__toggle_button.width(),
            self.__toggle_button.height())
        return super().resizeEvent(event)

    def childEvent(self, event):
        if self.__ignore_child_event:
            return

        super().childEvent(event)

    def __add_toggle_button(self):
        self.__ignore_child_event = True

        self.__toggle_button = QtWidgets.QPushButton(
            parent=self,
            geometry=QtCore.QRect(0, 0, 26, 26),
            icon=self.style().standardIcon(QtWidgets.QStyle.SP_ArrowRight))
        self.__toggle_button.clicked.connect(self.__toggle_left_pane)

        self.__ignore_child_event = False

    def handle_restored_state(self):
        vertical_tab_size = self.sizes()[Splitter.PLAYLIST_PANEL_INDEX]
        self.__update_icons(vertical_tab_size)

        if self.sizes()[0] != 0:
            self.__opened_panel_size = vertical_tab_size
        else:
            self.__opened_panel_size = \
                Splitter.PLAYLIST_PANEL_DEFAULT_SIZE

    def set_state(self, state):
        if state:
            self.restoreState(state)
        else:
            self.setSizes([0, 1])
        self.handle_restored_state()

    def __update_icons(self, size):
        if size == 0:
            self.__toggle_button.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_ArrowRight))
            self.__toggle_button.setToolTip('Show playlist panel')
        else:
            self.__toggle_button.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.SP_ArrowLeft))
            self.__toggle_button.setToolTip('Hide playlist panel')

    def __toggle_left_pane(self):

        with self.__animate_context() as cur_sizes:
            orig_sizes = tuple(cur_sizes)
            if self.__opened_panel_size != \
                cur_sizes[Splitter.PLAYLIST_PANEL_INDEX] \
                and cur_sizes[Splitter.PLAYLIST_PANEL_INDEX] != 0:
                self.__opened_panel_size = cur_sizes[0]
            if cur_sizes[Splitter.PLAYLIST_PANEL_INDEX] == 0:
                cur_sizes[Splitter.CLIPS_TABLE_INDEX] -= \
                    self.__opened_panel_size
                cur_sizes[Splitter.PLAYLIST_PANEL_INDEX] = \
                    self.__opened_panel_size
            else:
                cur_sizes[Splitter.CLIPS_TABLE_INDEX] += \
                    cur_sizes[Splitter.PLAYLIST_PANEL_INDEX]
                cur_sizes[Splitter.PLAYLIST_PANEL_INDEX] = 0
            self.__target_sizes = Splitter.SplitterAnimation(
                orig_sizes,
                tuple(cur_sizes),
                time.time() + Splitter.ANIM_LENGTH / 1000.0)

    @contextmanager
    def __animate_context(self):
        """Animate the panel(s) to a new position. Stop any current
        animation.
        Context is provided cur_sizes. The context is expected to
        modify self.__target_sizes. If not, the original animation
        will continue (if any).
        """
        if self.__animating:
            self.__animation_timer.stop()
            self.__animating = False
            cur_sizes = self.__target_sizes.target_sizes
        else:
            cur_sizes = self.sizes()
        orig_target = self.__target_sizes
        self.__target_sizes = None

        try:
            yield list(cur_sizes)
        finally:
            if self.__target_sizes is None:
                self.__target_sizes = orig_target

            if self.__target_sizes is not None:
                if self.__animation_timer is None:
                    self.__animation_timer = QtCore.QTimer(self)
                    self.__animation_timer.timeout.connect(self.__animate)
                self.__animation_timer.start(1000//60)
                self.__animating = True


    @staticmethod
    def linear_interpolation(a, b, t):
        return a + (b - a) * t

    @QtCore.Slot()
    def __animate(self):
        if not self.__animating or not self.__target_sizes:
            return
        now = time.time()
        if now >= self.__target_sizes.anim_end:
            self.setSizes(self.__target_sizes.target_sizes)
            self.__update_icons(self.__target_sizes.target_sizes)
            self.__animation_timer.stop()
            self.__animating = False
            self.__target_sizes = None

            self.__splitter_moved()
            return

        anim_len_in_millis = Splitter.ANIM_LENGTH / 1000.0
        anim_start = self.__target_sizes.anim_end - anim_len_in_millis
        perc = (now - anim_start) / anim_len_in_millis
        tot = sum(self.__target_sizes.target_sizes)
        tab_size = self.linear_interpolation(
            self.__target_sizes.start_sizes[Splitter.PLAYLIST_PANEL_INDEX],
            self.__target_sizes.target_sizes[Splitter.PLAYLIST_PANEL_INDEX],
            perc)

        mid_size = tot - tab_size
        self.setSizes([tab_size, mid_size])

    def __splitter_moved(self):
        sizes = self.sizes()
        self.__update_icons(sizes[0])

        playlist_panel_size = sizes[Splitter.PLAYLIST_PANEL_INDEX]
        if playlist_panel_size > 0:
            # In order to not save the size as increasingly smaller
            # as the user drags the splitter closed, use a timer
            # to delay the save.
            QtCore.QTimer.singleShot(100, \
                partial(self.__save_opened_panel_size, playlist_panel_size))

    def __save_opened_panel_size(self, size):
        """Remember this size if the size is still the same."""
        sizes = self.sizes()
        if len(sizes) < Splitter.PLAYLIST_PANEL_INDEX:
            return
        playlist_panel_size = sizes[Splitter.PLAYLIST_PANEL_INDEX]
        if playlist_panel_size != size:
            # Size has changed; don't save.
            return
        self.__opened_panel_size = playlist_panel_size
