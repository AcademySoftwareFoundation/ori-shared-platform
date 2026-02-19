from PySide2 import QtCore
from itview.skin.rpa_skin.api.session_api_skin import SessionApiSkin
from itview.skin.rpa_skin.api.timeline_api_skin import TimelineApiSkin
from itview.skin.rpa_skin.api.annotation_api_skin import AnnotationApiSkin
from itview.skin.rpa_skin.api.color_api_skin import ColorApiSkin
from itview.skin.rpa_skin.api.viewport_api_skin import ViewportApiSkin


class RpaSkin(QtCore.QObject):

    def __init__(self, rpa_tx, session):
        super().__init__()
        self.__rpa_tx = rpa_tx

        self.__session_api = \
            SessionApiSkin(self.__rpa_tx.session_api, session)
        self.__timeline_api = \
            TimelineApiSkin(self.__rpa_tx.timeline_api, self.__session_api, session)
        self.__color_api = \
            ColorApiSkin(self.__rpa_tx.color_api, session)
        self.__annotation_api = \
            AnnotationApiSkin(self.__rpa_tx.annotation_api, session)
        self.__viewport_api = ViewportApiSkin(
            self.__rpa_tx.viewport_api, session)

        self.__session_api._set_timeline_api(self.__timeline_api)

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
