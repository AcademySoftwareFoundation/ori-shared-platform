from PySide2 import QtCore, QtWidgets
from itview.skin.widgets.itv_dock_widget import ItvDockWidget
from rpa.widgets.sub_widgets.nonhide_menu import NonHideQMenu


class CetralWidget(QtWidgets.QScrollArea):

    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setWidgetResizable(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.setMinimumSize(100, 100)
        self.setMaximumSize(1e6, 1e6)

    def setWidget(self, widget):
        widget.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        widget.setMinimumSize(100, 100)
        widget.setMaximumSize(1e6, 1e6)
        super().setWidget(widget)

class MainWindow(QtWidgets.QMainWindow):
    SIG_INITIALIZED = QtCore.Signal()
    SIG_CLOSED = QtCore.Signal()
    SIG_CLOSED_FOR_RESTART = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setDockOptions(
            MainWindow.AnimatedDocks | MainWindow.AllowTabbedDocks | \
            MainWindow.AllowNestedDocks)
        self.setTabPosition(QtCore.Qt.AllDockWidgetAreas, QtWidgets.QTabWidget.North)

        self.__is_closing_for_restart = False

        self.__central_widget = CetralWidget()
        self.setCentralWidget(self.__central_widget)

        self.__fullscreen_widget = CetralWidget()

        self.setStyleSheet("""
            QMainWindow::separator {
                background: palette(window);
                width: 4px;
                height: 4px;
            }
            QMainWindow::separator:hover {
                background: #0073C2;
            }
        """)

        self.__can_close_handlers = []
        self.__are_actions_added_to_core_view = False
        self.__config_api = None
        self.__logger_api = None

    def add_can_close_handler(self, can_close):
        self.__can_close_handlers.append(can_close)

    def set_config_api(self, config_api):
        self.__config_api = config_api

    def set_logger_api(self, logger_api):
        self.__logger_api = logger_api

    def init(self):
        self.update_title(None)
        self.SIG_CLOSED.connect(
            lambda:self.save_main_window_config())

        menu_bar = self.menuBar()
        self.__file_menu = menu_bar.addMenu("File")
        self.__session_menu = menu_bar.addMenu("Session")
        self.__plugins_menu = menu_bar.addMenu("Plugins")

        for menu in menu_bar.findChildren(QtWidgets.QMenu):
            if menu.title() == self.__plugins_menu.title():
                menu.aboutToShow.connect(
                    lambda menu=menu: self.__sort_menu_actions(menu))

        self.__status_bar = self.statusBar()
        self.__status_bar.showMessage("Welcome to Itview5")

    def __sort_menu_actions(self, menu):
        actions = menu.actions()
        sorted_actions = sorted(actions, key=lambda action: action.text())
        sorted_actions = [a for a in sorted_actions if a.text() != "Plugins Manager"]

        for action in actions:
            if action.text() == "Plugins Manager":
                continue
            menu.removeAction(action)

        menu.addSeparator()

        for action in sorted_actions:
            menu.addAction(action)

    def save_main_window_config(self):
        self.__config_api.setValue("window/geometry", self.saveGeometry())
        self.__config_api.setValue("window/state", self.saveState())

    def set_core_view(self, core_view):

        self.__central_widget.setWidget(core_view)

    def get_core_view(self):
        return self.__central_widget.widget()

    def get_file_menu(self):
        return self.__file_menu

    def get_session_menu(self):
        return self.__session_menu

    def get_plugins_menu(self):
        return self.__plugins_menu

    def get_status_bar(self):
        return self.__status_bar

    def set_closing_for_restart(self, is_closing_for_restart:bool):
        self.__is_closing_for_restart = is_closing_for_restart

    def closeEvent(self, event):
        for can_close in self.__can_close_handlers:
            if not can_close():
                event.ignore()
                return
        super().closeEvent(event)
        if self.__is_closing_for_restart:
            self.SIG_CLOSED_FOR_RESTART.emit()
        else:
            self.SIG_CLOSED.emit()

    def read_settings(self):
        geometry = self.__config_api.value("window/geometry")
        if geometry is None:
            self.resize(960, 540)
        self.restoreGeometry(geometry)
        state = self.__config_api.value("window/state")
        self.restoreState(state)

        self.SIG_INITIALIZED.emit()

    def update_title(self, title):
        if not title:
            title = "Nothing loaded"
        self.setWindowTitle("Itview5 - %s" % (title))

    def toggle_fullscreen(self):
        if self.__fullscreen_widget.isFullScreen():
            core_view = self.__fullscreen_widget.takeWidget()
            self.__central_widget.setWidget(core_view)
            self.__fullscreen_widget.hide()
        else:
            core_view = self.__central_widget.takeWidget()
            self.__fullscreen_widget.setWidget(core_view)
            self.__fullscreen_widget.showFullScreen()

            if not self.__are_actions_added_to_core_view:
                actions = self.collect_all_actions()
                for action in actions:
                    core_view.addAction(action)
                    self.__are_actions_added_to_core_view = True

    def createPopupMenu(self):
        new_menu = NonHideQMenu(self)
        menu = QtWidgets.QMainWindow.createPopupMenu(self)
        if menu:
            docks = []
            toolbars = []
            sorted_actions = \
                sorted(menu.actions(), key=lambda action: action.text())

            for action in sorted_actions:
                w = action.parentWidget()
                if isinstance(w, QtWidgets.QDockWidget):
                    docks.append(action)
                elif isinstance(w, QtWidgets.QToolBar):
                    toolbars.append(action)

            for dock_a in docks:
                new_menu.addAction(dock_a)
            new_menu.addSeparator()
            for toolbar_a in toolbars:
                new_menu.addAction(toolbar_a)

            return new_menu

        return menu

    def collect_all_actions(self):
        """
        Collect all QActions from a QMainWindow:
        - Window-level actions
        - Menu bar + menus (recursively)
        - Toolbars

        Returns:
            list of QAction objects (unique, order preserved)
        """
        collected_actions = []

        # 1. Actions directly added to the main window
        collected_actions.extend(self.actions())

        # 2. Menu bar and its menus
        menubar = self.menuBar()
        if menubar is not None:
            for menu in menubar.findChildren(QtWidgets.QMenu):
                collected_actions.extend(menu.actions())

        # 3. Toolbars and their actions
        for toolbar in self.findChildren(QtWidgets.QToolBar):
            try:
                collected_actions.extend(toolbar.actions())
            except TypeError as e:
                self.__logger_api.warning(
                    "The following toolbar is overriding default actions object! {}".format(toolbar))
                self.__logger_api.warning(e)

        # 4. Deduplicate while preserving order
        seen = set()
        unique_actions = []
        for act in collected_actions:
            if act not in seen:
                seen.add(act)
                unique_actions.append(act)

        return unique_actions
