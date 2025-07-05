try:
    from PySide2 import QtGui, QtCore, QtWidgets
    from PySide2.QtWidgets import QAction, QActionGroup
except ImportError:
    from PySide6 import QtGui, QtCore, QtWidgets
    from PySide6.QtGui import QAction, QActionGroup

class Actions(QtCore.QObject):
    def __init__(self):
        super().__init__()

        self.turn_off_background = QAction("Turn Off Background")
        self.turn_off_background.setShortcut(QtGui.QKeySequence("Alt+D"))

        self.wipe = QAction("Wipe Mode") # TODO: move to interactive toolbar once added
        self.wipe.setCheckable(True)

        self.pip = QAction("Picture in Picture", parent=self)
        self.pip.setCheckable(True)
        self.pip.setShortcut(QtGui.QKeySequence("Ctrl+Shift+B"))

        self.side_by_side = QAction("Side by Side", parent=self)
        self.side_by_side.setCheckable(True)
        self.side_by_side.setShortcut(QtGui.QKeySequence("Ctrl+Shift+S"))

        self.top_to_bottom = QAction("Top to Bottom", parent=self)
        self.top_to_bottom.setCheckable(True)
        self.top_to_bottom.setShortcut(QtGui.QKeySequence("Ctrl+Shift+T"))

        self.swap_background = QAction(
            "Swap Foreground with Background", parent=self)
        self.swap_background.setShortcut(
            QtGui.QKeySequence("Shift+Space"))

        action_group = QActionGroup(self)
        action_group.addAction(self.pip)
        action_group.addAction(self.side_by_side)
        action_group.addAction(self.top_to_bottom)
        action_group.setExclusionPolicy(QActionGroup.ExclusionPolicy.ExclusiveOptional)
