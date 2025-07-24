try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtWidgets import QAction
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QAction
from rpa.widgets.session_manager.clips_controller.view.model import THUMBNAIL_WIDTH


class ActionWithStrData(QAction):
    SIG_TRIGGERED = QtCore.Signal(str)

    def __init__(self, name, data):
        super().__init__(name)
        self.__data = data
        self.triggered.connect(
            lambda: self.SIG_TRIGGERED.emit(self.__data))

class HeaderView(QtWidgets.QHeaderView):
    SIG_REFRESH_ATTR = QtCore.Signal(str)
    SIG_REFRESH_ALL_ATTRS = QtCore.Signal()
    SIG_COLUMN_HIDDEN = QtCore.Signal(int, bool) # column_index, is_hidden

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setMinimumHeight(30)
        self.setDefaultSectionSize(120)

        self.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        self.setSectionsMovable(True)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        self.setSortIndicatorShown(True)

        self.__clip_attrs_button = QtWidgets.QToolButton(self)
        self.__clip_attrs_button.setIcon(
            QtGui.QIcon(QtGui.QPixmap(":column_popdown.png")))
        self.__clip_attrs_button.setToolTip("Select columns to display")
        self.__clip_attrs_button.setFixedSize(30, self.height())
        self.__clip_attrs_button.clicked.connect(self.__toggle_clip_attrs_menu)

        self.__clip_attrs_menu = NoHideTogglableMenu('Columns', self)
        search_widget_action = SearchLineEditAction(
            self.__clip_attrs_menu,
            placeholder_text="Search,..",
            line_edit_width=100)
        self.__clip_attrs_menu.addAction(search_widget_action)
        search_widget_action.SIG_TXT_CHANGED.connect(
            self.__clip_attrs_menu.filter_actions)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self.__show_header_context_menu)

        self.__thumbnail_column_index = None

    @property
    def clip_attrs_menu(self):
        return self.__clip_attrs_menu

    def load_column_toggle_menu(self):
        if self.model() is None:
            return
        source_model = self.model().sourceModel()
        column_count = source_model.columnCount()
        all_data = {column: source_model.headerData(column, QtCore.Qt.Horizontal) \
            for column in range(column_count)}
        sorted_data = dict(sorted(all_data.items(), key=lambda item:item[1]))

        for column, header_data in sorted_data.items():
            self.setSectionHidden(column, True)
            action = QAction(header_data, self.__clip_attrs_menu)
            action.setCheckable(True)
            action.setChecked(False)
            action.setData(column)
            action.toggled.connect(self.__toggle_column_visibility)
            self.__clip_attrs_menu.addAction(action)

            attr = source_model.attrs[column]
            if attr == "play_order":
                action.setEnabled(False)
            if attr == "thumbnail_url":
                self.__thumbnail_column_index = column

    def set_column_hidden(self, index, is_hidden):
        column_name = self.model().headerData(index, QtCore.Qt.Horizontal)
        is_checked = not is_hidden
        for action in self.__clip_attrs_menu.actions():
            if action.text() == column_name and \
            action.isChecked() != is_checked:
                action.setChecked(is_checked)

    def __toggle_column_visibility(self, checked):
        action = self.sender()
        column_index = action.data()
        hidden = not checked
        self.setSectionHidden(column_index, hidden)
        if checked and column_index == self.__thumbnail_column_index:
            self.parent().setColumnWidth(self.__thumbnail_column_index, THUMBNAIL_WIDTH+10)
        self.SIG_COLUMN_HIDDEN.emit(column_index, hidden)

    def __toggle_clip_attrs_menu(self):
        pos = self.__clip_attrs_button.mapToGlobal(
            self.__clip_attrs_button.rect().bottomLeft())
        self.__clip_attrs_menu.exec_(pos)
        self.__clip_attrs_menu.show()

    def __show_header_context_menu(self, pos):
        cursor_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        column_index = self.logicalIndexAt(cursor_pos)
        is_clicked_on_attr_column = True
        if column_index == -1:
            is_clicked_on_attr_column = False

        attr = self.model().sourceModel().attrs[column_index]
        menu = QtWidgets.QMenu(self)
        global_pos = self.mapToGlobal(pos)
        section_pos = self.sectionViewportPosition(column_index)
        section_h = self.height()

        menu_pos = QtCore.QPoint(section_pos, section_h)
        global_menu_pos = self.mapToGlobal(menu_pos)
        global_menu_pos.setY(global_menu_pos.y() + 1)

        if is_clicked_on_attr_column:
            refresh_action = ActionWithStrData("Refresh column", attr)
            menu.addAction(refresh_action)
            refresh_action.SIG_TRIGGERED.connect(self.SIG_REFRESH_ATTR)

            hide_action = menu.addAction("Hide column")
            hide_action.triggered.connect(lambda: self.__hide_column(column_index))
            if attr == "play_order":
                hide_action.setEnabled(False)

        refresh_all_action = menu.addAction("Refresh all columns")
        refresh_all_action.triggered.connect(self.SIG_REFRESH_ALL_ATTRS)

        menu.addMenu(self.__clip_attrs_menu)

        menu.exec_(global_pos)

    def __hide_column(self, column):
        column_name = self.model().headerData(column, QtCore.Qt.Horizontal)
        hidden = True
        self.setSectionHidden(column, hidden)
        self.SIG_COLUMN_HIDDEN.emit(column, hidden)
        for action in self.__clip_attrs_menu.actions():
            if action.text() == column_name:
                action.blockSignals(True)
                action.setChecked(False)
                action.blockSignals(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.__clip_attrs_button.move(
            self.width() - self.__clip_attrs_button.width(), 0)

class SearchLineEditAction(QtWidgets.QWidgetAction):
    SIG_TXT_CHANGED = QtCore.Signal(str)

    def __init__(self, parent, placeholder_text="", line_edit_width=200):
        super().__init__(parent)
        self.__line_edit = QtWidgets.QLineEdit(parent)
        self.__line_edit.setPlaceholderText("Search,..")
        self.__line_edit.textChanged.connect(self.SIG_TXT_CHANGED)
        self.__line_edit.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.__line_edit.setFocus()

    def createWidget(self, parent):
        return self.__line_edit

class NoHideTogglableMenu(QtWidgets.QMenu):
    def __init__(self, title:str, parent=None):
        super().__init__(title, parent)

    def mouseReleaseEvent(self, event):
        action = self.activeAction()
        if action and action.isEnabled():
            action.setEnabled(False)
            super().mouseReleaseEvent(event)
            action.setEnabled(True)
            action.trigger()
        else:
            super().mouseReleaseEvent(event)

    def actions(self):
        actions = super().actions()
        return [action for action in actions \
            if not isinstance(action, SearchLineEditAction)]

    def filter_actions(self, text):
        for action in self.actions():
            if isinstance(action, SearchLineEditAction):
                continue
            action.setVisible(text.lower() in action.text().lower())

class HeaderViewPrefCntrlr:
    def __init__(self, view:HeaderView):
        self.__view = view
        self.__source_model = self.__view.model().sourceModel()

    def set_attrs(self, attrs):

        if len(attrs) == 1 and attrs[0] == "play_order":
            attrs = ["play_order", "media_path"]
        all_attrs = []
        attrs_set = set(attrs)
        for action in self.__view.clip_attrs_menu.actions():
            column = action.data()
            attr = self.__source_model.attrs[column]
            all_attrs.append(attr)
            if attr in attrs_set:
                action.setChecked(True)

        visual_attrs = []
        index = -1
        for attr in attrs:
            if attr in all_attrs:
                index = index + 1
                visual_attrs.append(attr)

        model_attrs = self.__source_model.attrs
        for index, attr in enumerate(visual_attrs):
            attr_index = model_attrs.index(attr)
            self.__view.moveSection(
                self.__view.visualIndex(attr_index), index)

    def get_attrs(self):
        columns = []
        for index in range(self.__source_model.columnCount()):
            if not self.__view.isSectionHidden(index):
                attr = self.__source_model.attrs[index]
                columns.append((attr, index))

        visually_sorted_columns = sorted(columns,
            key=lambda attr_pair: self.__view.visualIndex(attr_pair[1]))
        return [attr_pair[0] for attr_pair in visually_sorted_columns]

    def set_sort_state(self, attr, order):
        if not order:
            order = QtCore.Qt.DescendingOrder

        model_attrs = self.__source_model.attrs
        if any([not attr, attr not in model_attrs]):
            sort_attr = "play_order"
        else:
            sort_attr = attr
        column_index = model_attrs.index(sort_attr)
        self.__view.setSortIndicator(column_index, order)

    def get_sort_state(self):
        attr = self.__source_model.attrs[self.__view.sortIndicatorSection()]
        return attr, self.__view.sortIndicatorOrder()

    def set_column_widths(self, column_widths):
        for index in range(self.__source_model.columnCount()):
            column_name = self.__source_model.\
                headerData(index, QtCore.Qt.Horizontal)
            width = column_widths.get(column_name)
            if width:
                parent_widget = self.__view.parentWidget()
                if isinstance(parent_widget, QtWidgets.QTableView):
                    parent_widget.setColumnWidth(index, width)

    def get_column_widths(self):
        column_widths = {}
        for index in range(self.__source_model.columnCount()):
            column_name = \
                self.__source_model.headerData(index, QtCore.Qt.Horizontal)
            parent_widget = self.__view.parentWidget()
            if isinstance(parent_widget, QtWidgets.QTableView):
                column_widths[column_name] = parent_widget.columnWidth(index)
        return column_widths
