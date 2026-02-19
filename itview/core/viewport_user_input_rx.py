try:
    from PySide2 import QtCore, QtGui, QtWidgets
except:
    from PySide6 import QtCore, QtGui, QtWidgets


def require_viewport_widget(method):
    def wrapper(self, *args, **kwargs):
        if getattr(self, "_ViewportUserInputRx__viewport_widget", None) is None:
            return None
        return method(self, *args, **kwargs)
    return wrapper


class ViewportUserInputRx:

    def __init__(self):
        self.__viewport_widget = None

    def set_viewport_widget(self, widget):
        self.__viewport_widget = widget

    @require_viewport_widget
    def mouse_press(self, x, y):
        mouse_event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseButtonPress, QtCore.QPointF(x, y),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)
        QtWidgets.QApplication.sendEvent(self.__viewport_widget, mouse_event)
        print("mouse_press")

    @require_viewport_widget
    def mouse_drag(self, x, y):
        mouse_event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseMove, QtCore.QPointF(x, y),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)
        QtWidgets.QApplication.sendEvent(self.__viewport_widget, mouse_event)
        print("mouse_drag")

    @require_viewport_widget
    def mouse_release(self, x, y):
        mouse_event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseButtonRelease, QtCore.QPointF(x, y),
            QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)
        QtWidgets.QApplication.sendEvent(self.__viewport_widget, mouse_event)
        print("mouse_release")

    @require_viewport_widget
    def mouse_move(self, x, y):
        mouse_event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseMove, QtCore.QPointF(x, y),
            QtCore.Qt.NoButton, QtCore.Qt.NoButton, QtCore.Qt.NoModifier)
        QtWidgets.QApplication.sendEvent(self.__viewport_widget, mouse_event)
        print("mouse_move")
