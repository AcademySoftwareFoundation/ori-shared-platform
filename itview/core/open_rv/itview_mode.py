import os
import sys
import signal
import uuid
import logging
from logging.handlers import RotatingFileHandler
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)

from itview.rpc import Rpc
import platform
try:
    from PySide2 import QtCore, QtGui, QtWidgets
except:
    from PySide6 import QtCore, QtGui, QtWidgets
from rv import rvtypes
from itview.skin.dbid_mapper import DbidMapper
from itview import plugin_path_configs
from itview.skin.plugin_manager.controller import Controller as PluginManager
from itview.skin.main_window import MainWindow
from rpa.rpa import Rpa
from itview.skin.rpa_skin.rpa_skin import RpaSkin
from itview.skin.itview_palette import ItviewPalette
from itview.core.rpa_rx.rpa_rx import RpaRx
from itview.core.viewport_user_input_rx import ViewportUserInputRx
from itview.core.sub_progress_bar_tx.sub_progress_bar_tx \
    import SubProgressBarTx
from rpa.utils import default_connection_maker
from rv import commands
import rv.qtutils


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
    itview5_logger.info("[SPI_ITVIEW] Itview5 Logger Created")
    return itview5_logger


class ContainerWidget(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setLayout(QtWidgets.QStackedLayout())


class ItviewMode(QtCore.QObject, rvtypes.MinorMode):

    def __init__(self):
        print("Itview Mode 1")

        QtCore.QObject.__init__(self)
        rvtypes.MinorMode.__init__(self)

        # M - Start ++++++++++++++++++++++++++++++++++++++++++++++++

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        # self.__qApp = QtWidgets.QApplication(sys.argv)
        # self.__qApp.setPalette(ItviewPalette())

        self.__main_window = MainWindow()
        logger = create_logger()

        self.__plugin_manager = \
            PluginManager(self.__main_window, plugin_path_configs.get(), logger)

        os.environ["RPA_SESSION_ID"] = uuid.uuid4().hex
        for env_id_name in [
            "PLAYLIST_UUID_SEED", "CLIP_UUID_SEED",
            "CC_UUID_SEED", "HTML_OVERLAY_UUID_SEED"]:
            if os.environ.get(env_id_name) is None:
                os.environ[env_id_name] = uuid.uuid4().hex

        command_line_args = sys.argv[1:]
        with_sub = False
        if "wo_sub" in command_line_args:
            os.environ["WO_SUB"] = "1"
        else:
            os.environ["WO_SUB"] = "0"
        with_sub = False if os.environ["WO_SUB"] == "1" else True

        # skin__core, sub__core, main__sub = get_available_ports(3)

        # # Core ++++++++++++++++++++++++++++++++++++++++
        # os.environ["SKIN__CORE"] = str(skin__core)
        # if with_sub:
        #     os.environ["SUB__CORE"] = str(sub__core)
        # self.__core = Rpc(self, server_port=int(skin__core))

        env = os.environ.copy()
        env["RV_IN_ITVIEW"] = "1"
        env["LD_LIBRARY_PATH"] = ""

        rv_home = env["RV_HOME"]

        print("Itview Mode 2")

        # M - End ++++++++++++++++++++++++++++++++++++++++++++++++

        # RV - START ++++++++++++++++++++++++++++++++++++++++++++++++

        print("Itview Mode 3")

        self.__gl_window_container = None

        # if not os.getenv("RV_IN_ITVIEW", False):
        #     return

        # self.__skin = Rpc(
        #     self, port=int(os.getenv("SKIN__CORE")), use_rpc=True)
        # self.__skin.start()

        app = QtWidgets.QApplication.instance()
        self.__rpa_core = app.rpa_core

        # self.__rpa_rx = RpaRx(self.__skin, self.__rpa_core)
        self.__viewport_user_input_rx = ViewportUserInputRx()

        # self.__with_sub = False if os.environ["WO_SUB"] == "1" else True
        # if self.__with_sub:
        #     self.__sub = Rpc(self, server_port=int(os.getenv("SUB__CORE")))
        #     self.__sub.start()
        #     self.__sub_progress_bar_tx = \
        #         SubProgressBarTx(self.__sub, self.__rpa_core)

        if platform.system() in ("Linux", "Windows") \
        and not os.getenv("ITVIEW_RV_SEPARATE", False):
            app = QtWidgets.QApplication.instance()
            app.installEventFilter(self)

        self.init("ItviewMode", [], None)

        print("Itview Mode 4")

        # RV - END ++++++++++++++++++++++++++++++++++++++++++++++++

        # M - START ++++++++++++++++++++++++++++++++++++++++++++++++

        self.__rpa = Rpa(create_config(self.__main_window), logger)
        # rpa_skin = RpaSkin(self.__rpa_tx, session)

        self.__dbid_mapper = DbidMapper()
        # rpa_core_spi = RpaCoreSpi(self.__rpa_core, self.__dbid_mapper)
        # rpa_spi = RpaSpi(self.__rpa_tx, session, self.__dbid_mapper)
        # rpa_spi.session_api._set_timeline_api(rpa_skin.timeline_api)
        # # if with_sub:
        # #     self.__sub_progress_bar_tx = SubProgressBarTx(self.__sub, rpa_spi)

        # OPEN
        default_connection_maker.set_core_delegates_for_all_rpa(
            self.__rpa, self.__rpa_core)

        # SPI
        # default_connection_maker.set_core_delegates_for_all_rpa(
        #     self.__rpa, self.__rpa_core, exclude=[self.__rpa.session_api])
        # default_connection_maker.set_core_delegates(
        #     self.__rpa.session_api, rpa_core_spi.session_api)

        rv_main_window = rv.qtutils.sessionWindow()
        self.__viewport_widget_1 = rv_main_window.findChild(
            QtWidgets.QWidget, "no session")

        self._init_main_window()

    def _init_main_window(self):
        print("_init_main_window")
        self.__main_window.set_config_api(self.__rpa.config_api)
        self.__main_window.set_logger_api(self.__rpa.logger_api)
        self.__main_window.set_core_view(self.__get_view())
        self.__main_window.init()
        self.__rpa.session_api.get_attrs_metadata()

        # self.__plugin_manager.init(self.__rpa, self.__dbid_mapper, self.__viewport_user_input)
        self.__plugin_manager.init(self.__rpa, self.__dbid_mapper, self.__viewport_user_input_rx)

        self.__main_window.show()
        self.show_window()
        self.__main_window.read_settings()

        commands.unbind("default", "global", 'pointer-2--drag')
        commands.unbind("default", "global", 'pointer-3--push')

        commands.unbind("default", "global", 'key-down--control--S')
        commands.unbind("default", "global", 'key-down--control--s')

        commands.unbind("default", "global", 'key-down--control--o')

        commands.unbind("default", "global", 'mode-manager-toggle-mode')
        commands.unbind("default", "global", 'session-manager-load-ui')
        commands.unbind("default", "global", 'key-down--x')

        commands.unbind("default", "global", 'toggle-draw-panel')
        commands.unbind("default", "global", 'key-down--f10')

        commands.unbind("default", "global", 'key-down--~')
        commands.unbind("default", "global", 'key-down--f2')

        commands.unbind("default", "global", 'key-down--shift--c')

        # exit_value = self.__qApp.exec_()
        # if with_sub:
        #     self.__sub.rfc.close()
        # self.__core.stop()
        # # if with_sub:
        # #     self.__sub.stop()
        # #     sub.terminate()
        # core.terminate()
        # sys.exit(exit_value)


    @property
    def rpa_rx(self):
        return self.__rpa_rx

    @property
    def viewport_user_input_rx(self):
        return self.__viewport_user_input_rx

    def __get_view(self):
        return self.__viewport_widget_1
        # if os.getenv("ITVIEW_RV_SEPARATE", False):
        #     return QtWidgets.QWidget()

        if platform.system() in ("Linux", "Windows"):
            window_id = self.get_window_id()
            window = QtGui.QWindow.fromWinId(window_id)
            widget = QtWidgets.QWidget.createWindowContainer(window)
            print("+++++++++++++=")
            print("Widget with View")
            print("+++++++++++++=")
        else:
            widget = QtWidgets.QWidget()

        widget.installEventFilter(self)
        widget.setMinimumSize(640, 320)

        print("Core View", widget, type(widget))
        return widget

    def close(self):
        self.__main.stop()
        if self.__with_sub:
            self.__sub.stop()

    def eventFilter(self, o, e):
        return
        if isinstance(e, QtGui.QShowEvent):
            if isinstance(o, QtWidgets.QWidget) and o.isWindow() and o.isVisible():
                # if o.property("SHOW_IN_ITVIEW_MODE"):
                #     return False
                # if o.objectName() == "RvPreferences":
                #     o.raise_()
                #     o.activateWindow()
                #     return False
                # if isinstance(o.parent(), QtWidgets.QComboBox):
                #     return False

                # window = o.windowHandle()
                # window.setFlag(QtCore.Qt.WindowTransparentForInput)
                # window.setFlag(QtCore.Qt.FramelessWindowHint)
                if isinstance(o, QtWidgets.QMainWindow):

                    if self.__gl_window_container is None:
                        app = QtWidgets.QApplication.instance()
                        if app is not None:
                            app.setQuitOnLastWindowClosed(False)

                        viewport_widget = \
                            o.findChild(QtWidgets.QWidget, "no session")
                        self.__viewport_user_input_rx.set_viewport_widget(
                            viewport_widget)
                        self.__rpa_core.viewport_api._set_viewport_widget(viewport_widget)
                        parent = viewport_widget.parent()
                        parent.layout().removeWidget(viewport_widget)

                        self.__gl_window_container = ContainerWidget()
                        self.__gl_window_container.layout().addWidget(
                            viewport_widget)
                        self.__gl_window_container.hide()

                        self.__main_window_container = ContainerWidget()
                        self.__main_window_container.layout().addWidget(o)
                        self.__main_window_container.hide()
                        self._init_main_window()

                # elif isinstance(o, ContainerWidget):
                #     pass
                # elif isinstance(o, QtWidgets.QDockWidget):
                #     o.setFloating(False)
                # else:
                #     QtCore.QMetaObject.invokeMethod(o, "close" , QtCore.Qt.QueuedConnection)
        return False

    def get_window_id(self):
        return self.__gl_window_container.winId()

    def show_window(self):
        self.__gl_window_container.show()


def createMode():
    return ItviewMode()
