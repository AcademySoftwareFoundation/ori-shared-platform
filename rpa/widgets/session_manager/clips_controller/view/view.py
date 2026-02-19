try:
    from PySide2 import QtCore, QtWidgets, QtGui
except:
    from PySide6 import QtCore, QtWidgets, QtGui
from rpa.widgets.session_manager.clips_controller.view.item_delegate \
    import ItemDelegate
from rpa.widgets.session_manager.clips_controller.view.model import \
    THUMBNAIL_HEIGHT, ACTIVE_CLIPS_ROW_COLOR
from rpa.widgets.session_manager.clips_controller.view.style \
    import Style


class Table(QtWidgets.QTableView):
    SIG_CONTEXT_MENU_REQUESTED = QtCore.Signal(str, int, QtCore.QPoint)
    SIG_EMPTY_SPACE_CLICKED = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
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

        palette = self.palette()
        palette.setColor(
            QtGui.QPalette.Highlight, QtGui.QColor(*ACTIVE_CLIPS_ROW_COLOR))
        self.setPalette(palette)


    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos()).row()
        if index == -1:
            actual_index = -1
            clip_id = None
        else:
            source_model = self.model().sourceModel()
            proxy_model = source_model.get_proxy_model()
            source_mindex = proxy_model.mapToSource(self.indexAt(event.pos()))
            actual_index = source_mindex.row()
            clip_id = source_model.clips[actual_index]

        global_pos = self.mapToGlobal(event.pos())
        self.SIG_CONTEXT_MENU_REQUESTED.emit(clip_id, actual_index, global_pos)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            self.SIG_EMPTY_SPACE_CLICKED.emit()

        if event.button() == QtCore.Qt.MidButton:
            self.setDragEnabled(True)
        super().mousePressEvent(event)

    def select_clips(self, clips):
        selection_model = self.selectionModel()
        source_model = self.model().sourceModel()
        old_current_index = selection_model.currentIndex()

        selection_model.blockSignals(True)
        selection_model.clearSelection()

        first_selected_model_index = None
        for clip in clips:
            row = source_model.clips.index(clip)
            if row is None: continue
            source_index = source_model.index(row, 0)
            model_index = self.model().mapFromSource(source_index)
            if not model_index:
                continue
            selection_model.select(
                model_index, QtCore.QItemSelectionModel.Select | \
                    QtCore.QItemSelectionModel.Rows)
            if first_selected_model_index is None:
                first_selected_model_index = model_index
            source_model.dataChanged.emit(source_index, source_index, [QtCore.Qt.DisplayRole])

        current_model_index = None
        if old_current_index.row() != -1 and old_current_index.isValid():
            current_model_index = old_current_index
        else:
            current_model_index = first_selected_model_index

        if current_model_index:
            selection_model.setCurrentIndex(
                current_model_index, QtCore.QItemSelectionModel.NoUpdate)

        selection_model.blockSignals(False)

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
