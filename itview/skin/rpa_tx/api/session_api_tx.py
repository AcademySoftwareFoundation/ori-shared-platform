from PySide2 import QtCore
from rpa.api.session_api import SessionApi as _SessionApi
from itview.skin.rpa_tx.attr_utils import make_default_methods
import json


class SessionApiTx(QtCore.QObject):
    SIG_PLAYLISTS_MODIFIED = QtCore.Signal()
    SIG_PLAYLIST_MODIFIED = QtCore.Signal(str) # playlist_id
    SIG_FG_PLAYLIST_CHANGED = QtCore.Signal(str) # playlist_id
    SIG_BG_PLAYLIST_CHANGED = QtCore.Signal(object) # playlist_id
    SIG_CURRENT_CLIP_CHANGED = QtCore.Signal(object) # clip_id
    SIG_ATTR_VALUES_CHANGED = QtCore.Signal(list) # attr_values

    def __init__(self, rpc):
        super().__init__()
        self.__rpc = rpc
        make_default_methods(_SessionApi, "session_api", self)

    @property
    def _rpc(self):
        return self.__rpc
