import rpa.widgets.tablet_helper.resources.resources
from rpa.utils import utils

# PySide import fallback: Try PySide2 first, then PySide6
try:
    # PySide2 (Qt5): QAction, QPushButton, QSlider, QWidgetAction are in QtWidgets
    from PySide2.QtCore import Qt, QSize, QTimer, Signal, Slot
    from PySide2.QtGui import QColor, QIcon, QPalette
    from PySide2.QtWidgets import (
        QAction, QMenu, QPushButton, QSlider, QToolBar, QToolButton, QWidgetAction
    )
    PYSIDE_VERSION = 2
except:
    try:
        # PySide6 (Qt6): QAction moved to QtGui, QPushButton, QSlider, QWidgetAction still in QtWidgets
        from PySide6.QtCore import Qt, QSize, QTimer, Signal, Slot
        from PySide6.QtGui import QAction, QColor, QIcon, QPalette
        from PySide6.QtWidgets import (
            QMenu, QPushButton, QSlider, QToolBar, QToolButton, QWidgetAction
        )
        PYSIDE_VERSION = 6
    except:
        raise ImportError(
            "Neither PySide2 nor PySide6 is available. "
            "Please install one of them."
        )


# Constants
# Default values for sliders
DEFAULT_CONTRAST_MAX = 80
DEFAULT_CONTRAST_MIN = 0

SHOW_COLOR_PICKER = "show_color_picker"
INTERACTIVE_MODE = "interactive_mode"
INTERACTIVE_MODE_PEN = "pen"
INTERACTIVE_MODE_HARD_ERASER = "hard_eraser"
ENABLE_EYE_DROPPER = "enable_eye_dropper"
PICKED_COLOR = "picked_color"
PEN_WIDTH = "pen_width"
ERASER_WIDTH = "eraser_width"
IS_INTERACTIVE_MODE = "is_interactive_mode"
TOGGLE_MASK = "toggle_mask"
TOGGLE_FRAME_OVERLAY = "toggle_frame_overlay"
TOGGLE_TEXT_OVERLAY = "toggle_text_overlay"
TOGGLE_PHOTO_PLUGIN = "toggle_photo_plugin"

# Toggle color for active buttons
TOGGLE_ON_COLOR = (0.63, 0.63, 0.63)
ANNOTATION_TOOL_SIZES = [1, 2, 4, 6, 8, 12, 16, 20, 30, 40, 50, 75, 100, 125, 150, 200, 250, 300]
ANNOTATION_TOOL_SIZE_INDEX = {value:index for index, value in enumerate(ANNOTATION_TOOL_SIZES)}
DEFAULT_PEN_WIDTH_INDEX = 5
DEFAULT_ERASER_WIDTH_INDEX = 5
DEFAULT_MAX_PEN_WIDTH = len(ANNOTATION_TOOL_SIZES)
DEFAULT_MAX_ERASER_WIDTH = DEFAULT_MAX_PEN_WIDTH


def _load_icon(icon_filename):
    """
    Load an icon from Qt resources.

    Since the resources module is imported, icons are accessed directly
    from the compiled Qt resource system using the :icon_filename format.

    Args:
        icon_filename: Name of the icon file (e.g., "applications-graphics.png")

    Returns:
        QIcon: The loaded icon from Qt resources
    """
    # Load from Qt resources using the : prefix format
    # The resources module must be imported for this to work
    resource_path = f":{icon_filename}"
    icon = QIcon(resource_path)

    # Warn if icon is not found (should not happen if resources are properly compiled)
    if icon.isNull() or not icon.availableSizes():
        print(f"[TabletHelper] WARNING: Icon not found in resources: {icon_filename}")

    return icon


