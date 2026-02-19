from PySide2 import QtCore


class ViewportUserInputManager(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def itview_init(self, itview):
        self.__session_api = itview.rpa.session_api
        self.__main_window = itview.main_window
        self.__viewport_user_input = itview.viewport_user_input

        core_view = self.__main_window.get_core_view()
        print("core_view", core_view, type(core_view))
        core_view.installEventFilter(self)
        core_view.setMouseTracking(True)

    def eventFilter(self, obj, event):
        if not (
        event.type() == QtCore.QEvent.MouseButtonPress or
        event.type() == QtCore.QEvent.MouseMove or
        event.type() == QtCore.QEvent.MouseButtonRelease):
            return False

        get_pos = lambda: (event.pos().x(), event.pos().y())
        if event.type() == QtCore.QEvent.MouseButtonPress:
            self.__viewport_user_input.mouse_press(*get_pos())
        if event.type() == QtCore.QEvent.MouseMove:
            if event.buttons() == QtCore.Qt.NoButton:
                self.__viewport_user_input.mouse_move(*get_pos())
            elif event.buttons() == QtCore.Qt.LeftButton:
                self.__viewport_user_input.mouse_drag(*get_pos())
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self.__viewport_user_input.mouse_release(*get_pos())

        return False
