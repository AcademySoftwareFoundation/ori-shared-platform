try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore
from rv import rvtypes
from rpa.open_rv.rpa_core.rpa_core import RpaCore
try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets


class RpaCoreMode(QtCore.QObject, rvtypes.MinorMode):

    def __init__(self):

        QtCore.QObject.__init__(self)
        rvtypes.MinorMode.__init__(self)

        self.__rpa_core = RpaCore()

        self.init(
            "RpaCoreMode", [
                ("frame-changed", self.__frame_changed, ""),
                ("pre-render", self.__pre_render, ""),
                ("post-render", self.__post_render, ""),
                ("play-start", self.__play_state_changed, ""),
                ("play-stop", self.__play_state_changed, "")

            ], None
        )
        app = QtWidgets.QApplication.instance()
        app.rpa_core = self.__rpa_core

    def __frame_changed(self, event):
        event.reject()
        self.__rpa_core.session_api._frame_changed()
        self.__rpa_core.timeline_api.emit_frame_changed()

    def __play_state_changed(self, event):
        event.reject()
        self.__rpa_core.timeline_api.emit_play_status_changed()

    def __pre_render(self, event):
        event.reject()
        self.__rpa_core.viewport_api.pre_render(event)
        self.__rpa_core.color_api.pre_render(event)

    def render(self, event):
        event.reject()
        self.__rpa_core.color_api.render(event)
        self.__rpa_core.annotation_api.render(event)
        self.__rpa_core.viewport_api.render(event)

    def __post_render(self, event):
        event.reject()
        self.__rpa_core.color_api.post_render(event)


def createMode():
    return RpaCoreMode()
