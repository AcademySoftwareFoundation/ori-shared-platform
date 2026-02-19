from itview.core.rpa_rx.api.session_api_rx import SessionApiRx
from itview.core.rpa_rx.api.timeline_api_rx import TimelineApiRx
from itview.core.rpa_rx.api.annotation_api_rx \
    import AnnotationApiRx
from itview.core.rpa_rx.api.color_api_rx import ColorApiRx
from itview.core.rpa_rx.api.viewport_api_rx import ViewportApiRx


class RpaRx:

    def __init__(self, rpc, rpa):

        self.__rpc = rpc
        self.__rpa = rpa

        self.__session_api = SessionApiRx(
            self.__rpa.session_api, self.__rpc)
        self.__timeline_api = TimelineApiRx(
            self.__rpa.timeline_api, self.__rpc)
        self.__annotation_api = AnnotationApiRx(
            self.__rpa.annotation_api, self.__rpc)
        self.__color_api = ColorApiRx(self.__rpa.color_api, self.__rpc)
        self.__viewport_api = ViewportApiRx(self.__rpa.viewport_api, self.__rpc)

    @property
    def session_api(self):
        return self.__session_api

    @property
    def timeline_api(self):
        return self.__timeline_api

    @property
    def annotation_api(self):
        return self.__annotation_api

    @property
    def color_api(self):
        return self.__color_api

    @property
    def viewport_api(self):
        return self.__viewport_api
