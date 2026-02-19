from PySide2 import QtWidgets


class ItvDockWidget(QtWidgets.QDockWidget):

    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.setObjectName(title)
        self.setWindowTitle(title)

    def is_docked_alone(self):
        main_window = self.parentWidget()
        if not isinstance(main_window, QtWidgets.QMainWindow):
            return False

        tabified_widgets = main_window.tabifiedDockWidgets(self)
        visible_tabified_widgets = \
            [widget for widget in tabified_widgets if widget.isVisible()]
        if all(widget.isFloating() for widget in visible_tabified_widgets):
            return True

        return len(visible_tabified_widgets) == 0

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        options = QtWidgets.QStyleOptionDockWidget()
        self.initStyleOption(options)

        if self.isFloating() or self.is_docked_alone():
            options.title = self.windowTitle()
        else:
            options.title = ""

        painter.drawControl(QtWidgets.QStyle.CE_DockWidgetTitle, options)

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()

    def setWidget(self, widget):
        super().setWidget(widget)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        widget.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        widget.setMinimumSize(100, 100)
        widget.setMaximumSize(1e6, 1e6)
