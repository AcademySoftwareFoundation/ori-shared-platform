"""View elements of the MainDialog are held here."""

from collections import OrderedDict
from PySide2 import QtWidgets, QtCore, QtGui


class NoHideTogglableMenu(QtWidgets.QMenu):
    """Menu that persists even after a menu-item is selected"""
    def __init__(self, title:str, parent):
        super().__init__(title, parent)

    def mouseReleaseEvent(self, event):
        """Mouse release event"""
        action = self.activeAction()
        if action and action.isEnabled():
            action.setEnabled(False)
            super().mouseReleaseEvent(event)
            action.setEnabled(True)
            action.trigger()
        else:
            super().mouseReleaseEvent(event)


class PluginsTableView(QtWidgets.QTableView):
    """User interface for plugins data"""
    SIG_COPY_TO_CLIPBOARD = QtCore.Signal(list)
    SIG_MAKE_COLUMN_COPYABLE = QtCore.Signal(str, bool)

    def __init__(self):
        super().__init__()
        self.__context_menu = None
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setSelectionMode(QtWidgets.QTableView.ExtendedSelection)
        self.setWordWrap(True)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)

        vertical_header = self.verticalHeader()
        vertical_header.hide()
        vertical_header.setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)

        horizontal_header = self.horizontalHeader()
        horizontal_header.setSectionResizeMode(
            QtWidgets.QHeaderView.Interactive)
        horizontal_header.setSectionsMovable(True)

        self.__is_col_copyable_actions = {}
        self.__copy_action = None

        copy_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+C"), self)
        copy_shortcut.setContext(QtCore.Qt.WidgetShortcut)
        copy_shortcut.activated.connect(self.__copy_to_clipboard)

    def create_context_menu(self, header_names, copyable_col_names):
        """Create context menu for Plugins table"""
        self.__copy_action = QtWidgets.QAction("Copy (Ctrl+C)")
        self.__copy_action.triggered.connect(self.__copy_to_clipboard)

        self.__context_menu = QtWidgets.QMenu()
        self.__context_menu.addAction(self.__copy_action)

        copy_options_menu = \
            NoHideTogglableMenu("Copy Preference", self.__context_menu)
        for header_name in header_names:
            is_col_copyable_action = \
                QtWidgets.QAction(header_name, copy_options_menu)
            self.__is_col_copyable_actions[header_name] = \
                is_col_copyable_action
            is_col_copyable_action.setCheckable(True)
            if header_name in copyable_col_names:
                is_col_copyable_action.setChecked(True)
            is_col_copyable_action.toggled.connect(
                self.__toggle_is_col_copyable_action)
            copy_options_menu.addAction(is_col_copyable_action)
        self.__context_menu.addMenu(copy_options_menu)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            lambda pos: self.__context_menu.exec_(self.mapToGlobal(pos))
        )

    def __toggle_is_col_copyable_action(self):
        sender = self.sender()
        if sender and isinstance(sender, QtWidgets.QAction):
            self.SIG_MAKE_COLUMN_COPYABLE.emit(sender.text(), sender.isChecked())

    def __copy_to_clipboard(self):
        selected_rows = self.get_selected_plugin_rows()
        self.SIG_COPY_TO_CLIPBOARD.emit(selected_rows)

    def get_selected_plugin_rows(self):
        """Get the selected plugin rows based on proxy data model"""
        rows = OrderedDict()
        for model_index in self.selectedIndexes():
            rows[model_index.row()] = None
        return list(rows.keys())

    def get_plugins_copy_action(self):
        """Return the copy action of plugins table"""
        return self.__copy_action

    def make_col_copyable(self, header_name:str):
        """Make the column with the given header_name copyable"""
        action = self.__is_col_copyable_actions[header_name]
        action.setChecked(True)

    def get_current_row(self):
        """Get the plugin row whose data is currently being shown"""
        return self.currentIndex().row()

    def set_current_row(self, row:int):
        """Set the plugin row whose data is to be shown"""
        self.setCurrentIndex(self.model().index(row, 0))


class View(QtWidgets.QWidget):
    SIG_SEARCH_TXT_CHANGED = QtCore.Signal(str)
    SIG_COPY_TO_CLIPBOARD = QtCore.Signal(list)
    SIG_MAKE_COLUMN_COPYABLE = QtCore.Signal(str, bool)

    def __init__(self):
        super().__init__()
        search_label = QtWidgets.QLabel("Search:")
        search_line_edit = QtWidgets.QLineEdit()
        search_line_edit.setPlaceholderText(
            "Search through below listed plugins")
        search_line_edit.textChanged.connect(
            self.SIG_SEARCH_TXT_CHANGED)

        self.__plugins_table_view = PluginsTableView()
        self.__plugins_table_view.setContentsMargins(0, 0, 0, 0)
        self.__plugins_table_view.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.__plugins_table_view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.__plugins_table_view.SIG_COPY_TO_CLIPBOARD.connect(
            self.SIG_COPY_TO_CLIPBOARD)
        self.__plugins_table_view.SIG_MAKE_COLUMN_COPYABLE.connect(
            self.SIG_MAKE_COLUMN_COPYABLE)

        clear_selection_btn = QtWidgets.QPushButton("Clear Selection")
        clear_selection_btn.clicked.connect(
            self.__plugins_table_view.clearSelection)

        search_input_layout = QtWidgets.QHBoxLayout()
        search_input_layout.setContentsMargins(0, 0, 0, 0)
        search_input_layout.addWidget(search_label)
        search_input_layout.addWidget(search_line_edit)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(search_input_layout)
        main_layout.addWidget(self.__plugins_table_view)
        main_layout.addWidget(clear_selection_btn)

        self.setLayout(main_layout)

    def set_plugins_table_model(self, model):
        """Set the data model of the plugins table"""
        self.__plugins_table_view.setModel(model)

    def get_selected_plugin_rows(self):
        """Get the selected plugin rows based on proxy data model"""
        return self.__plugins_table_view.get_selected_plugin_rows()

    def create_plugins_context_menu(self, header_names, copyable_cols):
        """ Create context menu of the plugins table"""
        self.__plugins_table_view.create_context_menu(
            header_names, copyable_cols)

    def get_plugins_copy_action(self):
        """Get the copy action of the plugins table"""
        return self.__plugins_table_view.get_plugins_copy_action()

    def make_column_copyable(self, header_name):
        """Make the column with the given header name copyable"""
        self.__plugins_table_view.make_col_copyable(header_name)

    def get_current_plugin_row(self):
        """Get the plugin row whose data are being currently shown"""
        return self.__plugins_table_view.get_current_row()

    def set_current_plugin_row(self, row):
        """Set the plugin row whose data are to be shown"""
        self.__plugins_table_view.set_current_row(row)
