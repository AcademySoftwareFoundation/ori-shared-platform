from PySide2 import QtWidgets, QtGui, QtCore


class ProgressBar(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setModal(True)
        self.setMinimumWidth(300)

        self.__ui_threshold = 0

        layout = QtWidgets.QVBoxLayout(self)

        self.__label = QtWidgets.QLabel("")
        layout.addWidget(self.__label)

        self.__progress_bar = QtWidgets.QProgressBar(self)
        self.__progress_bar.setRange(0, 100)
        layout.addWidget(self.__progress_bar)

        self.setWindowFlags(
            self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

    def __center_on_screen(self):
        screen = QtGui.QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        dialog_geometry = self.geometry()

        x = (screen_geometry.width() - dialog_geometry.width()) // 2
        y = (screen_geometry.height() - dialog_geometry.height()) // 2
        self.move(x, y)

    def init(self, window_title, label, maximum):
        if maximum <= self.__ui_threshold:
            return
        self.setWindowTitle(window_title)
        self.__label.setText(label)
        self.__progress_bar.setMinimum(0)
        self.__progress_bar.setValue(0)
        self.__progress_bar.setMaximum(maximum)
        self.__center_on_screen()
        self.show()

    def update(self, window_title, label, value, maximum):
        if maximum <= self.__ui_threshold:
            return True
        label = label + f" {value}/{maximum}"
        self.__label.setText(label)
        self.__progress_bar.setValue(value)
        if value == maximum:
            return False
        return True
