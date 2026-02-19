try:
    from PySide2 import QtCore
except:
    from PySide6 import QtCore
from itview.attr_utils import make_attrs
from itview.core.rpa_rx.attr_utils import is_valid


class TimelineApiRx(QtCore.QObject):
    def __init__(self, rpa, rpc):
        super().__init__()
        self.__rpa = rpa
        self.__rpc = rpc

        self.__rpa.SIG_FRAME_CHANGED.connect(
            lambda frame: self.__rpc.rpc.rpa_tx.timeline_api.\
                SIG_FRAME_CHANGED.emit(frame))

        self.__rpa.SIG_PLAY_STATUS_CHANGED.connect(
            lambda is_playing, is_forward : self.__rpc.rpc.rpa_tx.timeline_api.\
                SIG_PLAY_STATUS_CHANGED.emit(is_playing, is_forward))

        make_attrs(self.__rpa, self, is_valid)
