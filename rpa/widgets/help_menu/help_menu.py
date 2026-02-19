from PySide2 import QtCore, QtWidgets, QtGui
from rpa.widgets.help_menu.about import AboutDialog
import os

class HelpMenu(QtWidgets.QMenu):
    def __init__(self, rpa, main_window):
        super().__init__("Help", main_window)
        self.__main_window = main_window
        # self.__rpa_version = os.getenv("SPK_OPT_itview5.rpa", "Unable to detect version")
        self.__rpa_version = "1.0"
        self.__about_dialog = AboutDialog("RPA",
                                          rpa_version=self.__rpa_version,
                                          parent=self.__main_window)

        self.__documentation = QtWidgets.QAction("Documentation")
        self.__documentation.triggered.connect(self.__open_documentation)
        self.__about = QtWidgets.QAction("About")
        self.__about.triggered.connect(self.__open_about_dialog)
        self.addAction(self.__documentation)
        self.addAction(self.__about)

    def __open_documentation(self):
        url = QtCore.QUrl("https://ori-shared-platform.readthedocs.io/en/latest/")
        QtGui.QDesktopServices.openUrl(url)

    def __open_about_dialog(self):
        self.__about_dialog.show()
