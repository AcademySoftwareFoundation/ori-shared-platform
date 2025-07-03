from PySide2 import QtGui, QtWidgets


class StripedFrame(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()

    def paintEvent(self, ev):
        super(StripedFrame, self).paintEvent(ev)
        p = QtGui.QPainter(self)
        x = self.width()
        y = self.height()
        p.setPen(self.palette().color(QtGui.QPalette.Light))
        p.drawLine(0,0,x, 0)