import math
import bisect
import six
from PySide2 import QtCore, QtGui, QtWidgets


class TimelineSlider(QtWidgets.QWidget):
    """ The Timeline Widget is a rectangular area with ticks to represent units
        of time (in frames).You can display keys in the timeline, and select
        a sequence of frames. The range may be fractional, but the current time
        is always integral. This widget emits the following signals.
        * SIG_SLIDER_SCOPE_SELECTED - user selects either clip/sequence.
        * SIG_CURRENT_TIME_CHANGED - user clicks new time or program changes time
        * SIG_SELECTION_RANGE_CHANGED - user releases a drag that selects a frame range
        * SIG_KEY_SET_CHANGED - set of keyframe marks has changed
        * SIG_SELECTED_KEYS_CHANGED - set of selected keyframe markers changed
        * SIG_MOVED_KEYS - selected keys were moved an offset
    """
    SIG_SLIDER_SCOPE_SELECTED = QtCore.Signal()
    SIG_CURRENT_TIME_CHANGED = QtCore.Signal(int)  # time, final (unnecassary final)
    SIG_SELECTION_RANGE_CHANGED = QtCore.Signal()
    SIG_KEY_SET_CHANGED = QtCore.Signal()
    SIG_SELECTED_KEYS_CHANGED = QtCore.Signal()
    SIG_MOVED_KEYS = QtCore.Signal(list, int) # keys, offset
    SIG_SCRUBBING_STATE_CHANGED = QtCore.Signal(bool)

    # Enumeration of possible (non-atomic) GUI interactions
    __ACTION_NONE = 0
    __ACTION_SET_TIME = 1
    __ACTION_SELECT = 2
    __ACTION_ZOOM = 3
    __ACTION_PAN = 4
    __ACTION_KEY_SELECT = 5

    # # Enumeration of possible items to click on
    __HIT_NONE = 0
    __HIT_TIMELINE = 1

    __cache_pixmap_height = 3

    def __init__(self, parent, slider_scope):
        super().__init__(parent)
        self.__slider_scope = slider_scope

        # self.setAttribute(QtCore.Qt.WA_NativeWindow, True) # breaks core view
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, True)
        self.setMinimumWidth(100)
        self.__layout = QtWidgets.QHBoxLayout(self)
        self.__layout.addStretch(100)
        self.setLayout(self.__layout)
        self.setFixedHeight(32)

        self.__current_time = -1  # Track the current time

        # Minimum span for a range
        self.__min_range = 2
        # The range we are displaying
        self.__time_range = (0, self.__min_range)
        self.__time_range_final = True
        # Internal view of the time range, in floating point, for smooth pan/zoom
        self.__float_time_range = self.__time_range
        # The full (home, base, global) range, to which we reset
        self.__full_range = (0, self.__min_range)
        # The range selected, or None if nothing is selected.
        self.__selection_range = None

        # The transform animate keys we are displaying in the timeline.
        self.__transform_key_set = []

        # The annotations and CC frames
        self.__key_set = set()
        self.__annotation_ro_keys = set()
        self.__annotation_rw_keys = set()
        self.__cc_ro_keys = set()
        self.__cc_rw_keys = set()
        self.__transform_keys = set()

        # A subset of self.__key_set that contains selected keys.
        self.__selected_key_set = {}

        # The misc keys we're displaying in the timeline
        self.__misc_key_set = {}

        # If not None, a shift mouse-press was done in the timeline to
        # select a key, deselect a key or to move selected keys.
        self.__key_mouse_state = None

        # hoverTime is the time the mouse is hovering over.
        # floatHoverTime is an unrounded version.
        # This is different than current time!
        self.__hover_time = None
        self.__float_hover_time = None

        self.__is_scrubbing = False

        # Can the user select a sequence of frames on the timeline?
        self.__allow_selection = True

        # Allow keys to be selected.
        self.__allow_key_selection = False

        # Should the widget show time labels below the center of the
        # timeline?  The pointer will still have time labels appear on
        # mouseover but current time labels will not be present.
        self.__show_time_labels = True

        # Should the widget show misc keys on the timeline?
        self.__show_misc_keys = False

        # Request mouseover events from QT.
        self.setMouseTracking(True)

        # Get key events from Qt even without focus.
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # GUI interaction in progress
        self.__current_action = self.__ACTION_NONE

        # Don't erase the background for us; we redraw everything
        # with offscreen buffers.
        self.setAutoFillBackground(False)

        # Pick a font for the labels.
        # We don't use the application standard font, because we really need
        # a small font for this widget.
        self.__label_font = QtGui.QFont('Helvetica', 8)

        # Don't draw labels within this far of the edge.
        self.__edge_padding = 10

        # Proportions for vertical division of space
        # These are fractions of the way down from the top (QPainter uses (0,0) top-left)
        #   that each characteristic should occur.

        self.__tick_base = 0.45

        self.__tick_area_extent = None
        self.__update_tick_area_extent()

        # Colors which don't fall in the palette()
        # For drawing the current time indication
        self.__key_frame_color = QtGui.QColor(0, 128, 0)
        # Saved but not associated with a note.
        self.__ro_annotation_frame_color = QtGui.QColor(0xbb, 0x83, 0x2a)
        self.__rw_annotation_frame_color = QtGui.QColor(128, 128, 0)
        self.__cc_frame_color = QtGui.QColor(0, 128, 0)
        self.__selected_key_frame_color = QtGui.QColor(192, 0, 0)
        self.__current_time_color = QtGui.QColor(72, 240, 72)
        self.__current_time_past_full_color = QtGui.QColor(200, 100, 20)
        self.__key_number_bg_color = QtGui.QColor(34, 34, 34)
        self._misc_key_frame_color = QtGui.QColor(67, 103, 117)
        self.__transform_key_frames_color = QtGui.QColor(240, 0, 0)

        # Cache commonly used pens and brushes based on the above
        # colors.
        self.__current_time_pen = QtGui.QPen(self.__current_time_color)
        self.__current_time_past_full_pen = QtGui.QPen(self.__current_time_past_full_color)
        self.__key_number_bg_brush = QtGui.QBrush(self.__key_number_bg_color)

        # Brushes for painting keys.
        self.__dark_red_brush = QtGui.QBrush(QtGui.QColor(128, 0, 0))
        self.__dark_green_brush = QtGui.QBrush(QtGui.QColor(0, 128, 0))
        self.__background_brush = QtGui.QBrush(QtGui.QColor(75, 75, 75))

        self.__slider_scope_ag = action_group = QtWidgets.QActionGroup(self)
        self.__slider_scope_seq_action = QtWidgets.QAction("Sequence", action_group)
        self.__slider_scope_seq_action.setCheckable(True)
        self.__slider_scope_clip_action = QtWidgets.QAction("Clip", action_group)
        self.__slider_scope_clip_action.setCheckable(True)
        action_group.setExclusive(True)
        action_group.triggered.connect(self.__slider_scope_selected)
        self.__context_menu_actions = (self.__slider_scope_seq_action, self.__slider_scope_clip_action)

        self.set_allow_key_selection(True)

        self.__load_defaults()

    def get_key_set(self):
        return self.__key_set

    def get_selected_keys(self):
        return self.__selected_key_set.keys()

    def current_time(self):
        """
        Get current time displayed on the slider

        Returns:
            int representing current time
        """
        return self.__current_time

    def set_current_time(self, t):
        """
        Set the current time to slider and trigger update/render

        Args:
            t (int): current time
        """
        t = int(t)
        if self.__current_time == t:
            return
        self.__current_time = t
        self.update()

    def get_current_time(self):
        return self.__current_time

    def __emit_current_time_changed(self, time):
        time = int(time)
        self.set_current_time(time)
        self.SIG_CURRENT_TIME_CHANGED.emit(time)

    def __clean_range(self, range, intify=True):
        """
        Given a range, return a range with int only and acceptable max range

        Args:
            range (tuple): slider range
            intify (bool): make the new range int only

        Returns:
            tuple of new clean range
        """
        if intify:
            new_range = TimelineSlider.round_range(range)
        else:
            new_range = range
        new_max = max(max(new_range), new_range[0] + self.__min_range)
        return new_range[0], new_max

    def set_range(self, left_range, right_range):
        if self.__full_range[0] == left_range and self.__full_range[1] == right_range:
            return
        self.__full_range = (left_range, right_range)
        self.setEnabled(self.__full_range[0] != self.__full_range[1])
        new_time_range = self.__clean_range(self.__full_range)
        if new_time_range == self.__time_range:
            return
        self.__time_range = new_time_range
        self.__float_time_range = self.__time_range
        self.update()

    def __set_float_time_range(self, float_time_range, update=True, final=True):
        new_float_range = self.__clean_range(float_time_range, intify=False)
        if new_float_range == self.__float_time_range and final == self.__time_range_final:
            return
        self.__float_time_range = new_float_range
        new_time_range = self.__clean_range(float_time_range)
        if new_time_range != self.__time_range or final != self.__time_range_final:
            self.__time_range_final = final
            self.__time_range = new_time_range
        if update:
            self.update()

    def reset_time_range(self):
        self.set_range(self.__full_range)

    def fit_time_range_to_keys(self):
        if self.__key_set:
            key_list = sorted(self.__key_set)
            min_key = key_list[0]
            max_key = key_list[-1]
            delta = (max_key - min_key) * 0.1
            self.__set_float_time_range((min_key - delta, max_key + delta))

    def allow_selection(self):
        return self.__allow_selection

    def set_allow_selection(self, flag):
        self.__allow_selection = flag
        if not self.__allow_selection:
            self.set_selected_time_range(None)

    def allow_key_selection(self):
        return self.__allow_key_selection

    def set_allow_key_selection(self, flag):
        self.__allow_key_selection = flag

    def set_show_time_labels(self, flag):
        if self.__show_time_labels == flag:
            return
        self.__show_time_labels = flag
        self.repaint()

    def set_selected_time_range(self, time_range):
        """
        Set the selected time range by the user

        Args:
            time_range (tuple): time range
        """
        if time_range == self.__selection_range:
            return
        self.__selection_range = time_range
        self.SIG_SELECTION_RANGE_CHANGED.emit()

    def set_show_misc_keys(self, flag):
        """
        Set if to show misc keys and update the slider

        Args:
            flag (bool): flag to on or off
        """
        if self.__show_misc_keys == flag:
            return
        self.__show_misc_keys = flag
        self.update()

    def set_annotation_ro_keys(self, frames):
        self.__annotation_ro_keys = frames
        self.update()

    def set_annotation_rw_keys(self, frames):
        self.__annotation_rw_keys = frames
        self.update()

    def set_cc_ro_keys(self, frames):
        self.__cc_ro_keys = frames
        self.update()

    def set_cc_rw_keys(self, frames):
        self.__cc_rw_keys = frames
        self.update()

    def clear_selected_keys(self):
        """
        Clear all keys and update the slider
        """
        self.__selected_key_set.clear()
        self.SIG_SELECTED_KEYS_CHANGED.emit()
        self.update()

    def add_misc_key(self, key, value):
        """
        Add new misc key and update the slider

        Args:
            key (int): key i.e. frame
            value (int): what it represents
        """
        self.__misc_key_set[key] = value
        self.update()

    def remove_misc_key(self, time):
        """
        Remove the misc key at the given time and update the slider
        :param time: time pos on slider
        :type time: int
        """
        if self.__misc_key_set.pop(time, None) is None:
            return
        self.update()

    def clear_misc_keys(self):
        """
        Clear the misc keys and update the slider
        """
        self.__misc_key_set.clear()
        self.update()

    def set_misc_keys(self, key_set):
        self.__misc_key_set.clear()
        for key, value in key_set.items():
            self.__misc_key_set[key] = value
        self.SIG_KEY_SET_CHANGED.emit()
        self.update()

    def set_transform_keys(self, key_set):
        """
        Given a  key set, set the transform keys and update the slider

        Args:
            key_set (list): list of keys/frames

        Returns:

        """
        if self.__transform_key_set == key_set:
            return
        del self.__transform_key_set[:]
        self.__transform_key_set = key_set
        self.update()

    def __find_closest_key(self, hit_time):
        """
        Given a time on the timeline find the closest key.

        Args:
            hit_time (int): time/frame on timeline

        Returns:
            closest key to the provided time
        """

        key_list = sorted(self.__key_set)
        if not key_list:
            return None
        index = bisect.bisect_left(key_list, hit_time)
        if index == 0:
            return key_list[0]
        elif index == len(key_list):
            return key_list[-1]
        else:
            candidate_1 = key_list[index - 1]
            candidate_2 = key_list[index]
            if (hit_time - candidate_1) > (candidate_2 - hit_time):
                return candidate_2
            else:
                return candidate_1

    def event(self, event):
        if event.type() != QtCore.QEvent.ToolTip:
            return super(TimelineSlider, self).event(event)

        hit = self.__hit_test_local_point(event.pos())
        if hit != self.__HIT_TIMELINE:
            return super(TimelineSlider, self).event(event)

        hit_time = self.get_time_from_local_x(event.x(), floor=True)
        if hit_time not in self.__key_set:
            return super(TimelineSlider, self).event(event)
        # Removed edbot usages here
        event.accept()
        return True

    def mousePressEvent(self, mouse_event):
        mouse_event.ignore()
        self.__current_action = self.__ACTION_NONE
        hit = self.__hit_test_local_point(mouse_event.pos())
        buttons = mouse_event.buttons()

        if hit == self.__HIT_NONE and not buttons & QtCore.Qt.MiddleButton:
            # mid-button over nothing
            return

        elif hit == self.__HIT_TIMELINE:
            hit_time = self.get_time_from_local_x(mouse_event.x())
            hit_time_floor = self.get_time_from_local_x(mouse_event.x(), floor=True)
            modifiers = mouse_event.modifiers()
            self.__prev_mouse_pos = mouse_event.pos()
            self.__mouse_press_time = self.__hover_time
            self.__float_mouse_press_time = self.__float_hover_time

            if buttons & QtCore.Qt.MiddleButton:
                # middle-mouse drag (any modifiers): pan
                self.__current_action = self.__ACTION_PAN
            elif self.allow_selection() and modifiers & QtCore.Qt.ControlModifier:
                # Update the selection range without signals.
                self.__selection_range = (hit_time_floor, hit_time_floor)
                self.__current_action = self.__ACTION_SELECT
                mouse_event.accept()  # Only prevent others from getting this event if it starts a selection.
            elif modifiers & QtCore.Qt.AltModifier:
                # alt-drag (any button but mid): zoom
                self.__current_action = self.__ACTION_ZOOM
            elif modifiers == QtCore.Qt.NoModifier and buttons & QtCore.Qt.LeftButton:
                self.set_selected_time_range(None)
                self.__emit_current_time_changed(hit_time)
                self.__current_action = self.__ACTION_SET_TIME
            elif self.__allow_key_selection and modifiers & QtCore.Qt.ShiftModifier and self.__key_set:
                self.__key_mouse_state = {'mouse-moved': False,
                                          'start': hit_time_floor,
                                          'end': hit_time_floor}
                self.set_selected_time_range(None)
                self.__current_action = self.__ACTION_KEY_SELECT

            # Any click in the timeline that isn't selecting, selecting a key,
            # deselecting a key or moving selected keys deselects all keys.
            if self.__current_action not in (self.__ACTION_SELECT, self.__ACTION_KEY_SELECT):
                self.__selected_key_set.clear()
                self.SIG_SELECTED_KEYS_CHANGED.emit()
        else:
            self.update()

    def mouseMoveEvent(self, mouse_event):
        mouse_event.ignore()
        self.__hover_time = None
        self.__float_hover_time = self.get_time_from_local_x(mouse_event.x(), floatValue=True)
        hit = self.__hit_test_local_point(mouse_event.pos())
        if hit == self.__HIT_TIMELINE or self.__current_action is not self.__ACTION_NONE:
            self.__hover_time = self.get_time_from_local_x(mouse_event.x())

        hover_time_floor = self.get_time_from_local_x(mouse_event.x(), floor=True)
        if self.__current_action == self.__ACTION_PAN:
            pan_amt = self.__float_mouse_press_time - self.__float_hover_time
            panned_range = tuple([v + pan_amt for v in self.__float_time_range])
            self.__set_float_time_range(panned_range, final=False)
            mouse_event.accept()
        elif self.__current_action == self.__ACTION_SELECT:
            # Update the selection range, but don't send signals.
            if self.__selection_range:
                self.__selection_range = (self.__selection_range[0], hover_time_floor)
            else:
                self.__selection_range = (hover_time_floor, hover_time_floor)
            mouse_event.accept()
        elif self.__current_action == self.__ACTION_ZOOM:
            dx = mouse_event.pos().x() - self.__prev_mouse_pos.x()
            zoom_factor = 1.05 if dx < 0 else 0.95
            center = self.__mouse_press_time
            self.__zoom_time_range(zoom_factor, center, final=False)
            self.__prev_mouse_pos = QtCore.QPoint(mouse_event.pos())
            mouse_event.accept()
        elif self.__current_action == self.__ACTION_SET_TIME:
            self.__emit_current_time_changed(self.__hover_time)
            if not self.__is_scrubbing:
                self.__is_scrubbing = True
                self.SIG_SCRUBBING_STATE_CHANGED.emit(self.__is_scrubbing)
        elif self.__current_action == self.__ACTION_KEY_SELECT:
            # Record that a mouse move occurred so a key is never
            # selected or deselected, even if the user moves the mouse
            # back to the position where the the original mouse press
            # occurred.
            end = hover_time_floor
            offset = end - self.__key_mouse_state['start']
            if offset != 0:
                self.__key_mouse_state['mouse-moved'] = True
                if self.__selected_key_set:
                    selected_keys_list = list(six.iterkeys(self.__selected_key_set))
                    min_key = min(selected_keys_list) + offset
                    max_key = max(selected_keys_list) + offset
                    if (min_key >= self.__time_range[0] and
                            max_key <= self.__time_range[1]):
                        self.__key_mouse_state['end'] = end
                        self.__emit_current_time_changed(min_key)
        self.update()

    def wheelEvent(self, wheel_event):
        wheel_event.ignore()
        center = self.__float_hover_time
        if wheel_event.modifiers() == QtCore.Qt.NoModifier and not (center is None):
            zoom_factor = 1.1 if wheel_event.angleDelta().y() < 0 else 0.9
            self.__zoom_time_range(zoom_factor, center)
            wheel_event.accept()

    def keyPressEvent(self, key_event):
        k = key_event.key()
        center = self.__float_hover_time
        if center is not None:
            if k == QtCore.Qt.Key_Plus or k == QtCore.Qt.Key_Equal:
                self.__zoom_time_range(0.9, center)
                key_event.accept()
            elif k == QtCore.Qt.Key_Minus:
                self.__zoom_time_range(1.1, center)
                key_event.accept()
        if k == QtCore.Qt.Key_Home:
            self.reset_time_range()
            key_event.accept()
        elif k == QtCore.Qt.Key_F:
            self.fit_time_range_to_keys()
            key_event.accept()

    def __zoom_time_range(self, factor, center, final=True):
        new_range = tuple(center + factor * (v - center) for v in self.__float_time_range)
        if new_range[1] - new_range[0] >= self.__min_range:
            self.__set_float_time_range(new_range, final=final)

    def mouseReleaseEvent(self, mouse_event):
        hit_time = self.get_time_from_local_x(mouse_event.x())
        if self.__current_action == self.__ACTION_SELECT:
            if self.__selection_range:
                self.__selection_range = (min(self.__selection_range[0], self.__selection_range[1]),
                                          max(self.__selection_range[0], self.__selection_range[1]))
                # Select all keys in selection range and reset selection range
                for key in self.__key_set:
                    if self.__selection_range[0] <= key <= self.__selection_range[1]:
                        self.__selected_key_set[key] = 0
                self.SIG_SELECTED_KEYS_CHANGED.emit()
                self.__selection_range = None
                # Calling setSelectedTimeRange signals only on change;
                # release may not be a change so signal explicitly here
                self.SIG_SELECTION_RANGE_CHANGED.emit()
            else:
                self.set_selected_time_range(None)
                self.__hover_time = hit_time
        elif self.__current_action in (self.__ACTION_ZOOM, self.__ACTION_PAN):
            self.__set_float_time_range(self.__float_time_range, final=True)
        elif self.__current_action == self.__ACTION_KEY_SELECT:
            # If the keys were moved then move them, assuming there
            # are any selected keys, otherwise select or deselect a
            # key.
            if self.__key_mouse_state['mouse-moved']:
                if self.__selected_key_set:
                    offset = self.__key_mouse_state['end'] - self.__key_mouse_state['start']
                    if offset != 0:
                        self.SIG_MOVED_KEYS.emit(
                            list(six.iterkeys(self.__selected_key_set)), offset
                        )
            else:
                # Find the closest key since it is hard to click on
                # keys sometimes.
                hit_time = self.__find_closest_key(self.__key_mouse_state['start'])
                if self.__selected_key_set.pop(hit_time, None) is None:
                    self.__selected_key_set[hit_time] = 0
                self.SIG_SELECTED_KEYS_CHANGED.emit()
            self.__key_mouse_state = None
        if self.__is_scrubbing:
            self.__is_scrubbing = False
            self.SIG_SCRUBBING_STATE_CHANGED.emit(self.__is_scrubbing)
        self.update()

        self.__current_action = self.__ACTION_NONE

    def resizeEvent(self, event):
        r = super(TimelineSlider, self).resizeEvent(event)
        self.__update_tick_area_extent()
        return r

    def leaveEvent(self, event):
        self.__hover_time = None
        self.__float_hover_time = None
        self.update()

    def paintEvent(self, paint_event):
        # Use repr() to generate a cache key because it is recursive
        # and should be fast, faster than pprint because repr() is in
        # C while pprint is in Python.  The only issue with repr() is
        # that it may not generate the same representation for
        # dictionaries if key/value pairs are added and removed, so
        # there may be cache misses that would otherwise be cache hits
        # if the string representation were consistent.  Hopefully,
        # this should happen infrequently in practice.
        self.__key_set = set(self.__annotation_ro_keys + self.__cc_ro_keys + self.__cc_rw_keys + self.__annotation_rw_keys)
        size = self.size()
        key = repr((size,
                    self.__full_range,
                    self.__float_time_range,
                    self.__current_action,
                    self.__selection_range,
                    self.__time_range,
                    self.__show_time_labels,
                    self.__key_mouse_state,
                    self.__annotation_rw_keys,
                    self.__annotation_ro_keys,
                    self.__cc_ro_keys,
                    self.__cc_rw_keys,
                    self.__selected_key_set,
                    self.__misc_key_set,
                    self.__transform_key_set,
                    self.__show_misc_keys))
        pixmap = QtGui.QPixmap(size)
        if not QtGui.QPixmapCache.find(key, pixmap):
            painter = QtGui.QPainter()
            painter.begin(pixmap)

            painter.setFont(self.__label_font)

            # Uses self.__fullRange
            self.__paint_background(painter)

            # Uses self.__selectionRange
            self.__paint_selection(painter)

            # Uses self.__timeRange and self.__show_time_labels.
            self.__paint_ticks_and_labels(painter)

            # Uses self.__timeRange, self.__fullRange,
            # self.__selectionRange and self.__floatTimeRange.
            self.__paint_arrows(painter)

            # Uses self.__timeRange, self.__key_mouse_state,
            # and self.__selected_key_set.
            self.__paint_keys(painter, self.__annotation_ro_keys, self.__ro_annotation_frame_color)
            self.__paint_keys(painter, self.__cc_ro_keys, self.__ro_annotation_frame_color)
            self.__paint_keys(painter, self.__cc_rw_keys, self.__rw_annotation_frame_color)
            self.__paint_keys(painter, self.__annotation_rw_keys, self.__rw_annotation_frame_color)
            self.__paint_transform_keys(painter)

            # Uses self.__timeRange, self.__misc_key_set,
            # and self.__show_time_labels.
            self.__paint_misc_keys(painter)

            painter.end()
            QtGui.QPixmapCache.insert(key, pixmap)

        painter = QtGui.QPainter(self)
        painter.setFont(self.__label_font)
        painter.drawPixmap(0, 0, pixmap)

        # # Uses self.__hover_time and self.__selectionRange.
        self.__paint_hover_time(painter)

        # # Uses self.__currentTime, self.__show_time_labels and self.__key_set
        self.__paint_current_time(painter)

    def __get_timeline_extent(self):
        """
        Get the area in which the main timeline will be drawn

        Returns:
            QtCore.QRect object
        """
        return QtCore.QRect(0, 0, self.width(), self.height())

    def __update_tick_area_extent(self):
        """
        The area, within the timeline extent, in which the tick marks and keyframes will be drawn
        """
        self.__tick_area_extent = QtCore.QRect(0, 0, self.width(), self.height() * self.__tick_base)

    def __get_tick_area(self, time):
        """
        Returns the area in which a tickmark of keyframe for the given time should be drawn

        Args:
            time (int): time/frame on timeline

        Returns:
            QtCore.QRectF object
        """
        available_width = float(self.__tick_area_extent.width() - 2 * self.__edge_padding)
        span = self.__float_time_range[1] - self.__float_time_range[0]
        tick_spacing = available_width / span
        frac = float(time - self.__float_time_range[0]) / span
        tick_left = self.__tick_area_extent.left() + self.__edge_padding + frac * available_width
        return QtCore.QRectF(tick_left, 0,
                             tick_spacing, self.__tick_area_extent.height() - 2)

    def __hit_test_local_point(self, point):
        """
        Check if the point is within the slider

        Args:
            point (tuple): point on slider

        Returns:
            0 or 1 representing if timeline was hit
        """
        if self.__get_timeline_extent().contains(point):
            return self.__HIT_TIMELINE
        else:
            return self.__HIT_NONE

    def get_time_from_local_x(self, x, floatValue=False, floor=False):
        """
        Get the time on slider based on the x pos
        Args:
            x (int): position on slider
            floatValue (bool): is float value?
            floor (bool): floor the return value?

        Returns:
            int time on slider
        """
        available_width = float(self.__tick_area_extent.width() - 2 * self.__edge_padding)
        span = self.__float_time_range[1] - self.__float_time_range[0]
        tick_spacing = available_width / span
        delta_x = x - (self.__tick_area_extent.left() + self.__edge_padding)
        float_time = delta_x / tick_spacing + self.__float_time_range[0]
        if floor:
            float_time = math.floor(float_time)
        if floatValue:
            return float_time
        else:
            if float_time >= 0:
                hit_time = int(float_time + 0.5)
            else:
                hit_time = int(float_time - 0.5)
            hit_time = int(max(self.__time_range[0], min(hit_time, self.__time_range[1])))
            return hit_time

    def __paint_background(self, painter):
        """
        Paint the timeline background, i.e. the dark rectangle

        Args:
            painter (QtGui.QPainter): QT painter
        """
        timeline_rect = self.__get_timeline_extent()
        offset = self.__tick_area_extent.height()

        bg_brush = self.palette().window()
        painter.fillRect(timeline_rect, bg_brush)

        left_end = max(self.__get_tick_area(self.__full_range[0]).left(), timeline_rect.left())
        right_end = min(self.__get_tick_area(self.__full_range[1] + 1).left(),
                        timeline_rect.right()) + 1
        key_number_rect = QtCore.QRect(left_end, timeline_rect.top() + offset, right_end - left_end,
                                       timeline_rect.height() - offset)

        painter.fillRect(key_number_rect, self.__key_number_bg_brush)

    def __paint_arrows(self, painter):
        # Only show arrows if the working range is outside of the full range.
        if not (self.__time_range[0] > self.__full_range[1] or self.__time_range[1] < self.__full_range[0]):
            return

        # Don't show arrows during selection, unless the selection is outside the working range.
        if self.__selection_range is not None:
            for sel_end in self.__selection_range:
                if sel_end > self.__float_time_range[0] and sel_end < self.__float_time_range[1]:
                    return

        timeline_rect = self.__get_timeline_extent()
        timeline_rect_top = timeline_rect.top()
        timeline_rect_height = timeline_rect.height()
        timeline_rect_left = timeline_rect.left()
        timeline_rect_right = timeline_rect.right()

        offset = self.__tick_area_extent.height()
        key_number_rect = QtCore.QRect(timeline_rect_left,
                                       timeline_rect_top + offset,
                                       timeline_rect.width(),
                                       timeline_rect_height - offset)

        palette = self.palette()
        painter.setPen(QtGui.QPen(palette.color(QtGui.QPalette.Shadow)))
        fill_brush = QtGui.QBrush(palette.color(QtGui.QPalette.Light))
        bg_brush = palette.window()
        top = timeline_rect_top + offset + 3
        bot = timeline_rect.bottom() - 3
        mid = (top + bot)/2
        ht = bot-top
        rect_width = 3*ht

        if self.__full_range[1] <= self.__time_range[0]:
            painter.fillRect(timeline_rect_left + 1,
                             timeline_rect_top + offset,
                             rect_width,
                             timeline_rect_height - offset,
                             bg_brush)
            painter.setBrush( fill_brush )
            painter.drawPolygon(
                QtCore.QPointF(timeline_rect_left + 2*ht, top),
                QtCore.QPointF(timeline_rect_left + 2*ht, bot),
                QtCore.QPointF(timeline_rect_left + ht, mid)
            )
        else:
            painter.fillRect(timeline_rect_right - rect_width,
                             timeline_rect_top + offset,
                             rect_width,
                             timeline_rect_height - offset,
                             bg_brush)
            painter.setBrush(fill_brush)
            painter.drawPolygon(
                QtCore.QPointF(timeline_rect_right - 2*ht, top),
                QtCore.QPointF(timeline_rect_right - 2*ht, bot),
                QtCore.QPointF(timeline_rect_right - ht, mid)
            )

    def __paint_ticks_and_labels(self, painter):
        """
        Draw tick marks and associated labels. This includes
        integer tick marks (unless they would be too crowded),
        and major tick marks (picked by some heuristic)

        Args:
            painter (QtGui.QPainter): QT painter
        """
        timeline_extent = self.__get_timeline_extent()
        tick_height = self.__tick_area_extent.height() / 4

        label_height = self.__tick_area_extent.height() * 0.6

        palette = self.palette()
        tick_pen = QtGui.QPen(palette.color(QtGui.QPalette.Shadow))
        label_pen = QtGui.QPen(palette.color(QtGui.QPalette.Light))

        tick_base = self.__tick_area_extent.bottom()

        # Draw the baseline (all the way to the edge)
        timeline_extent_left = timeline_extent.left()
        timeline_extent_right = timeline_extent.right()
        timeline_extent_bottom = timeline_extent.bottom()

        painter.setPen(tick_pen)
        painter.drawLine(timeline_extent_left, tick_base,
                         timeline_extent_right, tick_base)

        painter.setPen(QtGui.QPen(palette.color(QtGui.QPalette.Dark)))
        painter.drawLine(timeline_extent_left, tick_base,
                         timeline_extent_left, timeline_extent_bottom)
        painter.drawLine(timeline_extent_right, tick_base,
                         timeline_extent_right, timeline_extent_bottom)

        metric = QtGui.QFontMetrics(painter.font())
        y_pos = tick_base + metric.ascent() + 2

        def pos_fn(t):
            return self.__get_tick_area(t).left()

        def inv_pos_fn(screen_x):
            return self.get_time_from_local_x(screen_x, floatValue=True)

        def width_fn(t):
            return metric.horizontalAdvance(str(t))

        for t, is_major, draw_label in TimelineSlider.calculate_ticks(
                self.__time_range[0], self.__time_range[1],
                pos_fn, inv_pos_fn, width_fn, force_bound_labels=True
        ):
            x_pos = self.__get_tick_area(t).left()
            if is_major:
                painter.setPen(label_pen)
                painter.drawLine(x_pos, tick_base - 1, x_pos, tick_base - label_height)
                if draw_label and self.__show_time_labels:
                    frame_string = str(t)
                    width = metric.horizontalAdvance(frame_string)
                    x_pos -= width / 2
                    painter.drawText(x_pos, y_pos, frame_string)
            else:
                painter.setPen(tick_pen)
                painter.drawLine(x_pos, tick_base, x_pos, tick_base - tick_height)

    def __paint_transform_keys(self, painter):
        """
        Paints tranform keys

        Args:
            painter (QtGui.QPainter): QT painter
        """
        time_range = range(self.__time_range[0] - 1, self.__time_range[1] + 1)
        key_set = [k for k in self.__transform_key_set if k in time_range]
        if not key_set:
            return
        painter.setPen(self.__transform_key_frames_color)
        for key in sorted(key_set):
            tick_area = self.__get_tick_area(key)
            tick_area_left = tick_area.left()
            painter.drawLine(tick_area_left, 0,
                             tick_area_left, self.height() - 5)

    def __paint_keys(self, painter, key_set, color):
        """
        Paints given key set with a given color

        Args:
            painter (QtGui.QPainter): QT painter
            key_set (set): list of keys/frames to be drawn
            color (QtGui.QColor): color to use
        """
        time_range = range(self.__time_range[0] - 1, self.__time_range[1] + 1)
        key_set = list(filter(lambda frame: frame in time_range, key_set))
        if not key_set:
            return
        if self.__key_mouse_state:
            offset = self.__key_mouse_state['end'] - self.__key_mouse_state['start']
        else:
            offset = 0
        painter.setPen(self.palette().color(QtGui.QPalette.Window))
        # Paint the keys from left to right so that the left-most edge
        # of a key always matches where the current time would be
        # drawn if the current time equals the key's frame number.
        # This is to support two successive frames having keys, one
        # key selected and the other not so they have different
        # colors, and ensuring that the left edge of the higher
        # numbered frame's key matches where the current time would be
        # drawn.
        #
        # Additionally, draw selected keys after unselected keys so
        # that during a move selected keys are not painted over by
        # unselected keys from higher numbered frames.
        max_key_plus_one = max(key_set) + 1
        def key_sort_index(t):
            return t + max_key_plus_one if t in self.__selected_key_set else t

        for frame in sorted(key_set, key=key_sort_index):
            # a single frame might have multiple keys. we will render only the
            # first one in queue (the most recently added)
            if frame in self.__selected_key_set:
                color = self.__selected_key_frame_color
                tick_area = self.__get_tick_area(frame + offset)
            else:
                tick_area = self.__get_tick_area(frame)

            # NOTE: in itview 4, keys were drawn using rec frame, which started from 0
            # visually, we never show that, so in itview 5, the default start is 1
            # In order to make sure keys are drawn correctly, we do subtraction here, but
            # ideally, larger change should be done to all methods so it includes that change

            # It appears that QPainter#fillRect() will draw the left
            # edge of the rectangle one pixel to the right of
            # int(QRect#left()) if the input QRect's left() has a
            # non-zero floating point component.  This results in the
            # left edge of the key rectangle one pixel to the right of
            # the current time, which is drawn with
            # QPainter#drawLine().  Work around this by forcing the
            # left edge to an integer value so they exactly match.
            tick_area.setLeft(int(tick_area.left()))

            # Draw with a subtle radial gradient.  All the badges do
            # it. Why can't the keys?
            grad = QtGui.QRadialGradient()
            grad.setCenter(QtCore.QPointF(tick_area.topLeft()))
            grad.setFocalPoint(QtCore.QPointF(tick_area.topLeft()))
            grad.setRadius(max(tick_area.height(), tick_area.width()))
            grad.setColorAt(0, color.lighter(115))
            grad.setColorAt(1, color.darker(115))
            key_brush = QtGui.QBrush(grad)

            # Old-style (flat) drawing
            # key_brush = QtGui.QBrush(self.__key_frame_color)

            painter.fillRect(tick_area, key_brush)

    def __paint_misc_keys(self, painter):
        """
        Function that paints any misc keys set in the timeline
        Currently, we are painting the timewarped frames as misc keys

        Args:
            painter (QtGui.QPainter): QT painter
        """
        if not self.__show_misc_keys:
            return

        time_range = range(self.__time_range[0] - 1, self.__time_range[1] + 1)
        misc_key_set = dict(
            [(k, v) for k, v in six.iteritems(self.__misc_key_set) if k in time_range]
        )
        if not misc_key_set:
            return

        tick_height = self.__tick_area_extent.height()

        painter.setPen(self.palette().color(QtGui.QPalette.Window))
        max_key_plus_one = max(misc_key_set) + 1

        def key_sort_index(t):
            return t[0] + max_key_plus_one if t[0] in self.__selected_key_set else t[0]

        for key_time, _ in sorted(six.iteritems(misc_key_set), key=key_sort_index):
            tick_area = self.__get_tick_area(key_time)
            tick_area.setHeight(tick_height)
            color = self._misc_key_frame_color

            tick_area.setLeft(int(tick_area.left()))

            grad = QtGui.QRadialGradient()
            grad.setCenter(QtCore.QPointF(tick_area.topLeft()))
            grad.setFocalPoint(QtCore.QPointF(tick_area.topLeft()))
            grad.setRadius(max(tick_area.height(), tick_area.width()))
            grad.setColorAt(0, color.lighter(115))
            grad.setColorAt(1, color.darker(115))
            key_brush = QtGui.QBrush(grad)

            painter.fillRect(tick_area, key_brush)

    def __paint_current_time(self, painter):
        """
        Paint green tick that indicates current time

        Args:
            painter (QtGui.QPainter): QT painter
        """
        current_time = self.current_time()
        time_extent = self.__get_tick_area(current_time)
        time_extent_left = time_extent.left()

        full_width = self.width() - self.__edge_padding * 2
        full_left = self.__edge_padding
        if time_extent_left >= full_left and time_extent_left <= full_left + full_width:
            pen = self.__current_time_pen
        else:
            pen = self.__current_time_past_full_pen
        old_pen = painter.pen()
        painter.setPen(pen)
        if self.__show_time_labels:
            painter.drawLine(time_extent_left, 0,
                             time_extent_left, time_extent.height() + 5)
            metric = QtGui.QFontMetrics(painter.font())
            if current_time in self.__key_set:
                if type(current_time) is str:
                    current_time = int(current_time)
                frame_string = '[%s]' % str(current_time)
            else:
                frame_string = str(current_time)
            x_pos = time_extent_left - metric.horizontalAdvance(frame_string) / 2
            y_pos = self.__tick_area_extent.bottom() + metric.ascent() + 2
            painter.drawText(x_pos, y_pos, frame_string)
        else:
            painter.drawLine(time_extent_left, 0,
                             time_extent_left, self.height())
        painter.setPen(old_pen)

    def __paint_hover_time(self, painter):
        """
        Paints a tick that appears on pointer hover

        Args:
            painter (QtGui.QPainter): QT painter
        """
        if self.__hover_time is None:
            return
        time_extent = self.__get_tick_area(self.__hover_time)
        time_extent_left = time_extent.left()
        old_pen = painter.pen()
        palette = self.palette()
        painter.setPen(palette.color(QtGui.QPalette.Light))
        painter.drawLine(time_extent_left, time_extent.bottom(),
                         time_extent_left, self.__get_timeline_extent().bottom())

        if self.__selection_range:
            painter.setPen(palette.color(QtGui.QPalette.HighlightedText))
        else:
            painter.setPen(palette.color(QtGui.QPalette.Light))
        metric = QtGui.QFontMetrics(painter.font())
        frame_string = str(
            self.__hover_time
        )
        x_pos = time_extent_left - metric.horizontalAdvance(frame_string) / 2
        y_pos = metric.ascent()  # spaced down from the top of the timeline
        painter.drawText(x_pos, y_pos, frame_string)
        painter.setPen(old_pen)

    def __paint_selection(self, painter):
        """
        Paint the selection area (e.g. Ctrl + Drag)
        :param painter: QT painter
        :type painter: QtGui.QPainter
        """
        if self.__selection_range is None:
            return
        selection = (min(self.__selection_range[0], self.__selection_range[1]),
                     max(self.__selection_range[0], self.__selection_range[1]))

        left_extent = self.__get_tick_area(selection[0])
        right_extent = self.__get_tick_area(selection[1])
        selection_rect = self.__get_timeline_extent()
        selection_extent = QtCore.QRect(left_extent.left(), selection_rect.top(),
                                        right_extent.right() - left_extent.left(),
                                        selection_rect.height())
        painter.fillRect(selection_extent, QtGui.QBrush(self.palette().color(QtGui.QPalette.Light)))

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        for action in self.__context_menu_actions:
            menu.addAction(action)
        menu.popup(event.globalPos())

    def __slider_scope_selected(self, action):
        if (self.__slider_scope.is_sequence_scope() and action is self.__slider_scope_seq_action) or \
                (self.__slider_scope.is_clip_scope() and action is self.__slider_scope_clip_action):
            return

        if action is self.__slider_scope_seq_action:
            self.__slider_scope.set_sequence_scope()
        if action is self.__slider_scope_clip_action:
            self.__slider_scope.set_clip_scope()

        self.set_show_time_labels(self.__slider_scope.is_clip_scope())
        self.SIG_SLIDER_SCOPE_SELECTED.emit()

    def __load_defaults(self):
        if self.__slider_scope.is_sequence_scope():
            self.__slider_scope_seq_action.setChecked(True)
            self.__slider_scope_selected(self.__slider_scope_seq_action)
            self.set_show_time_labels(False)
        else:
            self.__slider_scope_clip_action.setChecked(True)
            self.__slider_scope_selected(self.__slider_scope_clip_action)
            self.set_show_time_labels(True)

    @staticmethod
    def round_range(range):
        """
        Round the range. Return default 1, 1 range if provided range is None

        Args:
            range (tuple): range

        Returns:
            range_min, range_max (int,int)
        """
        if range is None:
            return 1, 1
        r_min = int(range[0]) if range[0] else 1
        r_max = int(range[1]) if range[1] else 1
        if range[0] > 0 and range[0] != r_min:
            r_min += 1
        if range[1] < 0 and range[1] != r_max:
            r_max -= 1
        return r_min, r_max

    @staticmethod
    def calculate_ticks(range_min, range_max, pos_fn, inv_pos_fn, width_fn,
                        margin=4, force_bound_labels=False):
        """
        Calculate where to draw tick marks and their labels for a timeline.

        Args:
            range_min (): min range
            range_max (): max range
            pos_fn (): position at which to center a label string
            inv_pos_fn (): time
            width_fn (): width of rendered string
            margin (): margin to allow between labels
            force_bound_labels (): always show the labels for the range min/max

        Returns:
            Given a (time) range, yield a list of (t, isMajor, drawLabel) values:
                t: the time value to draw for
                isMajor: typically longer/brighter
                drawLabel: draw the time as text
        """
        range_min_int = int(math.ceil(range_min))
        range_max_int = int(math.floor(range_max))

        if range_min_int > range_max_int:
            yield ((range_min + range_max) / 2.0, True, True)
            return

        # Calculate the label period.
        delta = range_max - range_min
        if delta < 10:
            label_period = 1
        elif delta < 20:
            label_period = 2
        else:
            if delta < 10000:
                base = 5
                offset = 2
            else:
                base = 10
                offset = 1
            scale = math.ceil(math.log(delta) / math.log(base))
            label_period = base ** max(1, scale - offset)
            label_period = int(label_period)

        if force_bound_labels:
            first_frame, last_frame = range_min_int, range_max_int
        else:
            left_bound = pos_fn(range_min)
            left_bound += width_fn(range_min_int) / 2 + margin / 2
            first_frame = int(math.ceil(inv_pos_fn(left_bound)))

            right_bound = pos_fn(range_max)
            right_bound -= width_fn(range_max_int) / 2 + margin / 2
            last_frame = int(math.floor(inv_pos_fn(right_bound)))

            # When zoomed way in, the frames may not have room to draw,
            #   and may get pushed crossed.
            if first_frame >= last_frame:
                first_frame, last_frame = range_min_int, range_max_int

        # The first major label is the on-period value
        #   next greater than the first label.
        first_major = first_frame + label_period - 1
        first_major = first_major - (first_major % label_period)

        # all the potentially-labeled frames
        major_frames = list(range(first_major, last_frame + 1, label_period))
        if major_frames[0] != first_frame:
            major_frames.insert(0, first_frame)
        if major_frames[-1] != last_frame:
            major_frames.append(last_frame)

        if (pos_fn(range_min_int + 1) - pos_fn(range_min_int)) >= 5 \
                and label_period > 1:
            # show unit frames
            all_frames = list(range(major_frames[0], major_frames[-1] + 1))
        else:
            all_frames = major_frames

        i = 0
        n_major = len(major_frames)
        left_edge = pos_fn(first_frame)  # will get set from first frame, anyway
        right_edge = pos_fn(last_frame) - width_fn(last_frame) / 2 - margin
        for frame in all_frames:
            if i < n_major and frame == major_frames[i]:
                i += 1
                pos = pos_fn(frame)
                width = width_fn(frame)
                pos -= width / 2
                if frame in (first_frame, last_frame) or \
                        (pos > left_edge and pos + width < right_edge):
                    left_edge = pos + width + margin
                    yield frame, True, True
                else:
                    yield frame, True, False
            else:
                yield frame, False, False
