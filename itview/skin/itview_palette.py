from PySide2 import QtCore, QtGui


class ItviewPalette(QtGui.QPalette):

    def __init__(self):
        super().__init__()

        def make_gray_color(f):
            return QtGui.QColor.fromRgbF(f, f, f)

        # Central roles
        self.setColor(QtGui.QPalette.Window, make_gray_color(0.18))
        self.setColor(QtGui.QPalette.WindowText, make_gray_color(0.70))
        self.setColor(QtGui.QPalette.Base, make_gray_color(0.22))
        self.setColor(QtGui.QPalette.AlternateBase, make_gray_color(0.25))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, QtGui.QColor(254, 253, 208))
        self.setColor(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, QtGui.QColor(QtCore.Qt.black))
        self.setColor(QtGui.QPalette.Text, self.color(QtGui.QPalette.WindowText))
        self.setColor(QtGui.QPalette.Button, self.color(QtGui.QPalette.Window))
        self.setColor(QtGui.QPalette.ButtonText, self.color(QtGui.QPalette.WindowText))
        self.setColor(QtGui.QPalette.BrightText, self.color(QtGui.QPalette.WindowText))

        # 3D bevel and shadow effects
        self.setColor(QtGui.QPalette.Light, make_gray_color(0.42))
        self.setColor(QtGui.QPalette.Midlight, make_gray_color(0.32))
        self.setColor(QtGui.QPalette.Mid, make_gray_color(0.22))
        self.setColor(QtGui.QPalette.Dark, make_gray_color(0.10))
        self.setColor(QtGui.QPalette.Shadow, make_gray_color(0.02))

        # Selected (marked) items
        self.setColor(QtGui.QPalette.Highlight, QtGui.QColor.fromRgbF(0.31, 0.31, 0.25))
        self.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(QtCore.Qt.white))

        # Hyperlinks
        self.setColor(QtGui.QPalette.Link, QtGui.QColor(249, 180, 27))
        self.setColor(QtGui.QPalette.LinkVisited, QtGui.QColor(249, 180, 27))

        # Disabled text
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, make_gray_color(0.46))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, self.color(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, self.color(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText))
        self.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, make_gray_color(0.55))
