from PySide2 import QtCore
from rpa.widgets.image_controller.image_controller import ImageController as RpaImageController


class ImageController(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window
        self.__cmd_line_args = itview.cmd_line_args

        self.__image_controller = RpaImageController(self.__rpa, self.__main_window)

        self.__create_menu_bar()

        self.__image_controller.actions.fstop_up.setProperty("hotkey_editor", True)
        self.__image_controller.actions.fstop_down.setProperty("hotkey_editor", True)
        self.__image_controller.actions.fstop_reset.setProperty("hotkey_editor", True)
        self.__image_controller.actions.fstop_pgup.setProperty("hotkey_editor", True)
        self.__image_controller.actions.fstop_pgdown.setProperty("hotkey_editor", True)
        self.__image_controller.actions.gamma_up.setProperty("hotkey_editor", True)
        self.__image_controller.actions.gamma_down.setProperty("hotkey_editor", True)
        self.__image_controller.actions.gamma_reset.setProperty("hotkey_editor", True)
        self.__image_controller.actions.rotation_reset.setProperty("hotkey_editor", True)
        self.__image_controller.actions.rotate_90.setProperty("hotkey_editor", True)
        self.__image_controller.actions.rotate_180.setProperty("hotkey_editor", True)
        self.__image_controller.actions.rotate_270.setProperty("hotkey_editor", True)
        self.__image_controller.actions.rotate_up_10.setProperty("hotkey_editor", True)
        self.__image_controller.actions.rotate_down_10.setProperty("hotkey_editor", True)

        self.__main_window.SIG_INITIALIZED.connect(self.__post_init)

    def __create_menu_bar(self):
        plugins_menu = self.__main_window.get_plugins_menu()
        image_controls = plugins_menu.addMenu("Image")
        image_controls.setTearOffEnabled(True)

        # FStop
        fstop_menu = image_controls.addMenu("FStop")
        fstop_menu.addAction(self.__image_controller.actions.fstop_up)
        fstop_menu.addAction(self.__image_controller.actions.fstop_down)
        fstop_menu.addAction(self.__image_controller.actions.fstop_reset)
        fstop_menu.addAction(self.__image_controller.actions.fstop_pgup)
        fstop_menu.addAction(self.__image_controller.actions.fstop_pgdown)
        fstop_menu.addSeparator()
        fstop_menu.addAction(self.__image_controller.actions.fstop_slider)

        # Gamma
        gamma_menu = image_controls.addMenu("Gamma")
        gamma_menu.addAction(self.__image_controller.actions.gamma_up)
        gamma_menu.addAction(self.__image_controller.actions.gamma_down)
        gamma_menu.addAction(self.__image_controller.actions.gamma_reset)
        gamma_menu.addSeparator()
        gamma_menu.addAction(self.__image_controller.actions.gamma_slider)

        # Image rotation
        image_rot_menu = image_controls.addMenu("Image Rotation")
        image_rot_menu.addAction(self.__image_controller.actions.rotation_reset)
        image_rot_menu.addAction(self.__image_controller.actions.rotate_90)
        image_rot_menu.addAction(self.__image_controller.actions.rotate_180)
        image_rot_menu.addAction(self.__image_controller.actions.rotate_270)
        image_rot_menu.addSeparator()
        image_rot_menu.addAction(self.__image_controller.actions.rotate_up_10)
        image_rot_menu.addAction(self.__image_controller.actions.rotate_down_10)
        image_rot_menu.addSeparator()
        image_rot_menu.addAction(self.__image_controller.actions.rotation_slider)

    def __post_init(self):
        pass
        # if self.__cmd_line_args.rotate is not None:
        #     deg = float(self.__cmd_line_args.rotate[0])
        #     self.__image_controller.set_image_rot_value(deg)

    def add_cmd_line_args(self, parser):
        group = parser.add_argument_group("Image Controls")
        group.add_argument(
            '--rot', '--rotate',
            action='store',
            metavar='DEGREE',
            type=float,
            nargs=1,
            dest='rotate',
            help='Rotate images to DEGREE'
        )