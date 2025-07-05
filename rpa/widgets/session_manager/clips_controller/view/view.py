try:
    from PySide2 import QtCore, QtWidgets, QtGui
except ImportError:
    from PySide6 import QtCore, QtWidgets, QtGui
from rpa.widgets.session_manager.clips_controller.view.item_delegate \
    import ItemDelegate
from rpa.widgets.session_manager.clips_controller.view.model import THUMBNAIL_HEIGHT
from rpa.widgets.session_manager.clips_controller.view.style \
    import Style


class Table(QtWidgets.QTableView):
    SIG_CONTEXT_MENU_REQUESTED = QtCore.Signal(int, QtCore.QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.setWordWrap(True)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setItemDelegate(ItemDelegate(self))
        self.verticalHeader().setDefaultSectionSize(THUMBNAIL_HEIGHT)

        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setStyle(Style())

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos()).row()
        global_pos = self.mapToGlobal(event.pos())
        self.SIG_CONTEXT_MENU_REQUESTED.emit(index, global_pos)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            self.setDragEnabled(True)
        super().mousePressEvent(event)

    def select_clips(self, clips):
        selection_model = self.selectionModel()
        source_model = self.model().sourceModel()

        current_total = source_model.rowCount()
        current_selections = []
        for index in selection_model.selectedRows():
            mindex = self.model().mapToSource(index)
            id = source_model.clips[mindex.row()]
            current_selections.append(id)
        if current_total == len(current_selections):
            clips = current_selections

        selection_model.blockSignals(True)
        selection_model.clearSelection()

        start_index = source_model.index(0, 0)
        end_index = source_model.index(
            source_model.rowCount() - 1, source_model.columnCount() - 1)
        source_model.dataChanged.emit(start_index, end_index, [QtCore.Qt.DisplayRole])
        for id in clips:
            row = source_model.clips.index(id)
            source_index = source_model.index(row, 0)
            model_index = self.model().mapFromSource(source_index)
            if not model_index:
                continue
            selection_model.select(
                model_index, QtCore.QItemSelectionModel.Select | \
                    QtCore.QItemSelectionModel.Rows)
            source_model.dataChanged.emit(source_index, source_index, [QtCore.Qt.DisplayRole])
        selection_model.blockSignals(False)

    def get_selected_indexes(self):
        mindexes = self.selectionModel().selectedRows()
        return [mindex.row() for mindex in mindexes]

    def get_mindex_at_pos(self):
        pos = self.viewport().mapFromGlobal(QtGui.QCursor.pos())
        return self.indexAt(pos)

    def get_drop_indicator_pen(self):
        return QtGui.QPen(QtGui.QColor("snow"), 2, QtCore.Qt.DotLine)

    def startDrag(self, supportedActions):
        drag = QtGui.QDrag(self)
        mime_data = self.model().mimeData(self.selectionModel().selectedIndexes())
        drag.setMimeData(mime_data)
        drag.setPixmap(QtGui.QPixmap())
        drag.exec_(supportedActions)


class View(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__header_layout = QtWidgets.QVBoxLayout()

        self.__stack = QtWidgets.QStackedWidget(parent)
        self.__table = Table(self.__stack)
        self.__stack.addWidget(self.__table)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.__header_layout)
        layout.addWidget(self.__stack)

        self.setLayout(layout)

    @property
    def header_layout(self):
        return self.__header_layout

    @property
    def stack(self):
        return self.__stack

    @property
    def table(self):
        return self.__table
