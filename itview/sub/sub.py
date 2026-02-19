#!/usr/bin/env python3

import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    sys.path.remove(script_dir)
itview_python_path = os.environ.get("ITVIEW_DIR")
if itview_python_path is None:
    raise Exception("ITVIEW_DIR is not set")
sys.path.insert(0, itview_python_path)

from PySide2 import QtWidgets, QtCore
import signal
from itview.skin.itview_palette import ItviewPalette
from itview.sub.progress_bar_rx import ProgressBarRx
from itview.rpc import Rpc


class Sub:
    def __init__(self):

        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.__qApp = QtWidgets.QApplication(sys.argv)
        self.__qApp.setPalette(ItviewPalette())
        self.__qApp.setQuitOnLastWindowClosed(False)

        main_sub_port = os.environ.get("MAIN__SUB")
        if main_sub_port is not None:
            self.__main = \
                Rpc(self, port=int(main_sub_port), use_rpc=True)
            self.__main.start()

        self.__core = \
            Rpc(self, port=int(os.environ["SUB__CORE"]), use_rpc=True)
        self.__core.start()

        main_window = QtWidgets.QMainWindow()
        self.__progress_bar_rx = ProgressBarRx(main_window)

        exit_value = self.__qApp.exec_()
        self.__main.stop()
        self.__core.stop()
        sys.exit(exit_value)

    @property
    def progress_bar_rx(self):
        return self.__progress_bar_rx

    def close(self):
        self.__core.close()
        self.__qApp.quit()


if __name__ == "__main__":
    Sub()
