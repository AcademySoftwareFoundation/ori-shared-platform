from rv import rvtypes
from timeline_api import TimelineApi
from color_corrector_api import ColorCorrectorApi
from mapper import Mapper
from rv_connector import RvConnector
from review_plugin_api.api.review_plugin_api import ReviewPluginApi


class ReviewPluginApiMode(rvtypes.MinorMode):

    def __init__(self):
        rvtypes.MinorMode.__init__(self)

        self.__color_corrector_api = ColorCorrectorApi.get_instance()
        self.__timeline_api = TimelineApi.get_instance()

        review_plugin_api = ReviewPluginApi()
        RvConnector(review_plugin_api).connect()
        mapper = Mapper.get_instance()
        mapper.set_review_plugin_api(review_plugin_api)

        self.init(
            "ReviewPluginApiMode",
            [
                ("frame-changed", self.__frame_changed, ""),
                ("play-start", self.__play_start, ""),
                ("play-stop", self.__play_stop, ""),
                ("source-group-complete", self.__source_group_complete, ""),
                ("range-changed", self.__range_changed, ""),
                ("pre-render", lambda event: self.__color_corrector_api.pre_render(), ""),
                ("post-render", lambda event: self.__color_corrector_api.post_render(), ""),
            ],
            []
        )

    def render(self, event):
        self.__color_corrector_api.render()

    def __frame_changed(self, event):
        event.reject()
        self.__timeline_api.emit_frame_changed()

    def __play_start(self, event):
        event.reject()
        self.__timeline_api.emit_play_status_changed()

    def __play_stop(self, event):
        event.reject()
        self.__timeline_api.emit_play_status_changed()

    def __source_group_complete(self, event):
        event.reject()
        self.__timeline_api.emit_new_media_added()

    def __range_changed(self, event):
        event.reject()
        self.__timeline_api.emit_frame_count_changed()

    def __pre_render(self, event):
        event.reject()
        self.__color_corrector_api.pre_render()

    def render(self, event):
        self.__color_corrector_api.render()

    def __post_render(self, event):
        event.reject()
        self.__color_corrector_api.post_render()


def createMode():
    return ReviewPluginApiMode()
