from PySide2 import QtCore
from itview.skin.rpa_tx.api.session_api_tx import SessionApiTx
from itview.skin.rpa_tx.api.timeline_api_tx import TimelineApiTx
from itview.skin.rpa_tx.api.annotation_api_tx import AnnotationApiTx
from itview.skin.rpa_tx.api.color_api_tx import ColorApiTx
from itview.skin.rpa_tx.api.viewport_api_tx import ViewportApiTx


class RpaTx(QtCore.QObject):

    def __init__(self, rpc):
        super().__init__()
        self.__rpc = rpc

        self.__session_api = SessionApiTx(self.__rpc)
        self.__timeline_api = TimelineApiTx(self.__rpc)
        self.__annotation_api = AnnotationApiTx(self.__rpc)
        self.__color_api = ColorApiTx(self.__rpc)
        self.__viewport_api = ViewportApiTx(self.__rpc)

    @property
    def session_api(self):
        return self.__session_api

    @property
    def timeline_api(self):
        return self.__timeline_api

    @property
    def color_api(self):
        return self.__color_api

    @property
    def annotation_api(self):
        return self.__annotation_api

    @property
    def viewport_api(self):
        return self.__viewport_api
