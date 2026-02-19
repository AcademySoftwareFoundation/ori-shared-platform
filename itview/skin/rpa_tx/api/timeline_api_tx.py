from PySide2 import QtCore
from rpa.api.timeline_api import TimelineApi as _TimelineApi
from itview.skin.rpa_tx.attr_utils import make_default_methods


class TimelineApiTx(QtCore.QObject):
    SIG_FRAME_CHANGED = QtCore.Signal(int) # frame
    SIG_PLAY_STATUS_CHANGED = QtCore.Signal(bool, bool) # playing, forward

    def __init__(self, rpc):
        super().__init__()
        self.__rpc = rpc
        make_default_methods(_TimelineApi, "timeline_api", self)

    @property
    def _rpc(self):
        return self.__rpc

    def goto_frame(self, frame:int):
        return self.__rpc.rpc.rpa_rx.timeline_api.goto_frame(frame)
