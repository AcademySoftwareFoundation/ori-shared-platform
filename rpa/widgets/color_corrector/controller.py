"""
Controller for Color Corrector
"""
import numpy as np
from PySide2 import QtCore, QtWidgets

from rpa.session_state.utils import screen_to_itview
from rpa.session_state.color_corrections import ColorTimer, Grade

from rpa.widgets.color_corrector.view.view import View
from rpa.widgets.color_corrector.view.slider_attrs import build_slider_attrs
from rpa.widgets.color_corrector import constants as C


class ControllerSignals(QtCore.QObject):
    SIG_CLOSE = QtCore.Signal()

class Controller(QtCore.QObject):
    def __init__(self, rpa, main_window):
        super().__init__()
        self.__rpa = rpa
        self.__main_window = main_window

        # API
        self.__cc_api = rpa.color_api
        self.__timeline_api = rpa.timeline_api
        self.__session_api = rpa.session_api
        self.__annotation_api = rpa.annotation_api
        self.__viewport_api = rpa.viewport_api

        attrs = build_slider_attrs()
        self.__view = View(attrs, self.__main_window)
        self.__clipboard_cc = None
        self.__points = []
        self.__transient_points = []

        # Connect all signals
        self.signals = ControllerSignals()
        self.SIG_CLOSE = self.signals.SIG_CLOSE
        self.__view.SIG_CLOSE.connect(self.SIG_CLOSE)

        self.__connect_footer_signals()
        self.__connect_signals(self.tab_widget.clip_tab)

        self.tab_widget.SIG_APPEND_TAB.connect(self.__append_tab)
        self.tab_widget.SIG_REORDER_TABS.connect(self.__reorder_tabs)
        self.tab_widget.SIG_TAB_CLOSED.connect(self.__tab_closed)
        self.tab_widget.SIG_TAB_RENAMED.connect(self.__tab_renamed)

        self.__cc_api.SIG_CCS_MODIFIED.connect(self.__ccs_modified)
        self.__cc_api.SIG_CC_NODE_MODIFIED.connect(self.__cc_node_modified)
        self.__cc_api.SIG_CC_MODIFIED.connect(self.__cc_modified)

        self.__session_api.SIG_CURRENT_CLIP_CHANGED.connect(self.__current_clip_changed)
        self.__timeline_api.SIG_FRAME_CHANGED.connect(self.__frame_changed)
        self.__timeline_api.SIG_PLAY_STATUS_CHANGED.connect(self.__set_play_status)

        self.__interactive_mode = self.__rpa.session_api.get_custom_session_attr(C.INTERACTIVE_MODE)
        dm = self.__session_api.delegate_mngr
        dm.add_post_delegate(self.__session_api.set_custom_session_attr, self.__update_interactive_mode)

        self.__drawing_in_progress = False
        core_view = self.__main_window.get_core_view()
        core_view.installEventFilter(self)

    def __update_interactive_mode(self, out, attr_id, value):
        if attr_id == C.INTERACTIVE_MODE:
            self.__interactive_mode = value

    def eventFilter(self, obj, event):
        if not (
        event.type() == QtCore.QEvent.MouseButtonPress or
        event.type() == QtCore.QEvent.MouseMove or
        event.type() == QtCore.QEvent.MouseButtonRelease):
            return False

        get_pos = lambda: (event.pos().x(), obj.height() - event.pos().y())
        if self.__interactive_mode in (C.INTERACTIVE_MODE_RECTANGLE, C.INTERACTIVE_MODE_ELLIPSE, C.INTERACTIVE_MODE_LASSO):
            if event.type() == QtCore.QEvent.MouseButtonPress \
            and event.buttons() == QtCore.Qt.LeftButton \
            and event.modifiers() == QtCore.Qt.NoModifier:
                self.new_shape(*get_pos())
                self.__drawing_in_progress = True
            if self.__drawing_in_progress and event.type() == QtCore.QEvent.MouseMove:
                self.append_to_shape(*get_pos())
            if self.__drawing_in_progress and event.type() == QtCore.QEvent.MouseButtonRelease:
                self.finish_shape(*get_pos())
                self.__drawing_in_progress = False
        return False

    @property
    def view(self):
        return self.__view

    @property
    def current_tab(self):
        return self.tab_widget.currentWidget()

    @property
    def current_clip(self):
        return self.__session_api.get_current_clip()

    @property
    def tab_widget(self):
        return self.__view.tab_widget

    def __connect_footer_signals(self):
        footer = self.__view.footer
        footer.SIG_COPY_CLICKED.connect(self.__copy_clicked)
        footer.SIG_PASTE_CLICKED.connect(self.__paste_clicked)
        footer.SIG_MUTE_TAB_CLICKED.connect(self.__mute_tab)
        footer.SIG_MUTE_ALL_TABS_CLICKED.connect(self.__mute_all_tabs)
        footer.SIG_PRINT_CLICKED.connect(self.__print_clicked)
        footer.SIG_EMAIL_ALL_CLICKED.connect(self.__email_all_clicked)
        footer.SIG_PUBLISH_CLICKED.connect(self.__publish_clicked)

    def __connect_signals(self, tab):
        # Colortimer signals
        tab.SIG_CREATE_COLORTIMER.connect(self.__create_colortimer)
        tab.SIG_OFFSET_CHANGED.connect(self.__offset_changed)
        tab.SIG_SLOPE_CHANGED.connect(self.__slope_changed)
        tab.SIG_POWER_CHANGED.connect(self.__power_changed)
        tab.SIG_SAT_CHANGED.connect(self.__sat_changed)
        tab.SIG_MUTE_COLOR_TIMER.connect(self.__mute_clicked)
        tab.SIG_RESET_COLOR_TIMER.connect(self.__color_timer_reset_clicked)
        tab.SIG_DELETE_COLOR_TIMER.connect(self.__delete_node)

        # Grade signals
        tab.SIG_CREATE_GRADE.connect(self.__create_grade)
        tab.SIG_FSTOP_CHANGED.connect(self.__fstop_changed)
        tab.SIG_GAMMA_CHANGED.connect(self.__gamma_changed)
        tab.SIG_BLACKPOINT_CHANGED.connect(self.__blackpoint_changed)
        tab.SIG_WHITEPOINT_CHANGED.connect(self.__whitepoint_changed)
        tab.SIG_LIFT_CHANGED.connect(self.__lift_changed)
        tab.SIG_MUTE_GRADE.connect(self.__mute_clicked)
        tab.SIG_RESET_GRADE.connect(self.__grade_reset_clicked)
        tab.SIG_DELETE_GRADE.connect(self.__delete_node)

        # Region signals
        tab.SIG_CREATE_REGION.connect(self.__create_region)
        tab.SIG_DELETE_REGION.connect(self.__delete_region)
        tab.SIG_FALLOFF_CHANGED.connect(self.__falloff_changed)

    def __disconnect_signals(self, tab):
        # ColorTimer signals
        tab.SIG_CREATE_COLORTIMER.disconnect(self.__create_colortimer)
        tab.SIG_OFFSET_CHANGED.disconnect(self.__offset_changed)
        tab.SIG_SLOPE_CHANGED.disconnect(self.__slope_changed)
        tab.SIG_POWER_CHANGED.disconnect(self.__power_changed)
        tab.SIG_SAT_CHANGED.disconnect(self.__sat_changed)
        tab.SIG_MUTE_COLOR_TIMER.disconnect(self.__mute_clicked)
        tab.SIG_RESET_COLOR_TIMER.disconnect(self.__color_timer_reset_clicked)
        tab.SIG_DELETE_COLOR_TIMER.disconnect(self.__delete_node)

        # Grade signals
        tab.SIG_CREATE_GRADE.disconnect(self.__create_grade)
        tab.SIG_FSTOP_CHANGED.disconnect(self.__fstop_changed)
        tab.SIG_GAMMA_CHANGED.disconnect(self.__gamma_changed)
        tab.SIG_BLACKPOINT_CHANGED.disconnect(self.__blackpoint_changed)
        tab.SIG_WHITEPOINT_CHANGED.disconnect(self.__whitepoint_changed)
        tab.SIG_LIFT_CHANGED.disconnect(self.__lift_changed)
        tab.SIG_MUTE_GRADE.disconnect(self.__mute_clicked)
        tab.SIG_RESET_GRADE.disconnect(self.__grade_reset_clicked)
        tab.SIG_DELETE_GRADE.disconnect(self.__delete_node)

        # Region signals
        tab.SIG_CREATE_REGION.disconnect(self.__create_region)
        tab.SIG_DELETE_REGION.disconnect(self.__delete_region)
        tab.SIG_FALLOFF_CHANGED.disconnect(self.__falloff_changed)

    def new_shape(self, x, y):
        """
        Draws a new shape in the view given (x,y) points.
        """
        # TODO: do not allow shapes for clip CCs due to incompatibility with itview4 and sync server
        if self.current_tab == self.tab_widget.clip_tab:
            return
        geometry = self.__viewport_api.get_current_clip_geometry()
        if geometry is None:
            return
        self.__points = [screen_to_itview(geometry, x, y)]
        if self.__interactive_mode == C.INTERACTIVE_MODE_LASSO:
            self.__transient_points.append(screen_to_itview(geometry, x, y))

    def append_to_shape(self, x, y):
        """
        Continues to append (x,y) points to the existing region shape.
        """
        # TODO: do not allow shapes for clip CCs due to incompatibility with itview4 and sync server
        if self.current_tab == self.tab_widget.clip_tab:
            return
        geometry = self.__viewport_api.get_current_clip_geometry()
        if geometry is None:
            return
        if self.__interactive_mode == C.INTERACTIVE_MODE_LASSO:
            self.__transient_points.append(screen_to_itview(geometry, x, y))

    def finish_shape(self, x, y):
        """
        Finish shape drawing and plot points according to shape selection.
        """
        # TODO: do not allow shapes for clip CCs due to incompatibility with itview4 and sync server
        if self.current_tab == self.tab_widget.clip_tab:
            return
        geometry = self.__viewport_api.get_current_clip_geometry()
        if geometry is None:
            return
        cc_id = self.current_tab.id
        if not self.__cc_api.has_region(self.current_clip, cc_id):
            self.__create_region(cc_id)
        self.__points.append(screen_to_itview(geometry, x, y))
        if self.__interactive_mode == C.INTERACTIVE_MODE_RECTANGLE:
            self.__plot_rectangle()
        if self.__interactive_mode == C.INTERACTIVE_MODE_ELLIPSE:
            self.__plot_ellipse()
        if self.__interactive_mode == C.INTERACTIVE_MODE_LASSO:
            self.__transient_points.append(screen_to_itview(geometry, x, y))
            self.__cc_api.append_shape_to_region(self.current_clip, cc_id, self.__transient_points)
            self.__transient_points = []

    def __plot_rectangle(self):
        """
        Draw rectangle shape.
        """
        points = []
        points.append((self.__points[0][0], self.__points[0][1]))
        points.append((self.__points[1][0], self.__points[0][1]))
        points.append((self.__points[1][0], self.__points[1][1]))
        points.append((self.__points[0][0], self.__points[1][1]))
        cc_id = self.current_tab.id
        self.__cc_api.append_shape_to_region(self.current_clip, cc_id, points)

    def __plot_ellipse(self):
        """
        Draw ellipse.
        """
        center = ((self.__points[0][0] + self.__points[1][0]) / 2, (self.__points[0][1] + self.__points[1][1]) / 2)
        a = abs(self.__points[1][0] - self.__points[0][0]) / 2
        b = abs(self.__points[1][1] - self.__points[0][1]) / 2
        number_of_points = int(np.clip(max(a,b), 20, 50))
        t = np.linspace(0, 2 * np.pi, number_of_points)
        x = center[0] + a * np.cos(t)
        y = center[1] + b * np.sin(t)
        points=[(a, b) for a, b in zip(x, y)]
        cc_id = self.current_tab.id
        self.__cc_api.append_shape_to_region(self.current_clip, cc_id, points)

    def __copy_clicked(self):
        self.__clipboard_cc = self.current_tab.id

    def __paste_clicked(self):
        cc_id = self.current_tab.id
        self.__cc_api.clear_nodes(self.current_clip, cc_id)
        nodes = self.__cc_api.get_nodes(self.current_clip, self.__clipboard_cc)
        self.__cc_api.append_nodes(self.current_clip, cc_id, nodes)

    def __mute_tab(self):
        if not self.current_tab: return
        cc_id = self.current_tab.id
        clip_id = self.current_clip
        is_mute = self.__cc_api.is_mute(clip_id, cc_id)
        self.__cc_api.mute(clip_id, cc_id, not is_mute)

    def __mute_all_tabs(self):
        clip_id = self.current_clip
        is_mute_all = self.__cc_api.is_mute_all(clip_id)
        self.__cc_api.mute_all(clip_id, not is_mute_all)

    def __print_clicked(self):
        monitor_data = self.__clip_tab.monitor.get_dict()
        relative_monitor_data = self.__clip_tab.relative_monitor.get_dict()
        color_grade_data = self.__clip_tab.color_timer.get_dict()

        cc_string = "\nMonitor:"
        for key in monitor_data:
            cc_string += "\n\t{0} {1}".format(key, monitor_data[key])
        cc_string += "\nRelative Clip Monitor:"
        for key in relative_monitor_data:
            cc_string += "\n\t{0} {1}".format(key, relative_monitor_data[key])
        cc_string += "\nClip Color Grade:"

        frame_tab = self.__view.frame_tab
        relative_monitor_data = frame_tab.relative_monitor.get_value_dict()
        color_grade_data = frame_tab.color_timer.get_value_dict()

        cc_string += "\nRelative Frame Monitor:"
        for key in relative_monitor_data:
            cc_string += "\n\t{0} {1}".format(key, relative_monitor_data[key])
        cc_string += "\nFrame Color Grade:"

        for index in range(self.tab_widget.count()):
            tab_text = self.tab_widget.tabText(index)
            if tab_text != "+" and index >= 2:
                widget = self.tab_widget.widget(index)
                cc_string += "\n{0} :".format(tab_text)
                cc_string += "\n\tRelative Region Monitor:"
                rel_monitor = widget.relative_monitor.get_value_dict()
                for key in rel_monitor:
                    cc_string += "\n\t\t{0} {1}".format(key, rel_monitor[key])

                cc_string += "\n\tRegion Color Grade:"
        print(cc_string)

    def __email_all_clicked(self):
        print("Email all clicked")

    def __publish_clicked(self):
        print("Publish")

    def __create_colortimer(self, cc_id):
        clip_id = self.__session_api.get_current_clip()
        colortimer = self.__cc_api.append_nodes(clip_id, cc_id, [ColorTimer()])

    def __create_grade(self, cc_id):
        clip_id = self.__session_api.get_current_clip()
        grade = self.__cc_api.append_nodes(clip_id, cc_id, [Grade()])

    def __offset_changed(self, cc_id, node_index, rgb):
        values = {"offset" : rgb}
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, values)

    def __power_changed(self, cc_id, node_index, rgb):
        values = {"power" : rgb}
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, values)

    def __slope_changed(self, cc_id, node_index, rgb):
        values = {"slope" : rgb}
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, values)

    def __sat_changed(self, cc_id, node_index, value):
        value = {"saturation" : value}
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, value)

    def __color_timer_reset_clicked(self, cc_id, node_index):
        node = self.__cc_api.get_node(self.current_clip, cc_id, node_index)
        if node.mute: return
        colortimer = ColorTimer().get_dict()
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, colortimer)

    def __fstop_changed(self, cc_id, node_index, rgb):
        values = {"gain" : rgb}
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, values)

    def __gamma_changed(self, cc_id, node_index, rgb):
        values = {"gamma" : rgb}
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, values)

    def __blackpoint_changed(self, cc_id, node_index, rgb):
        values = {"blackpoint" : rgb}
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, values)

    def __whitepoint_changed(self, cc_id, node_index, rgb):
        values = {"whitepoint" : rgb}
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, values)

    def __lift_changed(self, cc_id, node_index, rgb):
        values = {"lift" : rgb}
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, values)

    def __grade_reset_clicked(self, cc_id, node_index):
        node = self.__cc_api.get_node(self.current_clip, cc_id, node_index)
        if node.mute: return
        grade = Grade().get_dict()
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, grade)

    def __mute_clicked(self, cc_id, node_index):
        node = self.__cc_api.get_node(self.current_clip, cc_id, node_index)
        value = {"mute" : not node.mute}
        self.__cc_api.set_node_properties(self.current_clip, cc_id, node_index, value)

    def __delete_node(self, cc_id, node_index):
        self.__cc_api.delete_node(self.current_clip, cc_id, node_index)

    # Region
    def __create_region(self, cc_id):
        region = self.__cc_api.create_region(self.current_clip, cc_id)

    def __delete_region(self, cc_id):
        self.__cc_api.delete_region(self.current_clip, cc_id)

    def __falloff_changed(self, cc_id, value):
        self.__cc_api.set_region_falloff(self.current_clip, cc_id, value)

    # UI modified
    @QtCore.Slot(str)
    def __append_tab(self, name):
        clip_id = self.__session_api.get_current_clip()
        frame = self.__get_current_clip_frame()
        ccs = self.__cc_api.append_ccs(clip_id, [name], frame)
        if not ccs: return
        self.__cc_api.append_nodes(clip_id, ccs[0], [ColorTimer()])
        self.__cc_api.append_nodes(clip_id, ccs[0], [Grade()])
        self.__cc_api.create_region(clip_id, ccs[0])

    @QtCore.Slot(int, int)
    def __reorder_tabs(self, from_index, to_index):
        clip_id = self.__session_api.get_current_clip()
        frame = self.__get_current_clip_frame()
        clip_ccs = self.__cc_api.get_cc_ids(clip_id)
        self.__cc_api.move_cc(
            clip_id,
            from_index-len(clip_ccs),
            to_index-len(clip_ccs),
            frame)

    @QtCore.Slot(str)
    def __tab_closed(self, cc_id):
        tab = self.tab_widget.get_tab(cc_id)
        if tab is None: return
        self.__disconnect_signals(tab)
        self.tab_widget.delete_tab(cc_id)
        clip_id = self.__session_api.get_current_clip()
        frame = self.__get_current_clip_frame()
        self.__cc_api.delete_ccs(clip_id, [cc_id], frame)

    @QtCore.Slot(str, str)
    def __tab_renamed(self, cc_id, name):
        clip_id = self.__session_api.get_current_clip()
        self.__cc_api.set_name(clip_id, cc_id, name)

    # Session playback modified
    @QtCore.Slot(str)
    def __current_clip_changed(self, clip_id):
        playing, _ = self.__timeline_api.get_playing_state()
        if playing: return
        self.__delete_tabs()
        self.__ccs_modified(clip_id)

    @QtCore.Slot(int)
    def __frame_changed(self, sequence_frame=None, src_frame=None):
        playing, _ = self.__timeline_api.get_playing_state()
        scrubbing = self.__session_api.get_custom_session_attr("is_timeline_scrubbing")
        if playing or scrubbing:
            return
        widget = QtWidgets.QApplication.focusWidget()
        clip_id = self.__session_api.get_current_clip()
        self.__delete_tabs()
        self.__ccs_modified(clip_id)

    @QtCore.Slot(bool, bool)
    def __set_play_status(self, playing, forward):
        if not playing:
            # Update UI when the playback is paused
            self.__current_clip_changed(self.__session_api.get_current_clip())

    # API modified
    @QtCore.Slot(str, object)
    def __ccs_modified(self, clip_id, frame=None):
        """ This method is called when SIG_CCS_MODIFIED is emitted.
            Whenever there is a change in tabs - muted, creation, deletion or tabs
            are moved around, this signal is emitted.

            Args:
                clip_id: id of the clip where ccs are modified.
                frame(int, optional): frame number, if the cc modified is in a particular frame,
                            if it is a clip cc, frame is None.
        """
        mute_all = self.__cc_api.is_mute_all(clip_id)
        if self.tab_widget.is_all_mute() != mute_all:
            self.tab_widget.mute_all_tabs(mute_all)
            return
        if frame is None:
            frame = self.__get_current_clip_frame()
        curr_frame = self.__get_current_clip_frame()
        if frame != curr_frame: return
        self.__tabs_modified(clip_id, frame)

    @QtCore.Slot(str, str)
    def __cc_modified(self, clip_id, cc_id):
        """ This method is called when SIG_CC_MODIFIED is emitted.
            The signal gets emitted when there are changes to the current tab.
            For example if name, read_only, mute changes, or when
            nodes(Colortimer, Grade) get added or deleted or when region gets modified.
        """
        tab = self.tab_widget.get_tab(cc_id)
        if not tab: return
        is_ro = self.__cc_api.is_read_only(clip_id, cc_id)
        if is_ro and tab.is_read_only() != is_ro:
            self.tab_widget.lock(tab)
            return
        is_mute = self.__cc_api.is_mute(clip_id, cc_id)
        if tab.is_mute() != is_mute:
            tab.mute_all(is_mute)
            return
        name = self.__cc_api.get_name(clip_id, cc_id)
        if tab.name != name:
            self.tab_widget.set_name(tab, name)
            return
        self.__nodes_modified(clip_id, tab)
        self.__region_modified(clip_id, cc_id)

    @QtCore.Slot(str, str, int)
    def __cc_node_modified(self, clip_id, cc_id, node_index):
        """ This method is called when SIG_CC_NODE_MODIFIED is emitted.
            The signal gets emitted when there are changes to the values
            in any of the nodes(Colortimer or Grade).
            The node is indicated by the node_index.
        """
        node = self.__cc_api.get_node(clip_id, cc_id, node_index)
        tab = self.tab_widget.get_tab(cc_id)
        if not tab: return
        tab.set_node_values(node_index, node)

    def __delete_tabs(self):
        for tab in self.tab_widget.get_tabs():
            if tab == self.tab_widget.clip_tab: continue
            self.__disconnect_signals(tab)
        self.tab_widget.clear_all_tabs()

    def __region_modified(self, clip_id, cc_id):
        tab = self.tab_widget.get_tab(cc_id)
        if not tab: return
        cc_region = self.__cc_api.has_region(clip_id, cc_id)
        if not cc_region and not tab.region:
            return
        if not cc_region and tab.region:
            tab.delete_region()
            return
        if cc_region and not tab.region:
            tab.create_region()
        tab.set_falloff(self.__cc_api.get_region_falloff(clip_id, cc_id))

    def __nodes_modified(self, clip_id, tab):
        """
        This method is called when nodes(Colortimer, Grade) within a tab
        gets created or deleted.
        """
        tab.clear_nodes()
        for index, node in enumerate(self.__cc_api.get_nodes(clip_id, tab.id)):
            if isinstance(node, ColorTimer): tab.create_colortimer()
            if isinstance(node, Grade): tab.create_grade()
            tab.set_node_values(index, node)

    def __tabs_modified(self, clip_id, frame):
        if clip_id != self.current_clip: return
        clip_tabs = self.__cc_api.get_cc_ids(clip_id)
        new_tabs = clip_tabs + self.__cc_api.get_cc_ids(clip_id, frame)
        ui_tabs = [tab.id for tab in self.tab_widget.get_tabs()]
        if new_tabs == ui_tabs: return
        # Update the existing clip tab
        for index, cc_id in enumerate(ui_tabs):
            if cc_id is None:
                new_tab_id = None
                if new_tabs:
                    new_tab_id = new_tabs[index]
                self.tab_widget.update_clip_tab(new_tab_id)
                self.__nodes_modified(clip_id, self.tab_widget.clip_tab)
                self.__region_modified(clip_id, new_tab_id)
                ui_tabs[index] = new_tab_id
                break
        # Delete tabs
        for cc_id in reversed(ui_tabs):
            if cc_id and cc_id not in new_tabs:
                self.__disconnect_signals(self.tab_widget.get_tab(cc_id))
                self.tab_widget.delete_tab(cc_id)
                ui_tabs.remove(cc_id)
        # Append tabs
        for cc_id in new_tabs:
            if cc_id not in ui_tabs:
                cc_type = "clip" if cc_id in clip_tabs else "frame"
                tab = self.tab_widget.append_tab(
                    cc_id,
                    self.__cc_api.get_name(clip_id, cc_id),
                    type=cc_type)
                self.__connect_signals(tab)
                self.__nodes_modified(clip_id, tab)
                self.__region_modified(clip_id, cc_id)
                if self.__cc_api.is_read_only(clip_id, cc_id):
                    self.tab_widget.lock(tab)
        ui_tabs = [tab.id for tab in self.tab_widget.get_tabs()]
        # Move tabs
        for i, cc_id in enumerate(new_tabs):
            tab_index = ui_tabs.index(cc_id)
            if tab_index != i:
                self.tab_widget.move_tab(tab_index, i)
                ui_tabs.insert(i, ui_tabs.pop(tab_index))

    def __get_current_clip_frame(self):
        [clip_frame] = self.__timeline_api.get_clip_frames([self.__timeline_api.get_current_frame()])
        if type(clip_frame) is not tuple:
            return -1
        return clip_frame[1]
