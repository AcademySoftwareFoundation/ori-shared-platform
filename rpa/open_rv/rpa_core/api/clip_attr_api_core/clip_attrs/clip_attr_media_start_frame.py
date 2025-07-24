from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrMediaStartFrame:

    @property
    def id_(self)->str:
        return "media_start_frame"

    @property
    def name(self)->str:
        return "Media Start Frame"

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
        start_frame = commands.sourceMediaInfo(source_name).get("startFrame")
        return start_frame

ClipAttrApiCore.get_instance()._add_attr(ClipAttrMediaStartFrame())
