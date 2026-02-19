try:
    from PySide2 import QtCore
except:
    from PySide6 import QtCore
import json
from itview.attr_utils import make_attrs
from itview.core.rpa_rx.attr_utils import is_valid


class SessionApiRx(QtCore.QObject):
    def __init__(self, rpa, rpc):
        super().__init__()
        self.__rpa = rpa
        self.__rpc = rpc

        self.__rpa.SIG_PLAYLISTS_MODIFIED.connect(
            lambda : self.__rpc.rpc.rpa_tx.session_api.\
                SIG_PLAYLISTS_MODIFIED.emit())

        self.__rpa.SIG_PLAYLIST_MODIFIED.connect(
            lambda id: self.__rpc.rpc.rpa_tx.session_api.\
                SIG_PLAYLIST_MODIFIED.emit(id))

        self.__rpa.SIG_FG_PLAYLIST_CHANGED.connect(
            lambda id : self.__rpc.rpc.rpa_tx.session_api.\
                SIG_FG_PLAYLIST_CHANGED.emit(id))

        self.__rpa.SIG_BG_PLAYLIST_CHANGED.connect(
            lambda id: self.__rpc.rpc.rpa_tx.session_api.\
                SIG_BG_PLAYLIST_CHANGED.emit(id))

        self.__rpa.SIG_CURRENT_CLIP_CHANGED.connect(
            lambda id : self.__rpc.rpc.rpa_tx.session_api.\
                SIG_CURRENT_CLIP_CHANGED.emit(id))

        self.__rpa.SIG_ATTR_VALUES_CHANGED.connect(
            lambda attr_values : self.__rpc.rpc.rpa_tx.session_api.\
                SIG_ATTR_VALUES_CHANGED.emit(attr_values))

        make_attrs(self.__rpa, self, is_valid)
