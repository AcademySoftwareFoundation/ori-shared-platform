from rpa.session_state.session import Session
from rpa.open_rv.rpa_core.api.session_api_core import SessionApiCore
from rpa.open_rv.rpa_core.api.timeline_api_core import TimelineApiCore
from rpa.open_rv.rpa_core.api.annotation_api_core import AnnotationApiCore
from rpa.open_rv.rpa_core.api.color_api_core import ColorApiCore
from rpa.open_rv.rpa_core.api.viewport_api_core import ViewportApiCore


class RpaCore:

    def __init__(self):
        self.__session = Session()
        self.__annotation_api = AnnotationApiCore(self.__session)
        self.__session_api = SessionApiCore(
            self.__session, self.__annotation_api)
        self.__color_api = ColorApiCore(self.__session)
        self.__timeline_api = TimelineApiCore(
            self.__session, self.__session_api)
        self.__viewport_api = ViewportApiCore(
            self.__session, self.__session_api,
            self.__annotation_api, self.__color_api)

        self.__session_api.set_timeline_api(self.__timeline_api)

    @property
    def session(self):
        return self.__session

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
