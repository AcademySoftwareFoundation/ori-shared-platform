from PySide2 import QtGui, QtCore, QtWidgets


class Actions(QtCore.QObject):
    def __init__(self):
        super().__init__()

        self.fullscreen = QtWidgets.QAction("Fullscreen")
        self.fullscreen.setCheckable(True)
        self.fullscreen.setShortcut(QtGui.QKeySequence("F2"))

        self.fit_modes_radio = QtWidgets.QActionGroup(self)

        self.fit_to_window = QtWidgets.QAction("Fit To Window")
        self.fit_to_window.setCheckable(True)
        self.fit_to_window.setShortcut(QtGui.QKeySequence("F4"))

        self.fit_to_width = QtWidgets.QAction("Fit To Width")
        self.fit_to_width.setCheckable(True)
        self.fit_to_width.setShortcut(QtGui.QKeySequence("F5"))

        self.fit_to_height = QtWidgets.QAction("Fit To Height")
        self.fit_to_height.setCheckable(True)
        self.fit_to_height.setShortcut(QtGui.QKeySequence("F6"))

        self.fit_modes_radio.addAction(self.fit_to_window)
        self.fit_modes_radio.addAction(self.fit_to_width)
        self.fit_modes_radio.addAction(self.fit_to_height)
        self.fit_modes_radio.setExclusionPolicy(
            QtWidgets.QActionGroup.ExclusionPolicy.ExclusiveOptional
        )

        self.zoom_in = QtWidgets.QAction("Zoom In")
        self.zoom_in.setShortcut(QtGui.QKeySequence("="))

        self.zoom_out = QtWidgets.QAction("Zoom Out")
        self.zoom_out.setShortcut(QtGui.QKeySequence("-"))

        self.flip_x = QtWidgets.QAction("Flip Horizontally")
        self.flip_x.setCheckable(True)
        self.flip_x.setShortcut(QtGui.QKeySequence("P"))

        self.flip_y = QtWidgets.QAction("Flip Vertically")
        self.flip_y.setCheckable(True)
        self.flip_y.setShortcut(QtGui.QKeySequence("Shift+P"))

        self.reset_viewer = QtWidgets.QAction("Reset Viewer")
        self.reset_viewer.setShortcut(QtGui.QKeySequence("Home"))

        self.toggle_presentation_mode = QtWidgets.QAction("Toggle Presentation Mode")

        self.__create_zoom_modes()

    def __create_zoom_modes(self):
        self.zoom_modes = {}
        for i in range(1,11):
            zoom_mode = QtWidgets.QAction("{:.3f}".format(float(i)))
            zoom_mode.setShortcut(QtGui.QKeySequence(str(i%10)))
            self.zoom_modes[i] = zoom_mode