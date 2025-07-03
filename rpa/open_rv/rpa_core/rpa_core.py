from rpa.session_state.session import Session
from rpa.open_rv.rpa_core.api.session_api_core import SessionApiCore
from rpa.open_rv.rpa_core.api.timeline_api_core import TimelineApiCore
from rpa.open_rv.rpa_core.api.annotation_api_core import AnnotationApiCore
from rpa.open_rv.rpa_core.api.color_api_core import ColorApiCore
from rpa.open_rv.rpa_core.api.viewport_api_core import ViewportApiCore


class RpaCore:

    def __init__(self):
        session = Session()
        self.__annotation_api = AnnotationApiCore(session)
        self.__session_api = SessionApiCore(
            session, self.__annotation_api)
        self.__color_api = ColorApiCore(session)
        self.__timeline_api = TimelineApiCore(
            session, self.__session_api)
        self.__viewport_api = ViewportApiCore(
            session, self.__session_api,
            self.__annotation_api, self.__color_api)

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
