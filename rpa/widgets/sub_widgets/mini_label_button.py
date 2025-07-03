from PySide2 import QtCore, QtGui, QtWidgets


def SetCompactWidgetWidth(w, padding = 7):
    w.setFixedWidth(w.fontMetrics().horizontalAdvance(str(w.text())) + padding)

class MiniLabelButton(QtWidgets.QLabel):
    SIG_CLICKED = QtCore.Signal()

    def __init__(self, text, parent):
        super().__init__(text)
        smallFont = QtGui.QFont(self.font())
        smallFont.setPointSizeF( smallFont.pointSizeF() * 0.9 )
        self.setFont(smallFont)
        self.setAlignment( QtCore.Qt.AlignCenter)
        self.setCursor(QtCore.Qt.PointingHandCursor)

        self.__inside = False
        self.__checked = False
        SetCompactWidgetWidth(self, 12)
        self.setFixedHeight(20)
        self.updateState()

    def enterEvent(self, ev):
        self.__inside = True
        self.updateState()

    def leaveEvent(self, ev):
        self.__inside = False
        self.updateState()

    def updateState(self):
        if not self.isEnabled(): return
        if self.__inside or self.__checked:
            self.setForegroundRole(QtGui.QPalette.Highlight)
        else:
            self.setForegroundRole(QtGui.QPalette.BrightText)

    def paintEvent(self, ev):
        super(MiniLabelButton, self).paintEvent(ev)
        p = QtGui.QPainter(self)
        x = self.width()
        y = self.height()

        p.setPen(self.palette().color(QtGui.QPalette.BrightText))
        p.drawLine(0,0,x, 0)
        p.drawLine(0,y-1,x, y-1)
        p.drawLine(0,0,0, y-1)
        p.drawLine(x-1,0,x-1, y-1)

    def mouseReleaseEvent(self, ev):
        if not self.__inside:
            return

        self.SIG_CLICKED.emit()

    def setChecked(self, checked):
        self.__checked = checked
        self.updateState()

    def isChecked(self):
        return self.__checked