from PySide2 import QtCore
from rpa.widgets.annotation.annotation import Annotation as RpaAnnotation
import rpa.widgets.annotation.constants as C


class Annotation(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window
        self.__cmd_line_args = itview.cmd_line_args

        self.__annotation = RpaAnnotation(self.__rpa, self.__main_window)
        self.__create_menu_bar()

        self.__annotation.actions.show_annotations.setProperty("hotkey_editor", True)
        self.__annotation.actions.next_annot_frame.setProperty("hotkey_editor", True)
        self.__annotation.actions.prev_annot_frame.setProperty("hotkey_editor", True)
        self.__annotation.actions.undo.setProperty("hotkey_editor", True)
        self.__annotation.actions.redo.setProperty("hotkey_editor", True)
        self.__annotation.actions.clear_frame.setProperty("hotkey_editor", True)

        self.__core_view = self.__main_window.get_core_view()
        self.__core_view.installEventFilter(self)

        self.__main_window.SIG_INITIALIZED.connect(self.__post_init)

    def __create_menu_bar(self):
        plugins_menu = self.__main_window.get_plugins_menu()

        annotations_menu = None
        for action in plugins_menu.actions():
            submenu = action.menu()
            if submenu and submenu.title() == "Annotations":
                annotations_menu = submenu
                break
        if not annotations_menu:
            annotations_menu = plugins_menu.addMenu("Annotations")

        annotations_menu.addAction(self.__annotation.actions.clear_frame)
        annotations_menu.addAction(self.__annotation.actions.undo)
        annotations_menu.addAction(self.__annotation.actions.redo)

    def eventFilter(self, obj, event):
        if not (
        event.type() == QtCore.QEvent.MouseButtonPress or \
        event.type() == QtCore.QEvent.MouseMove or \
        event.type() == QtCore.QEvent.MouseButtonRelease):
            return False

        interactive_mode = None
        if event.modifiers() == QtCore.Qt.NoModifier:
            interactive_mode = self.__rpa.session_api.get_custom_session_attr(
                C.INTERACTIVE_MODE)
        if event.modifiers() == QtCore.Qt.ControlModifier:
            interactive_mode = C.INTERACTIVE_MODE_PEN
        if event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier:
            interactive_mode = C.INTERACTIVE_MODE_HARD_ERASER
        if event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier:
            interactive_mode = C.INTERACTIVE_MODE_LINE
        if event.modifiers() == QtCore.Qt.ControlModifier | QtCore.Qt.MetaModifier:
            interactive_mode = C.INTERACTIVE_MODE_MULTI_LINE

        self.__rpa.session_api.set_custom_session_attr(
            C.MODIFIER_INTERACTIVE_MODE, interactive_mode)

        return False

    def __post_init(self):
        pass
        # if self.__cmd_line_args.pencolor is not None:
        #     pen_color = self.__cmd_line_args.pencolor
        #     pen_color = tuple(map(lambda x: max(0.0, min(1.0, x)), pen_color))
        #     self.__annotation.set_pen_color(pen_color)

    def add_cmd_line_args(self, parser):
        group = parser.add_argument_group("Annotations")
        group.add_argument(
            '--pc', '--pencolor',
            action='store',
            type=float,
            nargs=3,
            metavar=('RED', 'GREEN', 'BLUE'),
            dest='pencolor',
            help='Specify annotation pen color as RGB of [0.0 - 1.0]'
        )
