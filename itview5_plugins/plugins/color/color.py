from PySide2 import QtCore, QtGui, QtWidgets
import PyOpenColorIO as OCIO
import color.resources.resources


class ChannelAction(QtWidgets.QAction):
    SIG_TRIGGERED = QtCore.Signal(str)
    def __init__(self, args, **kwargs):
        super().__init__(args, **kwargs)
        self.triggered.connect(self.emit_triggered)

    def emit_triggered(self, checked):
        self.SIG_TRIGGERED.emit(self.text())


class Color(QtCore.QObject):
    REVERT = "(Revert)"
    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window

        self.__color_api = self.__rpa.color_api
        self.__session_api = self.__rpa.session_api

        self.__create_channel_actions()
        self.__create_tool_bar()

        ocio_config = OCIO.GetCurrentConfig()
        self.__ocio_colorspaces = list(ocio_config.getColorSpaceNames())
        self.__ocio_colorspaces.insert(0, self.REVERT)
        self.__ocio_display_to_views = {}
        for display in ocio_config.getDisplays():
            self.__ocio_display_to_views[display] = list(ocio_config.getViews(display))

        self.__default_colorspace = None
        self.__default_display = ocio_config.getDefaultDisplay()
        self.__default_view = ocio_config.getDefaultView(self.__default_display)

        self.__populate_luts_in_menu()
        self.__rgb_channel_action.trigger()

        self.__session_api.SIG_CURRENT_CLIP_CHANGED.connect(
            self.__update_colorspace)
        self.__color_api.delegate_mngr.add_post_delegate(
            self.__color_api.set_channel, self.__channel_modified)

        self.__rgb_channel_action.setProperty("hotkey_editor", True)
        self.__red_channel_action.setProperty("hotkey_editor", True)
        self.__green_channel_action.setProperty("hotkey_editor", True)
        self.__blue_channel_action.setProperty("hotkey_editor", True)
        self.__alpha_channel_action.setProperty("hotkey_editor", True)
        self.__luminance_channel_action.setProperty("hotkey_editor", True)


    def __create_tool_bar(self):
        self.__tool_bar = QtWidgets.QToolBar()
        self.__tool_bar.setWindowTitle("Color Toolbar")
        self.__tool_bar.setObjectName(self.__tool_bar.windowTitle())
        reset_icon = QtGui.QIcon(QtGui.QPixmap(":reset.png"))

        self.__tool_bar.addWidget(QtWidgets.QLabel("Color Space:"))
        self.__ocio_colorspace_combo_box = QtWidgets.QComboBox()
        self.__ocio_colorspace_combo_box.currentIndexChanged.connect(self.__set_ocio_colorspace)

        self.__colorspace_reset_btn = QtWidgets.QPushButton(reset_icon, "")
        self.__colorspace_reset_btn.setFixedWidth(self.__colorspace_reset_btn.sizeHint().width())
        self.__colorspace_reset_btn.setToolTip("Reset colorspace")
        self.__colorspace_reset_btn.clicked.connect(self.__reset_colorspace)

        self.__tool_bar.addWidget(self.__ocio_colorspace_combo_box)
        self.__tool_bar.addWidget(self.__colorspace_reset_btn)

        self.__tool_bar.addSeparator()

        self.__tool_bar.addWidget(QtWidgets.QLabel("Display:"))
        self.__ocio_display_combo_box = QtWidgets.QComboBox()
        self.__ocio_display_combo_box.currentIndexChanged.connect(self.__set_ocio_display)
        self.__tool_bar.addWidget(self.__ocio_display_combo_box)

        self.__tool_bar.addSeparator()

        self.__tool_bar.addWidget(QtWidgets.QLabel("View:"))
        self.__ocio_view_combo_box = QtWidgets.QComboBox()
        self.__ocio_view_combo_box.currentIndexChanged.connect(self.__set_ocio_view)
        self.__color_api.delegate_mngr.add_post_delegate(
            self.__color_api.set_ocio_view, self.__update_ocio_view)
        self.__tool_bar.addWidget(self.__ocio_view_combo_box)

        self.__tool_bar.addSeparator()
        self.__tool_bar.addSeparator()

        self.__tool_bar.addWidget(QtWidgets.QLabel("Channel:"))
        self.__channel_select_button = QtWidgets.QToolButton(self.__tool_bar)
        self.__channel_select_button.setMinimumWidth(100)
        channel_select_menu = QtWidgets.QMenu(self.__tool_bar)
        for action in self.__channel_select_actions:
            channel_select_menu.addAction(action)
        self.__channel_select_button.setToolTip("Color channel view control")
        self.__channel_select_button.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.__channel_select_button.setMenu(channel_select_menu)
        self.__tool_bar.addWidget(self.__channel_select_button)

        self.__main_window.addToolBar(QtCore.Qt.TopToolBarArea, self.__tool_bar)

    def __update_ocio_view(self, out, view):
        try:
            self.__ocio_view_combo_box.blockSignals(True)
            self.__ocio_view_combo_box.setCurrentText(view)
        finally:
            self.__ocio_view_combo_box.blockSignals(False)

    def __set_ocio_colorspace(self):
        playlist_id = self.__session_api.get_fg_playlist()
        clip_id = self.__session_api.get_current_clip()
        if not clip_id: return
        colorspace = self.__ocio_colorspace_combo_box.currentText()
        if colorspace == self.REVERT:
            self.__reset_colorspace()
            return
        self.__color_api.set_ocio_colorspace(clip_id, colorspace)

    def __set_ocio_display(self):
        display = self.__ocio_display_combo_box.currentText()
        self.__populate_ocio_views(display)
        self.__color_api.set_ocio_display(display)

    def __set_ocio_view(self):
        view = self.__ocio_view_combo_box.currentText()
        self.__color_api.set_ocio_view(view)

    def __reset_colorspace(self):
        self.__ocio_colorspace_combo_box.setCurrentText(self.__default_colorspace)

    def __populate_luts_in_menu(self):
        self.__populate_ocio_colorspaces()
        # We also ensure to update views before we update display in RV
        # inorder to avoid DisplayTransformError which occurs when a view is set,
        # but the display selected doesn't have that particular view.
        self.__populate_ocio_views(self.__default_display)
        self.__populate_ocio_displays()

    def __populate_ocio_colorspaces(self):
        try:
            self.__ocio_colorspace_combo_box.blockSignals(True)
            self.__ocio_colorspace_combo_box.clear()
            self.__ocio_colorspace_combo_box.addItems(self.__ocio_colorspaces)
            self.__ocio_colorspace_combo_box.setCurrentIndex(0)
        finally:
            self.__ocio_colorspace_combo_box.blockSignals(False)

    def __populate_ocio_displays(self):
        try:
            self.__ocio_display_combo_box.blockSignals(True)
            self.__ocio_display_combo_box.clear()
            self.__ocio_display_combo_box.addItems(self.__ocio_display_to_views.keys())
            if self.__default_display not in self.__ocio_display_to_views.keys():
                self.__ocio_display_combo_box.addItem(self.__default_display)
            self.__ocio_display_combo_box.setCurrentText(self.__default_display)
        finally:
            self.__ocio_display_combo_box.blockSignals(False)

    def __populate_ocio_views(self, display):
        """ This will get called only when the display changes."""
        try:
            self.__ocio_view_combo_box.blockSignals(True)
            self.__ocio_view_combo_box.clear()
            all_views = self.__ocio_display_to_views.get(display, [])
            self.__ocio_view_combo_box.addItems(all_views)
            view = self.__color_api.get_ocio_view()
            if view == 'None' or view not in all_views:
                view = self.__default_view
                self.__color_api.set_ocio_view(view)
            self.__ocio_view_combo_box.setCurrentText(view)
        finally:
            self.__ocio_view_combo_box.blockSignals(False)

    def __update_colorspace(self, clip_id):
        if not clip_id: return
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        colorspace = self.__color_api.get_ocio_colorspace(clip_id)
        self.__default_colorspace = colorspace
        if colorspace not in self.__ocio_colorspaces:
            self.__ocio_colorspace_combo_box.addItem(colorspace)
        self.__ocio_colorspace_combo_box.setCurrentText(colorspace)

    def __update_display(self):
        display = self.__color_api.get_ocio_display()
        if display == self.__ocio_display_combo_box.currentText():
            return
        self.__populate_ocio_views(display)
        if display not in self.__ocio_display_to_views.keys():
            self.__ocio_display_combo_box.addItem(display)
        self.__ocio_display_combo_box.setCurrentText(display)

    def __update_luts(self):
        self.__update_colorspace()
        self.__update_display()

    def __create_channel_actions(self):
        self.__rgb_channel_action = ChannelAction("Color(RGB)")
        self.__rgb_channel_action.setCheckable(True)
        self.__rgb_channel_action.setShortcut(QtGui.QKeySequence("c"))
        self.__rgb_channel_action.SIG_TRIGGERED.connect(
            lambda name: self.__set_channel(name, 4))

        self.__red_channel_action = ChannelAction("Red")
        self.__red_channel_action.setCheckable(True)
        self.__red_channel_action.setShortcut(QtGui.QKeySequence("r"))
        self.__red_channel_action.SIG_TRIGGERED.connect(
            lambda name: self.__set_channel(name, 0))

        self.__green_channel_action = ChannelAction("Green")
        self.__green_channel_action.setCheckable(True)
        self.__green_channel_action.setShortcut(QtGui.QKeySequence("g"))
        self.__green_channel_action.SIG_TRIGGERED.connect(
            lambda name: self.__set_channel(name, 1))

        self.__blue_channel_action = ChannelAction("Blue")
        self.__blue_channel_action.setCheckable(True)
        self.__blue_channel_action.setShortcut(QtGui.QKeySequence("b"))
        self.__blue_channel_action.SIG_TRIGGERED.connect(
            lambda name: self.__set_channel(name, 2))

        self.__alpha_channel_action = ChannelAction("Alpha")
        self.__alpha_channel_action.setCheckable(True)
        self.__alpha_channel_action.setShortcut(QtGui.QKeySequence("a"))
        self.__alpha_channel_action.SIG_TRIGGERED.connect(
            lambda name: self.__set_channel(name, 3))

        self.__luminance_channel_action = ChannelAction("Luminance")
        self.__luminance_channel_action.setCheckable(True)
        self.__luminance_channel_action.setShortcut(QtGui.QKeySequence("l"))
        self.__luminance_channel_action.SIG_TRIGGERED.connect(
            lambda name: self.__set_channel(name, 5))

        self.__channel_select_actions = [
            self.__rgb_channel_action, self.__red_channel_action,
            self.__green_channel_action, self.__blue_channel_action,
            self.__alpha_channel_action, self.__luminance_channel_action]
        self.__channel_select_action_grp = QtWidgets.QActionGroup(self)
        self.__channel_select_action_grp.setExclusive(True)
        for action in self.__channel_select_actions:
            self.__channel_select_action_grp.addAction(action)

    def __set_channel(self, name, channel):
        current_channel = self.__color_api.get_channel()
        self.__channel_select_button.setText(name)
        if current_channel == channel:
            if channel != 4:
                self.__rgb_channel_action.trigger()
            return
        if channel == 0: #Red
            self.__color_api.set_channel(0)
        elif channel == 1: #Green
            self.__color_api.set_channel(1)
        elif channel == 2: #Blue
            self.__color_api.set_channel(2)
        elif channel == 3: #Alpha
            self.__color_api.set_channel(3)
        elif channel == 4: #Color(RGB)
            self.__color_api.set_channel(4)
        elif channel == 5: #Luminance
            self.__color_api.set_channel(5)

    def __channel_modified(self, out, channel):
        self.__channel_select_action_grp.blockSignals(True)
        if channel == 0: #Red
            self.__red_channel_action.setChecked(True)
            self.__channel_select_button.setText("Red")
        elif channel == 1: #Green
            self.__green_channel_action.setChecked(True)
            self.__channel_select_button.setText("Green")
        elif channel == 2: #Blue
            self.__blue_channel_action.setChecked(True)
            self.__channel_select_button.setText("Blue")
        elif channel == 3: #Alpha
            self.__alpha_channel_action.setChecked(True)
            self.__channel_select_button.setText("Alpha")
        elif channel == 4: #Color(RGB)
            self.__rgb_channel_action.setChecked(True)
            self.__channel_select_button.setText("Color(RGB)")
        elif channel == 5: #Luminance
            self.__luminance_channel_action.setChecked(True)
            self.__channel_select_button.setText("Luminance")
        self.__channel_select_action_grp.blockSignals(False)
