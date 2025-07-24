try:
    from PySide2 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets
from rpa.widgets.session_manager.playlists_controller.view.item_delegate \
    import ItemDelegate
from rpa.widgets.session_manager.playlists_controller.view.style \
    import Style


class View(QtWidgets.QListView):
    SIG_CONTEXT_MENU_REQUESTED = QtCore.Signal(object, QtCore.QPoint)
    SIG_SET_FG = QtCore.Signal(str) # playlist_id
    SIG_SET_BG = QtCore.Signal(str) # playlist_id
    SIG_DELETE = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setHeaderHidden(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setItemDelegate(ItemDelegate(self))
        self.setEnabled(True)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setStyle(Style())

        self.__mime_data_formats = []

    def setModel(self, model):
        super().setModel(model)

    def contextMenuEvent(self, event):
        mindex = self.indexAt(event.pos())
        global_pos = self.mapToGlobal(event.pos())
        self.SIG_CONTEXT_MENU_REQUESTED.emit(mindex, global_pos)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        id = self.model().playlist_ids[index.row()]

        if event.button() == QtCore.Qt.LeftButton:
            if index.isValid():
                if event.modifiers() & QtCore.Qt.ControlModifier:
                    self.selectionModel().select(index, QtCore.QItemSelectionModel.Toggle)
                    return
                elif event.modifiers() & QtCore.Qt.ShiftModifier:
                    super().mousePressEvent(event)
                elif event.modifiers() & QtCore.Qt.AltModifier:
                    self.SIG_SET_BG.emit(id)
                else:
                    self.selectionModel().setCurrentIndex(
                        index, QtCore.QItemSelectionModel.NoUpdate)
                    self.SIG_SET_FG.emit(id)
                    return
            else:
                super().mousePressEvent(event)

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        index = self.indexAt(event.pos())
        if index.isValid():
            self.edit(index)
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton and \
            event.modifiers() & QtCore.Qt.ShiftModifier:
            index = self.indexAt(event.pos())
            if index.isValid():
                self.SIG_DELETE.emit()
        super().mouseReleaseEvent(event)

    def rename_requested(self, index):
        self.edit(index)

    def clear_selection(self):
        self.selectionModel().clearSelection()

    def select_playlists(self, playlist_ids):
        selection_model = self.selectionModel()
        all_playlist_ids = self.model().playlist_ids

        selection_model.blockSignals(True)
        selection_model.clearSelection()

        valid_playlist_ids = [id for id in playlist_ids if id in all_playlist_ids]
        for id in valid_playlist_ids:
            index = all_playlist_ids.index(id)
            mindex = self.model().index(index, 0)
            selection_model.select(
                mindex, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows)

        selection_model.blockSignals(False)

    def get_mindex_at_pos(self):
        pos = self.viewport().mapFromGlobal(QtGui.QCursor.pos())
        return self.indexAt(pos)

    def get_selected_mindexes(self):
        return self.selectionModel().selectedIndexes()

    def get_selected_indexes(self):
        mindexes = self.selectionModel().selectedRows()
        return [mindex.row() for mindex in mindexes]

    def startDrag(self, supportedActions):
        drag = QtGui.QDrag(self)
        mime_data = self.model().mimeData(
            self.selectionModel().selectedIndexes())
        self.__mime_data_formats = mime_data.formats()
        drag.setMimeData(mime_data)
        drag.setPixmap(QtGui.QPixmap())
        drag.exec_(supportedActions)

    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        self.__mime_data_formats = mime_data.formats()
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        self.__mime_data_formats = []
        super().dropEvent(event)

    def get_mime_data_formats(self):
        return self.__mime_data_formats

    def get_prev_next_rect(self):
        pos = self.viewport().mapFromGlobal(QtGui.QCursor.pos())
        mindex_at_pos = self.indexAt(pos)
        rect = self.visualRect(mindex_at_pos)
        y_coord = rect.y()
        height = rect.height()

        prev_index = self.indexAt(QtCore.QPoint(pos.x(), y_coord - height))
        next_index = self.indexAt(QtCore.QPoint(pos.x(), y_coord + height))
        prev_rect = self.visualRect(prev_index)
        next_rect = self.visualRect(next_index)

        return prev_rect, next_rect

    def get_drop_indicator_pen(self):
        return QtGui.QPen(QtGui.QColor("snow"), 1.0, QtCore.Qt.DotLine)
