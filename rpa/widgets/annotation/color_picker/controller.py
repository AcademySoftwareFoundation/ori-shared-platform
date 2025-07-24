"""
Controller for Color Picker
"""

try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore
from rpa.widgets.annotation.color_picker.model import Rgb


class ControllerSignals(QtCore.QObject):
    SIG_SET_CURRENT_COLOR = QtCore.Signal(object)
    SIG_EYE_DROPPER_ENABLED = QtCore.Signal(bool)
    SIG_EYE_DROPPER_SIZE_CHANGED = QtCore.Signal(int)
    SIG_CLOSE = QtCore.Signal()


class Controller(object):

    def __init__(self, model, view):
        self.__model = model
        self.__view = view
        self.signals = ControllerSignals()

        self.__view.set_eye_dropper_sample_sizes(
            self.__model.get_eye_dropper_sample_size_names()
        )

        self.__view.set_color_slider_delta(
            self.__model.get_color_delta()
        )

        self.SIG_EYE_DROPPER_ENABLED = self.signals.SIG_EYE_DROPPER_ENABLED
        self.SIG_EYE_DROPPER_SIZE_CHANGED = self.signals.SIG_EYE_DROPPER_SIZE_CHANGED
        self.SIG_SET_CURRENT_COLOR = self.signals.SIG_SET_CURRENT_COLOR
        self.SIG_CLOSE = self.signals.SIG_CLOSE

        self.SIG_EYE_DROPPER_ENABLED.connect(self.enable_eye_dropper)
        self.SIG_SET_CURRENT_COLOR.connect(self.set_current_color)

        self.__view.SIG_EYE_DROPPER_ENABLED.connect(self.SIG_EYE_DROPPER_ENABLED)
        self.__view.SIG_EYE_DROPPER_SIZE_NAME_CHANGED.connect(
            self.set_eye_dropper_sample_size_from_name
        )

        self.__view.SIG_RED_SLIDER_CHANGED.connect(self.set_current_red)
        self.__view.SIG_GREEN_SLIDER_CHANGED.connect(self.set_current_green)
        self.__view.SIG_BLUE_SLIDER_CHANGED.connect(self.set_current_blue)
        self.__view.SIG_TEMPERATURE_SLIDER_CHANGED.connect(self.set_current_temperature)
        self.__view.SIG_MAGENTA_SLIDER_CHANGED.connect(self.set_current_magenta)
        self.__view.SIG_INTENSITY_SLIDER_CHANGED.connect(self.set_current_intensity)
        self.__view.SIG_SATURATION_SLIDER_CHANGED.connect(self.set_current_saturation)

        self.__view.SIG_SET_CURRENT_COLOR.connect(self.set_current_color)
        self.__view.SIG_SET_CURRENT_COLOR.connect(self.SIG_SET_CURRENT_COLOR)
        self.__view.SIG_CLEAR_RECENT_COLORS.connect(self.clear_recent_colors)
        self.__view.SIG_CLEAR_CUSTOM_COLORS.connect(self.clear_custom_colors)
        self.__view.SIG_ADD_CUSTOM_COLOR.connect(self.add_custom_color)
        self.__view.SIG_SET_FAV_COLOR.connect(self.set_fav_color)
        self.__view.SIG_CLEAR_FAV_COLORS.connect(self.clear_fav_colors)

        self.__view.SIG_CLOSE.connect(self.SIG_CLOSE)

    def enable_eye_dropper(self, enable):
        """ Enables and disables the eye dropper.

        :param enable: True to enable, and False to disable
        :type enable: bool
        """
        self.__model.enable_eye_dropper(enable)
        self.__view.enable_eye_dropper(enable)

    def is_eye_dropper_enabled(self):
        """ Determine whether the eye dropper is enabled for picking a color.

        :return: True if eye dropper is on, False otherwise
        :rtype: bool
        """
        return self.__model.is_eye_dropper_enabled()

    def set_eye_dropper_sample_size(self, size):
        """ Set the eye dropper's sample size for picking a color.

        :param size: eye dropper sample size value
        :type size: int
        """
        self.__model.set_eye_dropper_sample_size(size)
        self.__view.set_eye_dropper_sample_size(self.__model.get_eye_dropper_sample_size_index())

    def get_eye_dropper_sample_size(self):
        """ Return the current eye dropper sample size.

        :return: current eye dropper sample size
        :rtype: int
        """
        return self.__model.get_eye_dropper_sample_size()

    def set_eye_dropper_sample_size_from_name(self, size_name):
        """ Set the eye dropper's sample size from name.

        :param size_name: name of the selected eye dropper sample size
        :type size_name: str
        """
        value = self.__model.get_eye_dropper_sample_size_from_name(size_name)
        self.__model.set_eye_dropper_sample_size(value)
        self.SIG_EYE_DROPPER_SIZE_CHANGED.emit(self.__model.get_eye_dropper_sample_size())
        self.__view.set_eye_dropper_sample_size(self.__model.get_eye_dropper_sample_size_index())

    def get_eye_dropper_sample_size_names(self):
        """ Return the names of eye dropper sample sizes.

        :return: list of eye dropper sample size names
        :rtype: list (str)
        """
        return self.__model.get_eye_dropper_sample_size_names()

    def set_current_color(self, rgb):
        """ Set the current color using RGB values.

        :param rgb: RGB values of a color
        :type rgb: model.Rgb
        """
        if not self.__model.set_current_color(rgb.get_copy()):
            return False
        self.__view.set_current_color(self.__model.get_current_color())
        return True

    def get_current_color(self):
        """ Return the current pen color.

        :return: RGB, TMI and Saturation values of a color
        :rtype: model.Color
        """
        return self.__model.get_current_color()

    def set_color_in_use(self):
        """ Set the current color to be the color in use for annotations,
            and add the color in use to recent colors palette.
        """
        color = self.__model.get_current_color()
        is_color_in_use_set = self.__model.set_color_in_use(
            Rgb(color.red, color.green, color.blue)
        )
        if is_color_in_use_set or \
        (not is_color_in_use_set and self.__model.is_recent_colors_empty()):
            self.__model.set_recent_color(Rgb(color.red, color.green, color.blue))
            self.__view.set_recent_colors(self.__model.get_recent_colors())

        return is_color_in_use_set

    def get_color_in_use(self):
        """ Return the current color in use for annotations.

        :return: RGB values of a color
        :rtype: model.Rgb
        """
        return self.__model.get_color_in_use()

    def set_recent_colors(self, colors):
        """ Set a list of colors to recent colors palette.

        :param colors: list of RGB values
        :type colors: list (model.Rgb)
        """
        if not self.__model.set_recent_colors(colors):
            return False
        self.__view.set_recent_colors(self.__model.get_recent_colors())
        return True

    def get_recent_colors(self, number=None):
        """ Return the list of recent colors.

        :param number: optional; number of recent colors to return;
                       if None, the total number of recent colors
        :type number: int
        :return: list of RGB values of recent colors
        :rtype: list (model.Rgb)
        """
        recent_colors = self.__model.get_recent_colors()
        total_number = len(recent_colors)
        return recent_colors[:total_number if number is None else number]

    def clear_recent_colors(self):
        """ Set all recent colors to WHITE color.
        """
        self.__model.clear_recent_colors()
        self.__view.set_recent_colors(self.__model.get_recent_colors())

    def is_recent_colors_empty(self):
        """Check if there are no recent-colors used by user.

        :return: True if there are no recent colors
        :rtype: bool
        """
        return self.__model.is_recent_colors_empty()

    def set_custom_colors(self, colors):
        """ Set a list of colors to custom colors palette.

        :param colors: list of RGB values
        :type colors: list (model.Rgb)
        """
        if not self.__model.set_custom_colors(colors):
            return False
        self.__view.set_custom_colors(self.__model.get_custom_colors())
        return True

    def add_custom_color(self):
        """ Add the current color to the custom colors palette.
        """
        color = self.__model.get_current_color()
        if not self.__model.add_custom_color(Rgb(color.red, color.green, color.blue)):
            return False
        self.__view.set_custom_colors(self.__model.get_custom_colors())
        return True

    def get_custom_colors(self, number=None):
        """ Return the list of custom colors.

        :param number: optional; number of custom colors to return;
                       if None, the total number of custom colors
        :type number: int
        :return: list of RGB values of custom colors
        :rtype: list (model.Rgb)
        """
        custom_colors = self.__model.get_custom_colors()
        total_number = len(custom_colors)
        return custom_colors[:total_number if number is None else number]

    def clear_custom_colors(self):
        """ Set all custom colors to WHITE color.
        """
        self.__model.clear_custom_colors()
        self.__view.set_custom_colors(self.__model.get_custom_colors())

    def set_fav_colors(self, rgb_list):
        """ Set a list of colors to custom colors palette.

        :param rgb_list: list of RGB values
        :type rgb_list: list (model.Rgb)
        """
        if not self.__model.set_fav_colors(rgb_list):
            return False
        self.__view.set_fav_colors(self.__model.get_fav_colors())
        return True

    def set_fav_color(self, index):
        """ Set the current color to be a favorite color at the specified index.

        :param index: position of the favorite color in custom colors palette
        :type index: int
        """
        current_color = self.__model.get_current_color()

        if not self.__model.set_fav_color(
            index,
            Rgb(
                current_color.red,
                current_color.green,
                current_color.blue
            )
        ): return False
        self.__view.set_fav_color(index, self.__model.get_fav_color(index))
        return True

    def set_fav_color_tool_tip(self, index, tool_tip):
        """ Set a tooltip for the favorite color at the specified index.

        :param index: position of the favorite color in custom colors palette
        :type index: int
        :param tool_tip: favorite color's tooltip (hotkey bindings)
        :type tool_tip: str
        """
        if not self.__model.set_fav_color_tool_tip(index, tool_tip):
            return
        self.__view.set_fav_color_tool_tip(index, tool_tip)

    def get_fav_color_tool_tip(self, index):
        """ Return the tooltip of favorite color at specified index.

        :param index: position of the favorite color in custom colors palette
        :type index: int
        :return: favorite color's tooltip (hotkey bindings)
        :rtype: str
        """
        return self.__model.get_fav_color_tool_tip(index)

    def get_fav_color_default_tool_tip(self):
        """ Return the default tooltip of any favorite colors.

        :return: default tooltip
        :rtype: str
        """
        return self.__model.get_fav_color_default_tool_tip()

    def get_fav_color(self, index):
        """ Return the favorite color at the specified index.

        :param index: position of the favorite color in custom colors palette
        :type index: int
        :return: RGB values of a favorite color
        :rtype: model.Rgb
        """
        return self.__model.get_fav_color(index)

    def get_fav_colors(self):
        """ Return the list of favorite colors.

        :return: list of RGB values of favorite colors
        :rtype: list (model.Rgb)
        """
        return self.__model.get_fav_colors()

    def clear_fav_colors(self):
        """ Set all favorite colors to WHITE color.
        """
        self.__model.clear_fav_colors()
        self.__view.clear_fav_colors(self.__model.get_fav_colors())

    def get_max_num_of_recent_colors(self):
        """ Return the maximum number of colors in recent colors palette.
        """
        return self.__model.get_max_num_of_recent_colors()

    def get_max_num_of_custom_colors(self):
        """ Return the maximum number of colors in custom colors palette.
        """
        return self.__model.get_max_num_of_custom_colors()

    def get_max_num_of_fav_colors(self):
        """ Return the maximum number of favorite colors in custom colors palette.
        """
        return self.__model.get_max_num_of_fav_colors()

    def set_current_red(self, value):
        """ Set the current Red to given value and set a new current color.
        """
        self.__model.set_current_red(value)
        self.__view.set_current_color(self.__model.get_current_color())

    def get_current_red(self):
        """ Return the current value of Red.

        :return: Red value of RGB model
        :rtype: float
        """
        return self.__model.get_current_red()

    def set_current_green(self, value):
        """ Set the current Green to given value and set a new current color.
        """
        self.__model.set_current_green(value)
        self.__view.set_current_color(self.__model.get_current_color())

    def get_current_green(self):
        """ Return the current value of Green.

        :return: Green value of RGB model
        :rtype: float
        """
        return self.__model.get_current_green()

    def set_current_blue(self, value):
        """ Set the current Blue to given value and set a new current color.
        """
        self.__model.set_current_blue(value)
        self.__view.set_current_color(self.__model.get_current_color())

    def get_current_blue(self):
        """ Return the current value of Blue.

        :return: Blue value of RGB model
        :rtype: float
        """
        return self.__model.get_current_blue()

    def set_current_temperature(self, value):
        """ Set the current Temperature to given value and set a new current color.
        """
        self.__model.set_current_temperature(value)
        self.__view.set_current_color(self.__model.get_current_color())

    def get_current_temperature(self):
        """ Return the current value of Temperature.

        :return: Temperature value of TMI model
        :rtype: float
        """
        return self.__model.get_current_temperature()

    def set_current_magenta(self, value):
        """ Set the current Magenta to given value and set a new current color.
        """
        self.__model.set_current_magenta(value)
        self.__view.set_current_color(self.__model.get_current_color())

    def get_current_magenta(self):
        """ Return the current value of Magenta.

        :return: Magenta value of TMI model
        :rtype: float
        """
        return self.__model.get_current_magenta()

    def set_current_intensity(self, value):
        """ Set the current Intensity to given value and set a new current color.
        """
        self.__model.set_current_intensity(value)
        self.__view.set_current_color(self.__model.get_current_color())

    def get_current_intensity(self):
        """ Return the current value of Intensity.

        :return: Intensity value of TMI model
        :rtype: float
        """
        return self.__model.get_current_intensity()

    def set_current_saturation(self, value):
        """ Set the current Saturation to given value and set a new current color.
        """
        self.__model.set_current_saturation(value)
        self.__view.set_current_color(self.__model.get_current_color())

    def get_current_saturation(self):
        """ Return the current value of Saturation.

        :return: Saturation value of the current color
        :rtype: float
        """
        return self.__model.get_current_saturation()

    def get_latest_recent_color(self):
        """ Return the first color on the recent color palette.

        :return: RGB values of a color
        :rtype: model.Rgb
        """
        return self.__model.get_latest_recent_color()

    def get_color_delta(self):
        """ Return the step interval for setting values in color sliders.

        :return: step interval value for color sliders
        :rtype: int
        """
        return self.__model.get_color_delta()

    def show(self):
        """ Show the Color Picker window and set the starting pen color to be
            the latest recent color.
        """
        self.__view.show()
        self.__view.set_starting_color(self.__model.get_latest_recent_color())
