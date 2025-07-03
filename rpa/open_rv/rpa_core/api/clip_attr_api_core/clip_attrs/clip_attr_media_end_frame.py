from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrMediaEndFrame:

    @property
    def id_(self)->str:
        return "media_end_frame"

    @property
    def name(self)->str:
        return "Media End Frame"

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

    def get_value(self, source_group:str)->str:
        source_name = f"{source_group}_source"
        end_frame = commands.sourceMediaInfo(source_name).get("endFrame")
        return end_frame

ClipAttrApiCore.get_instance()._add_attr(ClipAttrMediaEndFrame())
