"""
RPA
===

Interface to access all RPA API modules.
"""

from rpa.api.session_api import SessionApi
from rpa.api.annotation_api import AnnotationApi
from rpa.api.timeline_api import TimelineApi
from rpa.api.color_api import ColorApi
from rpa.api.viewport_api import ViewportApi
from rpa.delegate_mngr import DelegateMngr
import uuid


class Rpa:

    def __init__(self, config_api, logger_api):
        super().__init__()
        self.__config_api = config_api
        self.__logger_api = logger_api

        self.__session_api = SessionApi(self.__logger_api)
        self.__annotation_api = AnnotationApi(self.__logger_api)
        self.__timeline_api = TimelineApi(self.__logger_api)
        self.__color_api = ColorApi(self.__logger_api)
        self.__viewport_api = ViewportApi(self.__logger_api)

        self.__session_id = uuid.uuid4().hex
        self.__delegate_mngr = DelegateMngr(self.__logger_api)

    @property
    def _delegate_mngr(self):
        return self.__delegate_mngr

    @property
    def session_id(self):
        return self.__session_id

    @property
    def session_api(self):
        return self.__session_api

    @property
    def config_api(self):
        return self.__config_api

    @property
    def logger_api(self):
        return self.__logger_api

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

    def close(self):
        self.__delegate_mngr.call(self.close)
