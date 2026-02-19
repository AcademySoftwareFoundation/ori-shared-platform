from PySide2 import QtCore, QtWidgets, QtGui
from itview.skin.widgets.itv_dock_widget import ItvDockWidget
from itview5_plugins.plugins.help_menu.about import AboutDialog
import os

USER_DOCUMENTATION = "https://sonyimageworks.atlassian.net/wiki/spaces/Dev/pages/1466302863/Itview5+-+Getting+Started+-+User+Guide"
RPA_DOCUMENTATION = "http://docs.spimageworks.com/projects/gitprod/itview5-plugins/rpa/docs/build/html/index.html"

class HelpMenu(QtCore.QObject):
    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__main_window = itview.main_window
        self.__toggle_rpa_interpretter_action = None
        self.__itview_version = os.getenv("SPK_PKG_itview5_VERSION", "Unable to detect version")
        self.__rpa_version = os.getenv("SPK_OPT_itview5.rpa", "Unable to detect version")
        self.__about_dialog = AboutDialog("Itview5", itview_version=self.__itview_version,
                                          rpa_version=self.__rpa_version, parent=self.__main_window)

        self.__user_documentation = QtWidgets.QAction("User Documentation")
        self.__user_documentation.triggered.connect(lambda: self.__open_link(USER_DOCUMENTATION))
        self.__rpa_documentation = QtWidgets.QAction("RPA Documentation")
        self.__rpa_documentation.triggered.connect(lambda: self.__open_link(RPA_DOCUMENTATION))
        self.__about = QtWidgets.QAction("About")
        self.__about.triggered.connect(self.__open_about_dialog)

        self.__create_menu()
        self.__main_window.SIG_INITIALIZED.connect(self.__post_init)

    def __create_menu(self):
        self.help_menu = self.__main_window.menuBar().addMenu("Help")
        self.help_menu.addAction(self.__user_documentation)
        self.help_menu.addAction(self.__rpa_documentation)
        self.help_menu.addAction(self.__about)

    def __open_link(self, link):
        url = QtCore.QUrl(link)
        QtGui.QDesktopServices.openUrl(url)

    def __post_init(self):
        dock = self.__main_window.findChild(ItvDockWidget, "Rpa Interpreter")
        if dock:
            self.__toggle_rpa_interpretter_action = dock.toggleViewAction()
            self.help_menu.addAction(self.__toggle_rpa_interpretter_action)

    def __open_about_dialog(self):
        self.__about_dialog.show()
