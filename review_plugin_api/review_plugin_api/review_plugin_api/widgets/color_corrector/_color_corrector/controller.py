"""
Controller for Color Corrector
"""
import numpy as np
from PySide2 import QtCore, QtWidgets
from review_plugin_api.widgets.color_corrector._color_corrector.view.view \
    import View
from review_plugin_api.widgets.color_corrector._color_corrector.model \
    import ClipModel, RegionModel, FrameModel, Slider, RegionName, TabType
from review_plugin_api.widgets.color_corrector._color_corrector.view.\
    color_corrector import RegionTab
from review_plugin_api.widgets.color_corrector._color_corrector.view.slider_attrs \
    import build_slider_attrs


class ControllerSignals(QtCore.QObject):
    SIG_CLOSE = QtCore.Signal()

class Controller(QtCore.QObject):
    def __init__(self, review_plugin_api, main_window):
        super().__init__()
        self.__review_plugin_api = review_plugin_api
        self.__main_window = main_window

        self.__cc_api = review_plugin_api.color_corrector_api
        self.__timeline_api = review_plugin_api.timeline_api

        attrs = build_slider_attrs()
        self.__view = View(attrs, self.__main_window)
        self.__clip_model = ClipModel()
        self.__frame_model = FrameModel()
        self.__region_model = RegionModel()

        self.__connect_clip_tab_signals()
        self.__connect_frame_tab_signals()
        self.__copy_color_timer = None
        self.__copy_grade = None
        self.__curr_shape_guid = None

        self.__is_all_tabs_muted = False
        self.__is_tab_muted = False

        self.tab_widget.SIG_REGION_TAB_CREATED.connect(self.__connect_region_tab_signals)
        self.tab_widget.SIG_REGION_CREATED.connect(self.__create_region_cc)
        self.tab_widget.SIG_REGION_TAB_CLOSED.connect(self.__delete_region_cc)
        self.tab_widget.SIG_REORDER_REGIONS.connect(self.__reorder_regions)

        self.signals = ControllerSignals()
        self.SIG_CLOSE = self.signals.SIG_CLOSE
        self.__view.SIG_CLOSE.connect(self.SIG_CLOSE)
        self.__timeline_api.SIG_FRAME_CHANGED.connect(self.__frame_changed)

        self.__dock_widget = QtWidgets.QDockWidget("Color Correction", self.__main_window)
        self.__dock_widget.setObjectName("Color Corrector Widget")
        self.__dock_widget.setWidget(self.__view)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__dock_widget)
        self.__dock_widget.hide()
        self.__initialize()

    def is_visible(self):
        return self.__dock_widget.isVisible()

    def show(self):
        """ Dock the Color Corrector window. """
        self.__dock_widget.show()

    def hide(self):
        """ Dock the Color Corrector window. """
        return self.__dock_widget.hide()

    @property
    def tab_widget(self):
        return self.__view.tab_widget

    @property
    def cc_guid(self):
        return self.current_tab.get_cc_guid()

    def __connect_clip_tab_signals(self):
        self.__clip_tab = self.__view.clip_tab
        # ColorTimer signals
        self.__clip_tab.SIG_OFFSET_CHANGED.connect(self.__clip_offset_changed)
        self.__clip_tab.SIG_SLOPE_CHANGED.connect(self.__clip_slope_changed)
        self.__clip_tab.SIG_POWER_CHANGED.connect(self.__clip_power_changed)
        self.__clip_tab.SIG_SAT_CHANGED.connect(self.__clip_sat_changed)
        self.__clip_tab.SIG_MUTE_COLOR_TIMER.connect(self.__clip_color_timer_mute_clicked)
        self.__clip_tab.SIG_RESET_COLOR_TIMER.connect(self.__clip_color_timer_reset_clicked)
        # Grade signals
        self.__clip_tab.SIG_FSTOP_CHANGED.connect(self.__clip_fstop_changed)
        self.__clip_tab.SIG_GAMMA_CHANGED.connect(self.__clip_gamma_changed)
        self.__clip_tab.SIG_BLACKPOINT_CHANGED.connect(self.__clip_blackpoint_changed)
        self.__clip_tab.SIG_WHITEPOINT_CHANGED.connect(self.__clip_whitepoint_changed)
        self.__clip_tab.SIG_LIFT_CHANGED.connect(self.__clip_lift_changed)
        self.__clip_tab.SIG_MUTE_GRADE.connect(self.__clip_grade_mute_clicked)
        self.__clip_tab.SIG_RESET_GRADE.connect(self.__clip_grade_reset_clicked)

    def __connect_frame_tab_signals(self):
        self.__frame_tab = self.__view.frame_tab
        # ColorTimer signals
        self.__frame_tab.SIG_OFFSET_CHANGED.connect(self.__frame_offset_changed)
        self.__frame_tab.SIG_SLOPE_CHANGED.connect(self.__frame_slope_changed)
        self.__frame_tab.SIG_POWER_CHANGED.connect(self.__frame_power_changed)
        self.__frame_tab.SIG_SAT_CHANGED.connect(self.__frame_sat_changed)
        self.__frame_tab.SIG_MUTE_COLOR_TIMER.connect(self.__frame_color_timer_mute_clicked)
        self.__frame_tab.SIG_RESET_COLOR_TIMER.connect(self.__frame_color_timer_reset_clicked)

        # Grade signals
        self.__frame_tab.SIG_FSTOP_CHANGED.connect(self.__frame_fstop_changed)
        self.__frame_tab.SIG_GAMMA_CHANGED.connect(self.__frame_gamma_changed)
        self.__frame_tab.SIG_BLACKPOINT_CHANGED.connect(self.__frame_blackpoint_changed)
        self.__frame_tab.SIG_WHITEPOINT_CHANGED.connect(self.__frame_whitepoint_changed)
        self.__frame_tab.SIG_LIFT_CHANGED.connect(self.__frame_lift_changed)
        self.__frame_tab.SIG_MUTE_GRADE.connect(self.__frame_grade_mute_clicked)
        self.__frame_tab.SIG_RESET_GRADE.connect(self.__frame_grade_reset_clicked)

    def __connect_region_tab_signals(self, region_tab):
        # ColorTimer signals
        region_tab.SIG_OFFSET_CHANGED.connect(self.__region_offset_changed)
        region_tab.SIG_SLOPE_CHANGED.connect(self.__region_slope_changed)
        region_tab.SIG_POWER_CHANGED.connect(self.__region_power_changed)
        region_tab.SIG_SAT_CHANGED.connect(self.__region_sat_changed)
        region_tab.SIG_MUTE_COLOR_TIMER.connect(self.__region_color_timer_mute_clicked)
        region_tab.SIG_RESET_COLOR_TIMER.connect(self.__region_color_timer_reset_clicked)

        # Grade signals
        region_tab.SIG_FSTOP_CHANGED.connect(self.__region_fstop_changed)
        region_tab.SIG_GAMMA_CHANGED.connect(self.__region_gamma_changed)
        region_tab.SIG_BLACKPOINT_CHANGED.connect(self.__region_blackpoint_changed)
        region_tab.SIG_WHITEPOINT_CHANGED.connect(self.__region_whitepoint_changed)
        region_tab.SIG_LIFT_CHANGED.connect(self.__region_lift_changed)
        region_tab.SIG_MUTE_GRADE.connect(self.__region_grade_mute_clicked)
        region_tab.SIG_RESET_GRADE.connect(self.__region_grade_reset_clicked)

    def __disconnect_signals(self, region_tab):
        # ColorTimer signals
        region_tab.SIG_OFFSET_CHANGED.disconnect(self.__region_offset_changed)
        region_tab.SIG_SLOPE_CHANGED.disconnect(self.__region_slope_changed)
        region_tab.SIG_POWER_CHANGED.disconnect(self.__region_power_changed)
        region_tab.SIG_SAT_CHANGED.disconnect(self.__region_sat_changed)
        region_tab.SIG_MUTE_COLOR_TIMER.disconnect(self.__region_color_timer_mute_clicked)
        region_tab.SIG_RESET_COLOR_TIMER.disconnect(self.__region_color_timer_reset_clicked)

        # Grade signals
        region_tab.SIG_FSTOP_CHANGED.disconnect(self.__region_fstop_changed)
        region_tab.SIG_GAMMA_CHANGED.disconnect(self.__region_gamma_changed)
        region_tab.SIG_BLACKPOINT_CHANGED.disconnect(self.__region_blackpoint_changed)
        region_tab.SIG_WHITEPOINT_CHANGED.disconnect(self.__region_whitepoint_changed)
        region_tab.SIG_LIFT_CHANGED.disconnect(self.__region_lift_changed)
        region_tab.SIG_MUTE_GRADE.disconnect(self.__region_grade_mute_clicked)
        region_tab.SIG_RESET_GRADE.disconnect(self.__region_grade_reset_clicked)

    @property
    def current_tab(self):
        return self.tab_widget.currentWidget()

    @property
    def current_frame(self):
        return self.__timeline_api.get_current_frame()

    def __frame_changed(self, frame):
        if self.__timeline_api.is_playing(): return
        widget = QtWidgets.QApplication.focusWidget()
        if frame in self.__frame_model.get_frames():
            frame_color_timer = self.__frame_model.get_view_color_timer(frame)
            frame_grade = self.__frame_model.get_view_grade(frame)
        else:
            frame_color_timer = frame_grade = self.__cc_api.get_frame_cc(frame)
        self.__view.set_color_timer(frame_color_timer, is_mute=self.__frame_model.is_color_timer_muted(frame), tab=self.__frame_tab)
        self.__view.set_grade(frame_grade, is_mute=self.__frame_model.is_grade_muted(frame), tab=self.__frame_tab)

        region_ccs = self.__cc_api.get_region_ccs(frame)
        self.tab_widget.remove_region_tabs()
        for region in region_ccs:
            self.tab_widget.append_tab()
            self.current_tab.set_cc_guid(region['guid'])
            self.__view.set_color_timer(region, is_mute=self.__region_model.is_color_timer_muted(frame, region['guid']))
            self.__view.set_grade(region, is_mute=self.__region_model.is_grade_muted(frame, region['guid']))

    def __create_region_cc(self, region_tab):
        cc = self.__cc_api.create_region_cc(self.current_frame)
        if "exception" in cc:
            self.tab_widget.remove_tab(region_tab)
            return
        region_tab.set_cc_guid(cc["guid"])
        region_cc = self.__cc_api.get_region_cc(self.current_frame, cc["guid"])
        self.__view.set_region_color_timer(region_cc)
        self.__view.set_region_grade(region_cc)

    def __delete_region_cc(self, region_tab):
        """
        Delete the cc shape when a region tab is deleted.
        Args:
            region_tab(RegionTab): region tab to be deleted
        """
        self.__disconnect_signals(region_tab)
        self.__cc_api.delete_region_cc(self.current_frame, region_tab.get_cc_guid())

    def __reorder_regions(self, from_index, to_index):
        """
        Reorder region ccs given the from and to index of the region tabs moved.
        Args:
            from_index(int): Tab moved from index
            to_index(int): Tab moved to index
        """
        # -2 is to neglect the first two tab indexes(clip and frame).
        index = (from_index-2, to_index-2)
        curr_ccs = self.__cc_api.get_region_ccs(self.current_frame)
        curr_ccs[index[0]], curr_ccs[index[1]] = curr_ccs[index[1]], curr_ccs[index[0]]
        guids = [d.get('guid') for d in curr_ccs]
        self.__cc_api.reorder_region_ccs(self.current_frame, guids)

    def new_shape(self, x, y, mode):
        """
        Draws a new shape in the view given (x,y) points.
        """
        if not isinstance(self.current_tab, RegionTab):
            return False
        self.__points = []
        self.__points.append((x,y))
        self.__curr_shape_guid = self.__cc_api.create_shape(
            self.current_frame, self.cc_guid)
        if mode == RegionName.LASSO:
            self.__cc_api.append_point_to_shape(
                self.current_frame,
                self.cc_guid,
                self.__curr_shape_guid, x, y)
        self.__cc_api.set_drawing_in_progress(True)

    def append_to_shape(self, x, y, mode):
        """
        Continues to append (x,y) points to the existing region shape.
        """
        if not isinstance(self.current_tab, RegionTab):
            return False
        if mode == RegionName.LASSO:
            self.__cc_api.append_point_to_shape(
                self.current_frame,
                self.cc_guid,
                self.__curr_shape_guid, x, y)

    def finish_shape(self, x, y, mode):
        """
        Finish shape drawing and plot points according to shape selection.
        """
        if not isinstance(self.current_tab, RegionTab):
            return False
        self.__points.append((x,y))
        if mode == RegionName.RECTANGLE:
            self.__plot_rectangle()
        if mode == RegionName.ELLIPSE:
            self.__plot_ellipse()
        if mode == RegionName.LASSO:
            self.__cc_api.append_point_to_shape(
                self.current_frame,
                self.cc_guid,
                self.__curr_shape_guid, x, y)
        self.__cc_api.set_drawing_in_progress(False)

    def __plot_rectangle(self):
        """
        Draw rectangle shape.
        """
        self.__cc_api.append_point_to_shape(
            self.current_frame, self.cc_guid, self.__curr_shape_guid,
            self.__points[0][0], self.__points[0][1])
        self.__cc_api.append_point_to_shape(
            self.current_frame, self.cc_guid, self.__curr_shape_guid,
            self.__points[1][0], self.__points[0][1])
        self.__cc_api.append_point_to_shape(
            self.current_frame, self.cc_guid, self.__curr_shape_guid,
            self.__points[1][0], self.__points[1][1])
        self.__cc_api.append_point_to_shape(
            self.current_frame, self.cc_guid, self.__curr_shape_guid,
            self.__points[0][0], self.__points[1][1])

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

        self.__cc_api.append_points_to_shape(
                self.current_frame, self.cc_guid, self.__curr_shape_guid,
                list(zip(x,y)))

    def __initialize(self):
        # ColorTimer
        clip_cc = self.__cc_api.get_clip_cc(self.current_frame)
        self.__view.set_clip_color_timer(clip_cc)
        self.__view.set_clip_grade(clip_cc)

        frame_cc = self.__cc_api.get_frame_cc(self.current_frame)
        self.__view.set_frame_color_timer(frame_cc)
        self.__view.set_frame_grade(frame_cc)

    # ColorTimer
    def __clip_offset_changed(self, rgb):
        self.__clip_model.set_color_timer_knob(Slider.OFFSET.value, rgb)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_color_timer())

    def __clip_power_changed(self, rgb):
        self.__clip_model.set_color_timer_knob(Slider.POWER.value, rgb)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_color_timer())

    def __clip_slope_changed(self, rgb):
        self.__clip_model.set_color_timer_knob(Slider.SLOPE.value, rgb)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_color_timer())

    def __clip_sat_changed(self, value):
        self.__clip_model.set_color_timer_knob(Slider.SAT.value, value)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_color_timer())

    def __clip_color_timer_mute_clicked(self):
        mute = self.__clip_model.is_color_timer_muted()
        self.__clip_model.mute_color_timer(not mute)
        self.__clip_tab.mute_color_timer(not mute)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_color_timer())

    def __clip_color_timer_reset_clicked(self):
        if self.__clip_model.is_color_timer_muted(): return
        self.__clip_model.reset_color_timer()
        cc = self.__clip_model.get_color_timer()
        self.__view.set_color_timer(cc)
        self.__cc_api.set_clip_cc(self.current_frame, cc)

    def __frame_offset_changed(self, rgb):
        self.__frame_model.set_color_timer_knob(self.current_frame, Slider.OFFSET.value, rgb)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_color_timer(self.current_frame))

    def __frame_power_changed(self, rgb):
        self.__frame_model.set_color_timer_knob(self.current_frame, Slider.POWER.value, rgb)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_color_timer(self.current_frame))

    def __frame_slope_changed(self, rgb):
        self.__frame_model.set_color_timer_knob(self.current_frame, Slider.SLOPE.value, rgb)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_color_timer(self.current_frame))

    def __frame_sat_changed(self, value):
        self.__frame_model.set_color_timer_knob(self.current_frame, Slider.SAT.value, value)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_color_timer(self.current_frame))

    def __frame_color_timer_mute_clicked(self):
        mute = self.__frame_model.is_color_timer_muted(self.current_frame)
        self.__frame_model.mute_color_timer(self.current_frame, not mute)
        self.__frame_tab.mute_color_timer(not mute)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_color_timer(self.current_frame))

    def __frame_color_timer_reset_clicked(self):
        if self.__frame_model.is_color_timer_muted(self.current_frame): return
        self.__frame_model.reset_color_timer(self.current_frame)
        cc = self.__frame_model.get_color_timer(self.current_frame)
        self.__view.set_color_timer(cc)
        self.__cc_api.set_frame_cc(self.current_frame, cc)

    def __region_offset_changed(self, rgb):
        self.__region_model.set_color_timer_knob(self.current_frame, self.cc_guid, Slider.OFFSET.value, rgb)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_color_timer(self.current_frame, self.cc_guid))

    def __region_power_changed(self, rgb):
        self.__region_model.set_color_timer_knob(self.current_frame, self.cc_guid, Slider.POWER.value, rgb)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_color_timer(self.current_frame, self.cc_guid))

    def __region_slope_changed(self, rgb):
        self.__region_model.set_color_timer_knob(self.current_frame, self.cc_guid, Slider.SLOPE.value, rgb)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_color_timer(self.current_frame, self.cc_guid))

    def __region_sat_changed(self, value):
        self.__region_model.set_color_timer_knob(self.current_frame, self.cc_guid, Slider.SAT.value, value)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_color_timer(self.current_frame, self.cc_guid))

    def __region_color_timer_mute_clicked(self):
        mute = self.__region_model.is_color_timer_muted(self.current_frame, self.cc_guid)
        self.__region_model.mute_color_timer(self.current_frame, self.cc_guid, not mute)
        self.current_tab.mute_color_timer(not mute)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_color_timer(self.current_frame, self.cc_guid))

    def __region_color_timer_reset_clicked(self):
        if self.__region_model.is_color_timer_muted(): return
        self.__region_model.reset_color_timer()
        cc = self.__region_model.get_color_timer(self.current_frame, self.cc_guid)
        self.__view.set_region_color_timer(cc)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, cc)

    # Grade
    def __clip_fstop_changed(self, rgb):
        self.__clip_model.set_grade_knob(Slider.FSTOP.value, rgb)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_grade())

    def __clip_gamma_changed(self, rgb):
        self.__clip_model.set_grade_knob(Slider.GAMMA.value, rgb)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_grade())

    def __clip_blackpoint_changed(self, rgb):
        self.__clip_model.set_grade_knob(Slider.BLACKPOINT.value, rgb)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_grade())

    def __clip_whitepoint_changed(self, rgb):
        self.__clip_model.set_grade_knob(Slider.WHITEPOINT.value, rgb)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_grade())

    def __clip_lift_changed(self, value):
        self.__clip_model.set_grade_knob(Slider.LIFT.value, value)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_grade())

    def __clip_grade_mute_clicked(self):
        mute = self.__clip_model.is_grade_muted()
        self.__clip_model.mute_grade(not mute)
        self.__clip_tab.mute_grade(not mute)
        self.__cc_api.set_clip_cc(self.current_frame, self.__clip_model.get_grade())

    def __clip_grade_reset_clicked(self):
        if self.__clip_model.is_grade_muted(): return
        self.__clip_model.reset_grade()
        cc = self.__clip_model.get_grade()
        self.__view.set_clip_grade(cc)
        self.__cc_api.set_clip_cc(self.current_frame, cc)

    def __frame_fstop_changed(self, rgb):
        self.__frame_model.set_grade_knob(self.current_frame, Slider.FSTOP.value, rgb)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_grade(self.current_frame))

    def __frame_gamma_changed(self, rgb):
        self.__frame_model.set_grade_knob(self.current_frame, Slider.GAMMA.value, rgb)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_grade(self.current_frame))

    def __frame_blackpoint_changed(self, rgb):
        self.__frame_model.set_grade_knob(self.current_frame, Slider.BLACKPOINT.value, rgb)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_grade(self.current_frame))

    def __frame_whitepoint_changed(self, rgb):
        self.__frame_model.set_grade_knob(self.current_frame, Slider.WHITEPOINT.value, rgb)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_grade(self.current_frame))

    def __frame_lift_changed(self, rgb):
        self.__frame_model.set_grade_knob(self.current_frame, Slider.LIFT.value, rgb)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_grade(self.current_frame))

    def __frame_grade_mute_clicked(self):
        mute = self.__frame_model.is_grade_muted(self.current_frame)
        self.__frame_model.mute_grade(self.current_frame, not mute)
        self.__frame_tab.mute_grade(not mute)
        self.__cc_api.set_frame_cc(self.current_frame, self.__frame_model.get_grade(self.current_frame))

    def __frame_grade_reset_clicked(self):
        if self.__frame_model.is_grade_muted(self.current_frame): return
        self.__frame_model.reset_grade(self.current_frame)
        cc = self.__frame_model.get_grade(self.current_frame)
        self.__view.set_frame_grade(cc)
        self.__cc_api.set_frame_cc(self.current_frame, cc)

    def __region_fstop_changed(self, rgb):
        self.__region_model.set_grade_knob(self.current_frame, self.cc_guid, Slider.FSTOP.value, rgb)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_grade(self.current_frame, self.cc_guid))

    def __region_gamma_changed(self, rgb):
        self.__region_model.set_grade_knob(self.current_frame, self.cc_guid, Slider.GAMMA.value, rgb)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_grade(self.current_frame, self.cc_guid))

    def __region_blackpoint_changed(self, rgb):
        self.__region_model.set_grade_knob(self.current_frame, self.cc_guid, Slider.BLACKPOINT.value, rgb)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_grade(self.current_frame, self.cc_guid))

    def __region_whitepoint_changed(self, rgb):
        self.__region_model.set_grade_knob(self.current_frame, self.cc_guid, Slider.WHITEPOINT.value, rgb)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_grade(self.current_frame, self.cc_guid))

    def __region_lift_changed(self, rgb):
        self.__region_model.set_grade_knob(self.current_frame, self.cc_guid, Slider.LIFT.value, rgb)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_grade(self.current_frame, self.cc_guid))

    def __region_grade_mute_clicked(self):
        mute = self.__region_model.is_grade_muted(self.current_frame, self.cc_guid)
        self.__region_model.mute_grade(self.current_frame, self.cc_guid, not mute)
        self.current_tab.mute_grade(not mute)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, self.__region_model.get_grade(self.current_frame, self.cc_guid))

    def __region_grade_reset_clicked(self):
        if self.__region_model.is_grade_muted(): return
        self.__region_model.reset_grade()
        cc = self.__region_model.get_grade(self.current_frame, self.cc_guid)
        self.__view.set_region_grade(cc)
        self.__cc_api.set_region_cc(self.current_frame, self.cc_guid, cc)