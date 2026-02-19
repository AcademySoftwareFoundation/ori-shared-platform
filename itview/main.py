#!/usr/bin/env python3

import os
import sys
import signal
import logging
from logging.handlers import RotatingFileHandler
import platform
import subprocess
from rpa.rpa import Rpa
from rpa.session_state.session import Session
from itview.skin.dbid_mapper import DbidMapper
from itview.skin.rpa_skin.rpa_skin import RpaSkin
from itview.skin.rpa_tx.rpa_tx import RpaTx
from itview.skin.viewport_user_input_tx import ViewportUserInputTx
from itview.skin.sub_progress_bar_tx.sub_progress_bar_tx \
    import SubProgressBarTx
from itview.skin.itview_palette import ItviewPalette
from itview.skin.main_window import MainWindow
from itview.skin.plugin_manager.controller import Controller as PluginManager
from itview import plugin_path_configs
from rpa.utils import default_connection_maker
from itview.rpc import Rpc, get_available_ports
from PySide2 import QtCore, QtGui, QtWidgets
import uuid


def create_config(main_window):
    config = QtCore.QSettings("imageworks.com", "itview_5", main_window)
    config.beginGroup("itview")
    return config

def create_logger():
    if platform.system() == 'Windows':
        log_dir = os.path.join(os.environ["APPDATA"], "itview")
    elif platform.system() == 'Linux':
        log_dir = os.path.join(os.environ["HOME"], ".itview")
    else:
        raise Exception("Unsupported platform!")

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_filepath = os.path.join(log_dir, "itview5.log")

    itview5_logger = logging.getLogger("Itview5")
    itview5_logger.setLevel(logging.DEBUG)
    if not itview5_logger.handlers:
        handler = RotatingFileHandler(
            log_filepath, mode="a", maxBytes= 10 * 1024 * 1024, backupCount=5)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(pathname)s %(funcName)s %(lineno)d:\n %(asctime)s %(levelname)s %(message)s\n",
            datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        itview5_logger.addHandler(handler)
        itview5_logger.propagate = False
    itview5_logger.info("[ITVIEW] Itview5 Logger Created")
    return itview5_logger


class Main(QtCore.QObject):
    def __init__(self):
        super().__init__()

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.__qApp = QtWidgets.QApplication(sys.argv)
        self.__qApp.setPalette(ItviewPalette())

        main_window = MainWindow()
        logger = create_logger()
        plugin_manager = \
            PluginManager(main_window, plugin_path_configs.get(), logger)

        os.environ["RPA_SESSION_ID"] = uuid.uuid4().hex
        for env_id_name in [
            "PLAYLIST_UUID_SEED", "CLIP_UUID_SEED",
            "CC_UUID_SEED", "HTML_OVERLAY_UUID_SEED"]:
            if os.environ.get(env_id_name) is None:
                os.environ[env_id_name] = uuid.uuid4().hex

        session = Session()

        command_line_args = sys.argv[1:]
        with_sub = False
        if "wo_sub" in command_line_args:
            os.environ["WO_SUB"] = "1"
        else:
            os.environ["WO_SUB"] = "0"
        with_sub = False if os.environ["WO_SUB"] == "1" else True

        skin__core, sub__core, main__sub = get_available_ports(3)

        # Core ++++++++++++++++++++++++++++++++++++++++
        os.environ["SKIN__CORE"] = str(skin__core)
        if with_sub:
            os.environ["SUB__CORE"] = str(sub__core)

        self.__core = Rpc(self, server_port=int(skin__core))
        env = os.environ.copy()
        env["RV_IN_ITVIEW"] = "1"
        env["LD_LIBRARY_PATH"] = ""

        rv_home = env["RV_HOME"]
        core = subprocess.Popen([f"{rv_home}/bin/rv", "-flags", "ModeManagerPreload=ocio_source_setup"], env=env)
        self.__core.start()
        self.__rpa_tx = RpaTx(self.__core)
        self.__viewport_user_input = ViewportUserInputTx(self.__core)
        # ++++++++++++++++++++++++++++++++++++++++

        # Sub ++++++++++++++++++++++++++++++++++++++++
        if with_sub:
            self.__sub = Rpc(self, server_port=int(main__sub))
            os.environ["MAIN__SUB"] = str(main__sub)
            sub = subprocess.Popen([sys.executable, env["SUB_EXE"]], env=os.environ.copy())
            self.__sub.start()
        # ++++++++++++++++++++++++++++++++++++++++

        rpa = Rpa(create_config(main_window), logger)
        rpa_skin = RpaSkin(self.__rpa_tx, session)

        dbid_mapper = DbidMapper()
        if with_sub:
            self.__sub_progress_bar_tx = SubProgressBarTx(self.__sub, rpa_skin)
        default_connection_maker.set_core_delegates_for_all_rpa(rpa, rpa_skin)

        main_window.set_config_api(rpa.config_api)
        main_window.set_core_view(self.__get_view())
        main_window.init()
        rpa.session_api.get_attrs_metadata()

        plugin_manager.init(rpa, dbid_mapper, self.__viewport_user_input)

        main_window.show()
        self.__show_window()
        main_window.read_settings()

        exit_value = self.__qApp.exec_()
        if with_sub:
            self.__sub.rfc.close()
        self.__core.stop()
        if with_sub:
            self.__sub.stop()
            sub.terminate()
        core.terminate()
        sys.exit(exit_value)

    @property
    def rpa_tx(self):
        return self.__rpa_tx

    def __get_view(self):
        if os.getenv("ITVIEW_RV_SEPARATE", False):
            return QtWidgets.QWidget()

        if platform.system() in ("Linux", "Windows"):
            window_id = self.__core.get_window_id()
            window = QtGui.QWindow.fromWinId(window_id)
            widget = QtWidgets.QWidget.createWindowContainer(window)
        else:
            widget = QtWidgets.QWidget()

        widget.installEventFilter(self)
        widget.setMinimumSize(640, 320)

        return widget

    def __show_window(self):
        if os.getenv("ITVIEW_RV_SEPARATE", False):
            return
        self.__core.show_window()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            # clear focus on central widget click
            focus_widget = QtWidgets.QApplication.focusWidget()
            if focus_widget is not None:
                focus_widget.clearFocus()
        return False


if __name__ == "__main__":
    Main()
