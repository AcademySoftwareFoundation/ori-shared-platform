from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrMediaLength:

    @property
    def id_(self)->str:
        return "media_length"

    @property
    def name(self)->str:
        return "Media Length"

    @property
    def data_type(self):
        return "int"

    @property
    def is_read_only(self):
        return True

    @property
    def is_keyable(self):
        return False

    @property
    def default_value(self):
        return 0

    def get_value(self, source_group:str)->int:
        media_info = commands.sourceMediaInfo(f"{source_group}_source")
        start_frame = media_info.get("startFrame")
        end_frame = media_info.get("endFrame")
        media_length = end_frame - start_frame + 1
        return media_length


ClipAttrApiCore.get_instance()._add_attr(ClipAttrMediaLength())
