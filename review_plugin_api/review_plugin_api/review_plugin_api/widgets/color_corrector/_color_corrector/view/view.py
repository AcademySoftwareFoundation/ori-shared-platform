"""
View for Color Corrector
"""

from PySide2 import QtCore, QtGui, QtWidgets
from review_plugin_api.widgets.color_corrector.widgets.mini_label_button \
    import MiniLabelButton
from review_plugin_api.widgets.color_corrector._color_corrector.view.tab_widget \
    import ColorCorrectorTabWidget
from review_plugin_api.widgets.color_corrector._color_corrector.model import Slider


class View(QtWidgets.QWidget):
    SIG_CLOSE = QtCore.Signal()
    def __init__(self, slider_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Color Correction")
        self.setGeometry(0, 0, 400, 770)

        self.__tab_widget = ColorCorrectorTabWidget(self, slider_data)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.__tab_widget)
        self.setLayout(layout)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.SIG_CLOSE.emit()

    @property
    def tab_widget(self):
        return self.__tab_widget

    @property
    def current_tab(self):
        return self.tab_widget.currentWidget()

    @property
    def clip_tab(self):
        return self.__tab_widget.clip_tab

    @property
    def frame_tab(self):
        return self.__tab_widget.frame_tab

    def set_color_timer(self, value, is_mute=False, tab=None):
        if tab is None: tab = self.current_tab
        tab.color_timer.set_offset(value[Slider.OFFSET.value])
        tab.color_timer.set_slope(value[Slider.SLOPE.value])
        tab.color_timer.set_power(value[Slider.POWER.value])
        tab.color_timer.set_sat(value[Slider.SAT.value])
        tab.color_timer.set_mute(is_mute)

    def set_grade(self, value, is_mute=False, tab=None):
        if tab is None: tab = self.current_tab
        tab.grade.set_fstop(value[Slider.FSTOP.value])
        tab.grade.set_gamma(value[Slider.GAMMA.value])
        tab.grade.set_blackpoint(value[Slider.BLACKPOINT.value])
        tab.grade.set_whitepoint(value[Slider.WHITEPOINT.value])
        tab.grade.set_lift(value[Slider.LIFT.value])
        tab.grade.set_mute(is_mute)

    def set_offset(self, offset):
        self.current_tab.color_timer.set_offset(offset)

    def set_slope(self, slope):
        self.current_tab.color_timer.set_slope(slope)

    def set_power(self, power):
        self.current_tab.color_timer.set_power(power)

    def set_sat(self, sat):
        self.current_tab.color_timer.set_sat(sat)

    def set_fstop(self, fstop):
        self.current_tab.color_timer.set_fstop(fstop)

    def set_gamma(self, slope):
        self.current_tab.color_timer.set_slope(slope)

    def set_blackpoint(self, blackpoint):
        self.current_tab.color_timer.set_blackpoint(blackpoint)

    def set_whitepoint(self, whitepoint):
        self.current_tab.color_timer.set_whitepoint(whitepoint)

    def set_lift(self, lift):
        self.current_tab.color_timer.set_lift(lift)

    def set_clip_color_timer(self, value, is_mute=False):
        self.clip_tab.color_timer.set_offset(value[Slider.OFFSET.value])
        self.clip_tab.color_timer.set_slope(value[Slider.SLOPE.value])
        self.clip_tab.color_timer.set_power(value[Slider.POWER.value])
        self.clip_tab.color_timer.set_sat(value[Slider.SAT.value])
        self.clip_tab.color_timer.set_mute(is_mute)

    def set_frame_color_timer(self, value, is_mute=False):
        self.frame_tab.color_timer.set_offset(value[Slider.OFFSET.value])
        self.frame_tab.color_timer.set_slope(value[Slider.SLOPE.value])
        self.frame_tab.color_timer.set_power(value[Slider.POWER.value])
        self.frame_tab.color_timer.set_sat(value[Slider.SAT.value])
        self.frame_tab.color_timer.set_mute(is_mute)

    def set_region_color_timer(self, value, is_mute=False):
        self.current_tab.color_timer.set_offset(value[Slider.OFFSET.value])
        self.current_tab.color_timer.set_slope(value[Slider.SLOPE.value])
        self.current_tab.color_timer.set_power(value[Slider.POWER.value])
        self.current_tab.color_timer.set_sat(value[Slider.SAT.value])
        self.current_tab.color_timer.set_mute(is_mute)

    def set_clip_grade(self, value, is_mute=False):
        self.clip_tab.grade.set_fstop(value[Slider.FSTOP.value])
        self.clip_tab.grade.set_gamma(value[Slider.GAMMA.value])
        self.clip_tab.grade.set_blackpoint(value[Slider.BLACKPOINT.value])
        self.clip_tab.grade.set_whitepoint(value[Slider.WHITEPOINT.value])
        self.clip_tab.grade.set_lift(value[Slider.LIFT.value])
        self.clip_tab.grade.set_mute(is_mute)

    def set_frame_grade(self, value, is_mute=False):
        self.frame_tab.grade.set_fstop(value[Slider.FSTOP.value])
        self.frame_tab.grade.set_gamma(value[Slider.GAMMA.value])
        self.frame_tab.grade.set_blackpoint(value[Slider.BLACKPOINT.value])
        self.frame_tab.grade.set_whitepoint(value[Slider.WHITEPOINT.value])
        self.frame_tab.grade.set_lift(value[Slider.LIFT.value])
        self.frame_tab.grade.set_mute(is_mute)

    def set_region_grade(self, value, is_mute=False):
        self.current_tab.grade.set_fstop(value[Slider.FSTOP.value])
        self.current_tab.grade.set_gamma(value[Slider.GAMMA.value])
        self.current_tab.grade.set_blackpoint(value[Slider.BLACKPOINT.value])
        self.current_tab.grade.set_whitepoint(value[Slider.WHITEPOINT.value])
        self.current_tab.grade.set_lift(value[Slider.LIFT.value])
        self.current_tab.grade.set_mute(is_mute)
