from PySide2 import QtCore, QtWidgets, QtGui
import os
from itview.skin.widgets.itv_dock_widget import ItvDockWidget
from rpa.widgets.session_auto_saver.session_auto_saver import SessionAutoSaver as _SessionAutoSaver


class SessionAutoSaver(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__main_window = itview.main_window
        self.__cmd_line_args = itview.cmd_line_args

        auto_save_directory = \
            os.path.join(os.path.expanduser("~"), ".config", "imageworks.com")
        os.makedirs(auto_save_directory, exist_ok=True)
        # hide_checkbox = self.__cmd_line_args.no_session_autosave
        hide_checkbox = False
        self.__session_auto_saver = _SessionAutoSaver(
            self.__rpa, self.__main_window,
            auto_save_directory=auto_save_directory, include_feedback=True,
            hide_checkbox=hide_checkbox)

        dock_widget = ItvDockWidget("Session Auto Saver", self.__main_window)
        dock_widget.setWidget(self.__session_auto_saver)
        self.__main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock_widget)
        dock_widget.hide()

        self.__toggle_action = dock_widget.toggleViewAction()

        plugins_menu = self.__main_window.get_plugins_menu()
        plugins_menu.addAction(self.__toggle_action)

    def add_cmd_line_args(self, parser):
        group = parser.add_argument_group("Session Auto Saver")
        group.add_argument(
            '--na', '--noautosave',
            action='store_true',
            dest='no_session_autosave',
            help='Do not show autosave dialog')