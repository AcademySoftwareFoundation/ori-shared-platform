try:
    from PySide2 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets


class InputLineEdit(QtWidgets.QLineEdit):
    """A LineEdit widget with several enhanced features:
        Emits SIG_GOT_FOCUS and SIG_LOST_FOCUS signals,
        Escape key clears current changes,
        Do not handle context menu events,
        Smaller size hints,
       """

    SIG_DRAG_ENTER_EVENT = QtCore.Signal(object, QtGui.QDragEnterEvent) # emit, event
    SIG_DRAG_START = QtCore.Signal(object, QtGui.QMouseEvent) # self, event
    SIG_DROP_EVENT = QtCore.Signal(object, QtGui.QDropEvent) # self, event
    SIG_GOT_FOCUS = QtCore.Signal()
    SIG_LOST_FOCUS = QtCore.Signal()

    SIG_DECREMENT = QtCore.Signal(int) # key event modifiers
    SIG_INCREMENT = QtCore.Signal(int) # key event modifiers
    SIG_SUPER_ENTER = QtCore.Signal()

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setAcceptDrops(False)
        self.returnPressed.connect(self.__clearFocus)
        self.__undoValue = None
        self.__middleDown = None


    @QtCore.Slot()
    def __clearFocus(self):
        self.clearFocus()


    def resetPalette(self):
        """Reset a palette back to normal"""
        self.setPalette(PaintingUtils.GetReadOnlyPalette(self.isReadOnly()))


    def sizeHint(self):
        size = QtWidgets.QLineEdit.sizeHint(self)
        size.setWidth(self.fontMetrics().horizontalAdvance('0')*8)
        return size


    def focusInEvent(self, event):
        QtWidgets.QLineEdit.focusInEvent(self, event)
        if event.reason() == QtCore.Qt.ActiveWindowFocusReason:
            return

        self.__undoValue = str(self.text())
        self.SIG_GOT_FOCUS.emit()


    def focusOutEvent(self, event):
        changed = bool(self.__undoValue != self.text())
        QtWidgets.QLineEdit.focusOutEvent(self, event)

        if not changed:
            return
        if event.reason() == QtCore.Qt.ActiveWindowFocusReason:
            return

        self.__undoValue = None
        self.SIG_LOST_FOCUS.emit()


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            event.accept()
            self.SIG_INCREMENT.emit(event.modifiers())
            return
        elif event.key() == QtCore.Qt.Key_Down:
            event.accept()
            self.SIG_DECREMENT.emit(event.modifiers())
            return
        elif event.key() == QtCore.Qt.Key_Enter and (event.modifiers() & QtCore.Qt.ControlModifier):
            self.SIG_SUPER_ENTER.emit()
            return
        elif event.key() == QtCore.Qt.Key_Return and (event.modifiers() & QtCore.Qt.ControlModifier):
            self.SIG_SUPER_ENTER.emit()
            return

        if event.key() == QtCore.Qt.Key_Escape:
            if self.__undoValue is not None:
                self.setText(self.__undoValue)
            self.clearFocus()
            event.accept()
            return
        if event.key() == QtCore.Qt.Key_Return:
            self.SIG_LOST_FOCUS.emit()
        QtWidgets.QLineEdit.keyPressEvent(self, event)


    def setReadOnly(self, state):
        QtWidgets.QLineEdit.setReadOnly(self, state)
        self.setPalette(PaintingUtils.GetReadOnlyPalette(state))


    def contextMenuEvent(self, event):
        QtWidgets.QWidget.contextMenuEvent(self, event)


    def dragEnterEvent(self, event):
        self.SIG_DRAG_ENTER_EVENT.emit(self, event)
        if not event.isAccepted():
            QtWidgets.QWidget.dragEnterEvent(self, event)


    def dropEvent(self, event):
        self.SIG_DROP_EVENT.emit(self, event)
        if not event.isAccepted():
            QtWidgets.QWidget.dropEvent(self, event)


    def mouseMoveEvent(self, event):
        if self.__middleDown:
            diff = event.globalPos() - self.__middleDown
            dist = abs(diff.x()) + abs(diff.y())
            if dist > 6:
                self.__middleDown = None
                self.SIG_DRAG_START.emit(self, event)
                event.accept()
        else:
            QtWidgets.QLineEdit.mouseMoveEvent(self, event)


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.__middleDown = QtCore.QPoint(event.globalPos())
            event.accept()

        if event.button() == QtCore.Qt.RightButton:
            return

        QtWidgets.QLineEdit.mousePressEvent(self, event)


    def mouseReleaseEvent(self, event):
        if self.__middleDown:
            self.__middleDown = None
            event.accept()

        QtWidgets.QLineEdit.mouseReleaseEvent(self, event)