class SliderWidgetAction(QWidgetAction):
    """
    Custom widget action that creates a slider widget.

    This class wraps a QSlider in a QWidgetAction to be used in menus
    and toolbars.
    """

    def __init__(self, parent, orientation=Qt.Vertical,
                 minimum=None, maximum=None, tick_interval=None,
                 single_step=None, maximum_width=None):
        """
        Initialize the slider widget action.

        Args:
            parent: Parent widget
            orientation: Slider orientation (Qt.Vertical or Qt.Horizontal)
            minimum: Minimum slider value
            maximum: Maximum slider value
            tick_interval: Interval between tick marks
            single_step: Single step increment
            maximum_width: Maximum width of the slider
        """
        super().__init__(parent)

        self._orientation = orientation
        self._minimum = minimum
        self._maximum = maximum
        self._tick_interval = tick_interval
        self._single_step = single_step
        self._maximum_width = maximum_width

    def createWidget(self, parent):
        """
        Create the slider widget.

        Args:
            parent: Parent widget for the slider

        Returns:
            QSlider: Configured slider widget
        """
        slider = QSlider(self._orientation, parent)
        if self._minimum is not None:
            slider.setMinimum(self._minimum)
        if self._maximum is not None:
            slider.setMaximum(self._maximum)
        if self._tick_interval is not None:
            slider.setTickInterval(self._tick_interval)
        if self._single_step is not None:
            slider.setSingleStep(self._single_step)
        if self._maximum_width is not None:
            slider.setMaximumWidth(self._maximum_width)
        return slider

    def getCreatedWidget(self):
        """
        Get the created slider widget.

        Returns:
            QSlider: The slider widget instance

        Raises:
            AssertionError: If no widget or multiple widgets exist
        """
        widgets = self.createdWidgets()
        assert widgets, "No widgets created"
        assert len(widgets) == 1, "Multiple widgets created"
        return widgets[0]


