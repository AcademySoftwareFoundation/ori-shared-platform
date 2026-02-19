import atexit
import os
import signal
import subprocess
import time
from PySide2 import QtCore, QtGui, QtWidgets

MELD_PATH = "/net/soft_scratch/users/pjurkas/pub/meld/meld"
OLD_SNAPSHOT_PATH = "/tmp/itview5-session-tree-old.txt"
NEW_SNAPSHOT_PATH = "/tmp/itview5-session-tree-new.txt"
SKIN_SNAPSHOT_PATH = "/tmp/itview5-session-tree-skin.txt"
CORE_SNAPSHOT_PATH = "/tmp/itview5-session-tree-core.txt"


class SessionTreeViewer(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self.__process = None

        if os.path.exists(OLD_SNAPSHOT_PATH):
            os.remove(OLD_SNAPSHOT_PATH)
        if os.path.exists(NEW_SNAPSHOT_PATH):
            os.remove(NEW_SNAPSHOT_PATH)
        if os.path.exists(SKIN_SNAPSHOT_PATH):
            os.remove(SKIN_SNAPSHOT_PATH)
        if os.path.exists(CORE_SNAPSHOT_PATH):
            os.remove(CORE_SNAPSHOT_PATH)

    def itview_init(self, itview):
        self.__rpa = itview.rpa
        self.__dbid_mapper = itview.dbid_mapper
        self.__main_window = itview.main_window

        self.__session_api = self.__rpa.session_api

        self.__action = QtWidgets.QAction("Compare Session Tree Snapshots", self.__main_window)
        self.__action.setShortcut(QtGui.QKeySequence("F12"))
        self.__action.triggered.connect(self.__action_triggered)

        plugins_menu = self.__main_window.get_plugins_menu()
        plugins_menu.addAction(self.__action)

    def __start_meld(self):
        if self.__process is None or self.__process.poll() is not None:
            env = os.environ.copy()
            env["GTK_THEME"] = "Adwaita"
            if self.__is_multi_process:
                self.__process = subprocess.Popen([
                    MELD_PATH,
                    "-L", "SKIN",
                    SKIN_SNAPSHOT_PATH,
                    "-L", "CORE",
                    CORE_SNAPSHOT_PATH],
                    env=env)
                time.sleep(1)
                subprocess.Popen([
                    MELD_PATH,
                    "-n",
                    "-L", "OLD",
                    OLD_SNAPSHOT_PATH,
                    "-L", "NEW",
                    NEW_SNAPSHOT_PATH],
                    env=env)
            else:
                self.__process = subprocess.Popen([
                    MELD_PATH,
                    "-L", "OLD",
                    OLD_SNAPSHOT_PATH,
                    "-L", "NEW",
                    NEW_SNAPSHOT_PATH],
                    env=env)
            atexit.register(self.__stop_meld)

    def __stop_meld(self):
        if self.__process is not None and self.__process.poll() is None:
            self.__process.send_signal(signal.SIGINT)

    def __action_triggered(self):
        out = self.__session_api.get_session_str()
        try:
            skin_str, core_str = out
            self.__is_multi_process = True
        except:
            skin_str = out
            self.__is_multi_process = False

        if os.path.exists(NEW_SNAPSHOT_PATH):
            os.replace(NEW_SNAPSHOT_PATH, OLD_SNAPSHOT_PATH)
        else:
            with open(OLD_SNAPSHOT_PATH, "w") as file:
                file.write(skin_str)
        with open(NEW_SNAPSHOT_PATH, "w") as file:
            file.write(skin_str)

        if self.__is_multi_process:
            with open(SKIN_SNAPSHOT_PATH, "w") as file:
                file.write(skin_str)
            with open(CORE_SNAPSHOT_PATH, "w") as file:
                file.write(core_str)

        self.__start_meld()
