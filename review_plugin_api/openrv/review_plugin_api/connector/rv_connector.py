import default_connection_maker
from timeline_api import TimelineApi
from color_corrector_api import ColorCorrectorApi


class RvConnector:

    def __init__(self, review_plugin_api):
        self.__review_plugin_api = review_plugin_api

    def connect(self):
        default_connection_maker.register_core_delegate_func(
            self.__review_plugin_api.color_corrector_api,
            ColorCorrectorApi.get_instance())

        self.__connect_timeline_api()

    def __connect_timeline_api(self):
        review_plugin_api_timeline_api = self.__review_plugin_api.timeline_api
        other_timeline_api = TimelineApi.get_instance()

        other_timeline_api.SIG_FRAME_CHANGED.connect(
            review_plugin_api_timeline_api.SIG_FRAME_CHANGED)
        other_timeline_api.SIG_FRAME_COUNT_CHANGED.connect(
            review_plugin_api_timeline_api.SIG_FRAME_COUNT_CHANGED)
        other_timeline_api.SIG_PLAY_STATUS_CHANGED.connect(
            review_plugin_api_timeline_api.SIG_PLAY_STATUS_CHANGED)
        other_timeline_api.SIG_NEW_MEDIA_ADDED.connect(
            review_plugin_api_timeline_api.SIG_NEW_MEDIA_ADDED)

        default_connection_maker.register_core_delegate_func(
            review_plugin_api_timeline_api, other_timeline_api)
