from PySide2 import QtGui, QtCore, QtWidgets


class Actions(QtCore.QObject):

    def __init__(self):
        super().__init__()

        self.toggle_mask = QtWidgets.QAction("Toggle Mask")
        self.toggle_mask.setCheckable(True)
        self.toggle_mask.setShortcut(QtGui.QKeySequence("K"))

        self.cycle_mask = QtWidgets.QAction("Cycle Masks")
        self.cycle_mask.setShortcut(QtGui.QKeySequence("Alt+K"))

        self.guess_mask = QtWidgets.QAction("Guess Mask")
        self.guess_mask.setCheckable(True)