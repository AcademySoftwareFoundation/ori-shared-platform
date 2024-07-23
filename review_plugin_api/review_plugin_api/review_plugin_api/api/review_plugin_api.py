from review_plugin_api.api.timeline_api import TimelineApi
from review_plugin_api.api.color_corrector_api import ColorCorrectorApi
from review_plugin_api.api._delegate_mngr import DelegateMngr


class ReviewPluginApi:

    def __init__(self):
        super().__init__()

        self.__timeline_api = TimelineApi()
        self.__color_corrector_api = ColorCorrectorApi()

        self.__delegate_mngr = DelegateMngr()

    @property
    def delegate_mngr(self):
        return self.__delegate_mngr

    @property
    def timeline_api(self):
        return self.__timeline_api

    @property
    def color_corrector_api(self):
        return self.__color_corrector_api