class TabletHelper(QToolBar):
    photo_plugin_toggled = Signal(bool)
    all_overlays_toggled = Signal(bool)

    def __init__(self, rpa, parent=None):
        super().__init__("Tablet Helper", parent)
        self.setObjectName("TabletHelper")

        self.__rpa = rpa
        self._orient_horizontal = False
        self._default_color = None
        self._mode_actions = []
        self._current_mode_action = None  # Track currently active mode action

        # Slider widgets
        self._pen_width_slider = None
        self._eraser_width_slider = None
        self._contrast_slider = None

        # Slider widget actions (needed to access widgets when menus are shown)
        self._pen_width_swa = None
        self._erase_width_swa = None
        self._contrast_swa = None

        # Actions
        self.color_action = None
        self.clear_anno_action = None
        self.undo_anno_action = None
        self.redo_anno_action = None
        self.mute_action = None
        self.next_clip_action = None
        self.prev_clip_action = None
        self.next_anno_action = None
        self.prev_anno_action = None
        # self.dim_action = None
        # self.audio_wf_action = None
        self.color_swatch_action = None
        self.photo_action = None
        self.frame_action = None
        self.text_action = None
        self.overlay_action = None
        self.scrub_action = None
        self.mask_action = None
        self.pen_action = None
        self.eraser_action = None
        self.color_pick_action = None
        self.orient_action = None
        # self.contrast_action = None
        self.pen_size_action = None
        self.eraser_size_action = None
        self.colorIter = 0
        self.annotationColor = [
            (1.0, 1.0, 1.0),
            (1.0, 0.0, 0.0),
            (0.9, 0.5, 0.0),
            (0.3, 1.0, 0.9)
        ]
        self.defaultAnnoColor = self.annotationColor[0]

        self._init_actions()
        self._init_toolbar()

        self.__rpa.timeline_api.delegate_mngr.add_post_delegate(
            self.__rpa.timeline_api.set_mute, self.__post_set_mute)
        self.__rpa.timeline_api.delegate_mngr.add_post_delegate(
            self.__rpa.timeline_api.enable_audio_scrubbing,
            self.__post_enable_audio_scrubbing)

        self.__rpa.session_api.delegate_mngr.add_post_delegate(
            self.__rpa.session_api.set_custom_session_attr,
            self.__post_set_custom_session_attr)

    def __post_set_custom_session_attr(self, out, attr_id, value):
        if attr_id == PICKED_COLOR:
            self.__update_color_action_bg(value)
        elif attr_id == PEN_WIDTH:
            self.__update_pen_width(value)
        elif attr_id == ERASER_WIDTH:
            self.__update_eraser_width(value)
        elif attr_id == TOGGLE_MASK:
            self.mask_action.setProperty("is_pressed", value)
            self._set_action_selected_visual(self.mask_action, value)
        elif attr_id == TOGGLE_FRAME_OVERLAY:
            self.frame_action.setProperty("is_pressed", value)
            self._set_action_selected_visual(self.frame_action, value)
        elif attr_id == TOGGLE_TEXT_OVERLAY:
            self.text_action.setProperty("is_pressed", value)
            self._set_action_selected_visual(self.text_action, value)
        elif attr_id == TOGGLE_PHOTO_PLUGIN:
            self.photo_action.setProperty("is_pressed", value)
            self._set_action_selected_visual(self.photo_action, value)
        elif attr_id == INTERACTIVE_MODE:
            if value == INTERACTIVE_MODE_PEN:
                self._set_action_selected_visual(self.eraser_action, False)
                self._set_action_selected_visual(self.pen_action, True)
            if value == INTERACTIVE_MODE_HARD_ERASER:
                self._set_action_selected_visual(self.eraser_action, True)
                self._set_action_selected_visual(self.pen_action, False)

    def _init_actions(self):
        """Initialize all toolbar actions with icons and tooltips."""
        # Color and annotation actions
        self.color_action = QAction(
            _load_icon("applications-graphics.png"),
            "Cycle Annotation Color",
            self
        )
        self.clear_anno_action = QAction(
            _load_icon("edit-clear.png"),
            "Clear Annotations",
            self
        )
        self.undo_anno_action = QAction(
            _load_icon("edit-undo.png"),
            "Undo Annotation",
            self
        )
        self.redo_anno_action = QAction(
            _load_icon("edit-redo.png"),
            "Redo Annotation",
            self
        )

        # Playback actions
        if self.__rpa.timeline_api.is_mute():
            mute_icon_name = "audio-volume-muted.png"
        else: mute_icon_name = "audio-volume-high.png"
        self.mute_action = QAction(
            _load_icon(mute_icon_name),
            "Mute Audio",
            self
        )
        self.next_clip_action = QAction(
            _load_icon("go-next.png"),
            "Next Clip",
            self
        )
        self.prev_clip_action = QAction(
            _load_icon("go-previous.png"),
            "Previous Clip",
            self
        )

        # Annotation navigation
        self.next_anno_action = QAction(
            _load_icon("arrow-right-double.png"),
            "Next Annotation",
            self
        )
        self.prev_anno_action = QAction(
            _load_icon("arrow-left-double.png"),
            "Previous Annotation",
            self
        )

        # Display and tool actions
        # self.dim_action = QAction(
        #     _load_icon("help-hint.png"),
        #     "Dim Lights",
        #     self
        # )
        # self.audio_wf_action = QAction(
        #     _load_icon("applications-multimedia.png"),
        #     "Audio Waveforms",
        #     self
        # )
        self.color_swatch_action = QAction(
            _load_icon("fill-color.png"),
            "Color Swatch",
            self
        )
        self.photo_action = QAction(
            _load_icon("preferences-desktop-user.png"),
            "Photo Plugin",
            self
        )
        self.photo_action.setProperty("is_pressed", False)
        self.frame_action = QAction(
            _load_icon("frame-overlay.png"),
            "Display frame overlay",
            self
        )
        self.frame_action.setProperty("is_pressed", False)
        self.text_action = QAction(
            _load_icon("text-overlay.png"),
            "Display text overlay",
            self
        )
        self.text_action.setProperty("is_pressed", False)
        self.overlay_action = QAction(
            _load_icon("all-overlay.png"),
            "Display all overlays",
            self
        )
        self.overlay_action.setProperty("is_pressed", False)
        self.scrub_action = QAction(
            _load_icon("applications-media-scrub.png"),
            "Play audio while scrubbing",
            self
        )
        self.mask_action = QAction(
            _load_icon("insert-image.png"),
            "Toggle Mask",
            self
        )
        self.mask_action.setProperty("is_pressed", False)

        # Drawing tools
        self.pen_action = QAction(
            _load_icon("draw-freehand.png"),
            "Pen Tool",
            self
        )
        self.pen_action.setProperty(IS_INTERACTIVE_MODE, False)
        self.eraser_action = QAction(
            _load_icon("draw-eraser.png"),
            "Eraser Tool",
            self
        )
        self.eraser_action.setProperty(IS_INTERACTIVE_MODE, False)
        self.color_pick_action = QAction(
            _load_icon("color-picker.png"),
            "Color Picker",
            self
        )

        # Toolbar control
        self.orient_action = QAction(
            _load_icon("orient-horizontal.png"),
            "Change Toolbar Orientation",
            self
        )

        # Create slider widgets
        self._create_pen_size_slider()
        self._create_eraser_slider()
        self._create_contrast_slider()

        # Connect actions to placeholder slots
        self.color_action.triggered.connect(self._on_cycle_color)
        self.clear_anno_action.triggered.connect(self._on_clear_annotations)
        self.undo_anno_action.triggered.connect(self._on_undo_annotation)
        self.redo_anno_action.triggered.connect(self._on_redo_annotation)
        self.mute_action.triggered.connect(self._on_mute_audio)
        self.next_clip_action.triggered.connect(self._on_next_clip)
        self.prev_clip_action.triggered.connect(self._on_prev_clip)
        self.next_anno_action.triggered.connect(self._on_next_annotation)
        self.prev_anno_action.triggered.connect(self._on_prev_annotation)
        # self.dim_action.triggered.connect(self._on_dim_lights)
        # self.audio_wf_action.triggered.connect(self._on_audio_waveform)
        self.color_swatch_action.triggered.connect(self._on_color_swatch)
        self.photo_action.triggered.connect(self._on_photo_plugin)
        self.frame_action.triggered.connect(self._on_frame_overlay)
        self.text_action.triggered.connect(self._on_text_overlay)
        self.overlay_action.triggered.connect(self._on_all_overlays)
        self.scrub_action.triggered.connect(self._on_audio_scrub)
        self.mask_action.triggered.connect(self._on_toggle_mask)
        self.pen_action.triggered.connect(self._on_pen_select)
        self.eraser_action.triggered.connect(self._on_eraser_select)
        self.color_pick_action.triggered.connect(self._on_color_picker)
        self.orient_action.triggered.connect(self._on_orientation_change)

        # Track mode actions for visual feedback
        self._mode_actions.extend([self.pen_action, self.eraser_action])

    def _init_toolbar(self):
        """Initialize the toolbar with all actions."""
        # Add actions to toolbar in order
        self.addAction(self.orient_action)
        # self.addAction(self.dim_action)
        # self.addWidget(self.contrast_action)
        self.addAction(self.color_action)
        self.addAction(self.color_pick_action)
        self.addAction(self.color_swatch_action)
        self.addAction(self.pen_action)
        self.addWidget(self.pen_size_action)
        self.addAction(self.eraser_action)
        self.addWidget(self.eraser_size_action)
        self.addAction(self.clear_anno_action)
        self.addAction(self.undo_anno_action)
        self.addAction(self.redo_anno_action)
        self.addAction(self.prev_anno_action)
        self.addAction(self.next_anno_action)
        self.addAction(self.prev_clip_action)
        self.addAction(self.next_clip_action)
        self.addAction(self.mute_action)
        self.addAction(self.scrub_action)
        self.addAction(self.mask_action)
        # self.addAction(self.audio_wf_action)
        self.addAction(self.photo_action)
        self.addAction(self.frame_action)
        self.addAction(self.text_action)
        self.addAction(self.overlay_action)

        # Set toolbar window flags
        self.setWindowFlags(
            Qt.Tool | Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint | Qt.X11BypassWindowManagerHint
        )
        # Ensure toolbar is movable - this enables the native drag handle
        # For floating toolbars, Qt automatically shows a handle area at the start
        self.setMovable(True)

        # Set auto-fill background for toggle buttons
        toggle_actions = [
            self.photo_action, self.scrub_action, self.mask_action,
            self.text_action, self.color_action,
            self.pen_action, self.eraser_action, self.frame_action
        ]
        for action in toggle_actions:
            widget = self.widgetForAction(action)
            if widget:
                widget.setAutoFillBackground(True)

        # Match reference toolbar icon size for compact appearance
        self.setIconSize(QSize(24, 24))

        # Reduce toolbar spacing for more compact layout (match reference)
        layout = self.layout()
        if layout:
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)

        # Set tool button style to show icons only for all actions
        for action in self.actions():
            widget = self.widgetForAction(action)
            if widget and isinstance(widget, QToolButton):
                widget.setToolButtonStyle(Qt.ToolButtonIconOnly)
                widget.setFocusPolicy(Qt.NoFocus)
                # Reduce button padding for more compact appearance
                widget.setStyleSheet("QToolButton { padding: 2px; }")

        # Get default background color
        frame_widget = self.widgetForAction(self.frame_action)
        if frame_widget:
            palette = frame_widget.palette().color(frame_widget.backgroundRole())
            self._default_color = (
                palette.red() / 255.0,
                palette.green() / 255.0,
                palette.blue() / 255.0
            )

        # Initialize orientation state to match actual toolbar orientation
        self._orient_horizontal = (self.orientation() == Qt.Horizontal)
        self._update_orientation_icon()

    def _create_pen_size_slider(self):
        """Create the pen size slider widget."""
        pen_size_menu = QMenu('')
        self._pen_width_swa = SliderWidgetAction(
            pen_size_menu,
            orientation=Qt.Vertical,
            minimum=1,
            maximum=DEFAULT_MAX_PEN_WIDTH,
            maximum_width=20
        )
        pen_size_menu.addAction(self._pen_width_swa)

        # Connect to menu's aboutToShow signal to get slider widget when it's created
        def _on_pen_menu_about_to_show():
            # Use QTimer to ensure widget is created after menu is shown
            def _get_slider_widget():
                if self._pen_width_slider is None:
                    widgets = self._pen_width_swa.createdWidgets()
                    if widgets:
                        self._pen_width_slider = widgets[0]
                        # Set default value to DEFAULT_PEN_WIDTH_INDEX
                        self._pen_width_slider.setValue(DEFAULT_PEN_WIDTH_INDEX)
                        self._pen_width_slider.valueChanged.connect(self._on_pen_width_changed)
                        pen_size_menu.setMinimumWidth(self._pen_width_slider.width() + 6)
                        # Update icon based on default slider value (without selecting tool)
                        icon_index = self._calculate_icon_index(DEFAULT_PEN_WIDTH_INDEX, DEFAULT_MAX_PEN_WIDTH)
                        icon_path = f"brush_{icon_index}.png"
                        self.pen_size_action.setIcon(_load_icon(icon_path))

            QTimer.singleShot(0, _get_slider_widget)

        pen_size_menu.aboutToShow.connect(_on_pen_menu_about_to_show)

        # Calculate default icon index for width 30
        default_icon_index = self._calculate_icon_index(DEFAULT_PEN_WIDTH_INDEX, DEFAULT_MAX_PEN_WIDTH)
        default_icon_path = f"brush_{default_icon_index}.png"

        self.pen_size_action = QToolButton(self)
        self.pen_size_action.setToolTip("Pen Size")
        self.pen_size_action.setMenu(pen_size_menu)
        self.pen_size_action.setPopupMode(QToolButton.InstantPopup)
        self.pen_size_action.setIcon(_load_icon(default_icon_path))
        self.pen_size_action.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.pen_size_action.setFocusPolicy(Qt.NoFocus)

    def _create_eraser_slider(self):
        """Create the eraser size slider widget."""
        eraser_size_menu = QMenu('')
        self._erase_width_swa = SliderWidgetAction(
            eraser_size_menu,
            orientation=Qt.Vertical,
            minimum=1,
            maximum=DEFAULT_MAX_ERASER_WIDTH,
            maximum_width=20
        )
        eraser_size_menu.addAction(self._erase_width_swa)

        # Connect to menu's aboutToShow signal to get slider widget when it's created
        def _on_eraser_menu_about_to_show():
            # Use QTimer to ensure widget is created after menu is shown
            def _get_slider_widget():
                if self._eraser_width_slider is None:
                    widgets = self._erase_width_swa.createdWidgets()
                    if widgets:
                        self._eraser_width_slider = widgets[0]
                        # Set default value to DEFAULT_ERASER_WIDTH_INDEX
                        self._eraser_width_slider.setValue(DEFAULT_ERASER_WIDTH_INDEX)
                        self._eraser_width_slider.valueChanged.connect(
                            self._on_eraser_width_changed
                        )
                        eraser_size_menu.setMinimumWidth(
                            self._eraser_width_slider.width() + 6
                        )
                        # Update icon based on default slider value (without selecting tool)
                        icon_index = self._calculate_icon_index(DEFAULT_ERASER_WIDTH_INDEX, DEFAULT_MAX_ERASER_WIDTH)
                        icon_path = f"eraser_{icon_index}.png"
                        self.eraser_size_action.setIcon(_load_icon(icon_path))

            QTimer.singleShot(0, _get_slider_widget)

        eraser_size_menu.aboutToShow.connect(_on_eraser_menu_about_to_show)

        # Calculate default icon index for width 30
        default_icon_index = self._calculate_icon_index(DEFAULT_ERASER_WIDTH_INDEX, DEFAULT_MAX_ERASER_WIDTH)
        default_icon_path = f"eraser_{default_icon_index}.png"

        self.eraser_size_action = QToolButton(self)
        self.eraser_size_action.setToolTip("Eraser Size")
        self.eraser_size_action.setMenu(eraser_size_menu)
        self.eraser_size_action.setPopupMode(QToolButton.InstantPopup)
        self.eraser_size_action.setIcon(_load_icon(default_icon_path))
        self.eraser_size_action.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.eraser_size_action.setFocusPolicy(Qt.NoFocus)

    def _create_contrast_slider(self):
        """Create the contrast slider widget."""
        contrast_menu = QMenu('')
        self._contrast_swa = SliderWidgetAction(
            contrast_menu,
            orientation=Qt.Vertical,
            minimum=DEFAULT_CONTRAST_MIN,
            maximum=DEFAULT_CONTRAST_MAX,
            maximum_width=20
        )
        contrast_menu.addAction(self._contrast_swa)

        # Connect to menu's aboutToShow signal to get slider widget when it's created
        def _on_contrast_menu_about_to_show():
            # Use QTimer to ensure widget is created after menu is shown
            def _get_slider_widget():
                if self._contrast_slider is None:
                    widgets = self._contrast_swa.createdWidgets()
                    if widgets:
                        self._contrast_slider = widgets[0]
                        self._contrast_slider.valueChanged.connect(self._on_contrast_changed)
                        contrast_menu.setMinimumWidth(self._contrast_slider.width() + 6)

            QTimer.singleShot(0, _get_slider_widget)

        contrast_menu.aboutToShow.connect(_on_contrast_menu_about_to_show)

        # self.contrast_action = QToolButton(self)
        # self.contrast_action.setToolTip("Contrast (Not Available)")
        # self.contrast_action.setMenu(contrast_menu)
        # self.contrast_action.setPopupMode(QToolButton.InstantPopup)
        # self.contrast_action.setIcon(_load_icon("contrast.png"))
        # self.contrast_action.setToolButtonStyle(Qt.ToolButtonIconOnly)
        # self.contrast_action.setFocusPolicy(Qt.NoFocus)
        # self.contrast_action.setEnabled(False)

    def set_visible(self, visible):
        """
        Set the visibility of the toolbar.

        Args:
            visible: True to show the toolbar, False to hide it
        """
        if visible:
            self.show()
        else:
            self.hide()

    def set_orientation(self, orientation):
        """
        Set the toolbar orientation.

        Args:
            orientation: Qt.Horizontal or Qt.Vertical
        """
        self.hide()
        self.setOrientation(orientation)
        self._orient_horizontal = (orientation == Qt.Horizontal)
        self._update_orientation_icon()
        self.show()

    def _update_orientation_icon(self):
        """Update the orientation icon based on current orientation."""
        if not self.orient_action:
            return

        if self.orientation() == Qt.Horizontal:
            self.orient_action.setIcon(
                _load_icon("orient-vertical.png")
            )
        else:
            self.orient_action.setIcon(
                _load_icon("orient-horizontal.png")
            )

    def _set_action_selected_visual(self, current_action, is_set):
        """
        Update visual feedback for mode actions.


        Uses stylesheets to ensure background color is visible in all states
        (normal, hover, pressed) and not just on hover.


        Args:
            current_action: The currently active action, or None
        """
        widget = self.widgetForAction(current_action)
        if is_set:
            # Use TOGGLE_ON_COLOR for selected action
            r, g, b = [int(x * 255) for x in TOGGLE_ON_COLOR]
            # Set background color for all states to ensure visibility
            stylesheet = (
                "QToolButton { "
                f"background-color: rgb({r}, {g}, {b}); "
                "padding: 2px; "
                "}"
                "QToolButton:hover { "
                f"background-color: rgb({r}, {g}, {b}); "
                "}"
                "QToolButton:pressed { "
                f"background-color: rgb({r}, {g}, {b}); "
                "}"
            )
            current_action.setProperty(IS_INTERACTIVE_MODE, True)
        else:
            # Use default color for unselected actions
            r, g, b = [int(x * 255) for x in self._default_color]
            # Set background color for all states
            stylesheet = (
                "QToolButton { "
                f"background-color: rgb({r}, {g}, {b}); "
                "padding: 2px; "
                "}"
                "QToolButton:hover { "
                f"background-color: rgb({r}, {g}, {b}); "
                "}"
                "QToolButton:pressed { "
                f"background-color: rgb({r}, {g}, {b}); "
                "}"
            )
            current_action.setProperty("is_interactive_mode", False)
        widget.setStyleSheet(stylesheet)

    def _calculate_icon_index(self, width, max_width):
        """
        Calculate icon index from width value.

        Args:
            width: Current width value
            max_width: Maximum width value

        Returns:
            int: Icon index (0-9)
        """
        # Calculate index: (width-1)/(max_width/10)
        # This maps width values to icon indices 0-9
        index = int((width - 1) / (max_width / 10))
        # Clamp to valid range
        return max(0, min(9, index))

    def __update_color_action_bg(self, color):
        color_widget = self.widgetForAction(self.color_action)
        r, g, b = [int(x * 255) for x in color[:-1]]
        stylesheet = (
            "QToolButton { "
            f"background-color: rgb({r}, {g}, {b}); "
            "padding: 2px; "
            "}"
            "QToolButton:hover { "
            f"background-color: rgb({r}, {g}, {b}); "
            "}"
            "QToolButton:pressed { "
            f"background-color: rgb({r}, {g}, {b}); "
            "}"
        )
        color_widget.setStyleSheet(stylesheet)

    @Slot()
    def _on_cycle_color(self):
        self.colorIter += 1
        if self.colorIter == len(self.annotationColor):
            self.colorIter = 0
        color = self.annotationColor[self.colorIter]

        self.__rpa.session_api.set_custom_session_attr(
            PICKED_COLOR, (*color, 1.0))

    @Slot()
    def _on_clear_annotations(self):
        utils.clear_current_frame_annotations(self.__rpa)

    @Slot()
    def _on_undo_annotation(self):
        utils.undo_annotations(self.__rpa)

    @Slot()
    def _on_redo_annotation(self):
        utils.redo_annotations(self.__rpa)

    @Slot()
    def _on_mute_audio(self):
        self.__rpa.timeline_api.set_mute(
            not self.__rpa.timeline_api.is_mute())

    @Slot()
    def _on_next_clip(self):
        utils.goto_next_clip(self.__rpa)

    @Slot()
    def _on_prev_clip(self):
        utils.goto_prev_clip(self.__rpa)

    @Slot()
    def _on_next_annotation(self):
        utils.goto_nearest_feedback_frame(self.__rpa, True)

    @Slot()
    def _on_prev_annotation(self):
        utils.goto_nearest_feedback_frame(self.__rpa, False)

    # @Slot()
    # def _on_dim_lights(self):
    #     """Placeholder slot for dim lights action."""
    #     print("[TabletHelper] DEBUG: Dim Lights action triggered")
    #     # Toggle state would be managed by external logic
    #     self.lights_dimmed.emit(True)

    # @Slot()
    # def _on_audio_waveform(self):
    #     """Placeholder slot for audio waveform action."""
    #     print("[TabletHelper] DEBUG: Audio Waveform action triggered")
    #     # Toggle state would be managed by external logic
    #     self.audio_waveform_toggled.emit(True)

    @Slot()
    def _on_color_swatch(self):
        self.__rpa.session_api.set_custom_session_attr(
            SHOW_COLOR_PICKER, True)

    @Slot()
    def _on_photo_plugin(self):
        self.__rpa.session_api.set_custom_session_attr(
            TOGGLE_PHOTO_PLUGIN,
            not self.photo_action.property("is_pressed"))

    @Slot()
    def _on_frame_overlay(self):
        self.overlay_action.setProperty("is_pressed", False)
        self._set_action_selected_visual(self.overlay_action, False)
        self.__rpa.session_api.set_custom_session_attr(
            TOGGLE_FRAME_OVERLAY,
            not self.frame_action.property("is_pressed"))

    @Slot()
    def _on_text_overlay(self):
        self.overlay_action.setProperty("is_pressed", False)
        self._set_action_selected_visual(self.overlay_action, False)
        self.__rpa.session_api.set_custom_session_attr(
            TOGGLE_TEXT_OVERLAY,
            not self.text_action.property("is_pressed"))

    @Slot()
    def _on_all_overlays(self):
        state = not self.overlay_action.property("is_pressed")
        self.overlay_action.setProperty("is_pressed", state)
        self._set_action_selected_visual(self.overlay_action, state)
        self.__rpa.session_api.set_custom_session_attr(
            TOGGLE_FRAME_OVERLAY, state)
        self.__rpa.session_api.set_custom_session_attr(
            TOGGLE_TEXT_OVERLAY, state)

    @Slot()
    def _on_audio_scrub(self):
        self.__rpa.timeline_api.enable_audio_scrubbing(
            not self.__rpa.timeline_api.is_audio_scrubbing_enabled())
        if self.__rpa.timeline_api.is_audio_scrubbing_enabled():
            self._set_action_selected_visual(self.scrub_action, True)
        else:
            self._set_action_selected_visual(self.scrub_action, False)

    @Slot()
    def _on_toggle_mask(self):
        self.__rpa.session_api.set_custom_session_attr(
            TOGGLE_MASK, not self.mask_action.property("is_pressed"))

    @Slot()
    def _on_pen_select(self):
        self._set_action_selected_visual(self.eraser_action, False)
        interactive_mode = self.__rpa.session_api.get_custom_session_attr(
            INTERACTIVE_MODE)
        if interactive_mode == INTERACTIVE_MODE_PEN:
            new_interactive_mode = None
            self._set_action_selected_visual(self.pen_action, False)
        else:
            new_interactive_mode = INTERACTIVE_MODE_PEN
            self._set_action_selected_visual(self.pen_action, True)
        self.__rpa.session_api.set_custom_session_attr(
            INTERACTIVE_MODE, new_interactive_mode)

    @Slot()
    def _on_eraser_select(self):
        self._set_action_selected_visual(self.pen_action, False)
        interactive_mode = self.__rpa.session_api.get_custom_session_attr(
            INTERACTIVE_MODE)
        if interactive_mode == INTERACTIVE_MODE_HARD_ERASER:
            new_interactive_mode = None
            self._set_action_selected_visual(self.eraser_action, False)
        else:
            new_interactive_mode = INTERACTIVE_MODE_HARD_ERASER
            self._set_action_selected_visual(self.eraser_action, True)
        self.__rpa.session_api.set_custom_session_attr(
            INTERACTIVE_MODE, new_interactive_mode)

    @Slot()
    def _on_color_picker(self):
        self.__rpa.session_api.set_custom_session_attr(ENABLE_EYE_DROPPER, True)

    @Slot()
    def _on_orientation_change(self):
        # Get the actual current orientation from the toolbar
        current_orientation = self.orientation()
        # Toggle to the opposite orientation
        new_orientation = Qt.Vertical if (current_orientation == Qt.Horizontal) else Qt.Horizontal
        orientation_str = "Horizontal" if (new_orientation == Qt.Horizontal) else "Vertical"
        self.set_orientation(new_orientation)

    def __update_pen_width(self, width):
        width_index = ANNOTATION_TOOL_SIZE_INDEX.get(width)
        if width_index is None: return
        if self._pen_width_slider and self._pen_width_slider.value() != width_index:
            self._pen_width_slider.blockSignals(True)
            self._pen_width_slider.setValue(width_index)
            self._pen_width_slider.blockSignals(False)

        # Calculate icon index and update icon
        icon_index = self._calculate_icon_index(width_index, DEFAULT_MAX_PEN_WIDTH)
        icon_path = f"brush_{icon_index}.png"
        self.pen_size_action.setIcon(_load_icon(icon_path))

    def __update_eraser_width(self, width):
        width_index = ANNOTATION_TOOL_SIZE_INDEX.get(width)
        if width_index is None: return
        if self._eraser_width_slider and self._eraser_width_slider.value() != width_index:
            self._eraser_width_slider.blockSignals(True)
            self._eraser_width_slider.setValue(width_index)
            self._eraser_width_slider.blockSignals(False)

        # Calculate icon index and update icon
        icon_index = self._calculate_icon_index(width_index, DEFAULT_MAX_ERASER_WIDTH)
        icon_path = f"brush_{icon_index}.png"
        self.eraser_size_action.setIcon(_load_icon(icon_path))

    @Slot(int)
    def _on_pen_width_changed(self, width):
        # Automatically select pen tool when size changes
        if self.pen_action.property(IS_INTERACTIVE_MODE) == False:
            self._on_pen_select()
        width = ANNOTATION_TOOL_SIZES[width - 1]
        self.__rpa.session_api.set_custom_session_attr(PEN_WIDTH, width)

    @Slot(int)
    def _on_eraser_width_changed(self, width):
        # Automatically select pen tool when size changes
        if self.eraser_action.property(IS_INTERACTIVE_MODE) == False:
            self._on_eraser_select()
        width = ANNOTATION_TOOL_SIZES[width - 1]
        self.__rpa.session_api.set_custom_session_attr(ERASER_WIDTH, width)

    # @Slot(int)
    # def _on_contrast_changed(self, value):
    #     contrast_value = value / 100.0
    #     print(f"[TabletHelper] DEBUG: Contrast changed to {contrast_value:.2f} (raw value: {value})")
    #     self.contrast_changed.emit(contrast_value)

    def __post_set_mute(self, out, state):
        if state:
            icon_name = "audio-volume-muted.png"
        else:
            icon_name = "audio-volume-high.png"
        self.mute_action.setIcon(_load_icon(icon_name))

    def __post_enable_audio_scrubbing(self, out, state):
        self._set_action_selected_visual(
            self.scrub_action,
            self.__rpa.timeline_api.is_audio_scrubbing_enabled())
