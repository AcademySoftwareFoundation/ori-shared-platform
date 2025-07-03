from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrResolution:

    @property
    def id_(self)->str:
        return "resolution"

    @property
    def name(self)->str:
        return "Resolution"

    @property
    def data_type(self):
        return "str"

    @property
    def is_read_only(self):
        return True

    @property
    def is_keyable(self):
        return False

    @property
    def default_value(self):
        return ""

    def get_value(self, source_group:str)->str:
        media_info = commands.sourceMediaInfo(f"{source_group}_source")
        w = media_info.get("uncropWidth")
        h = media_info.get("uncropHeight")
        return f"{w} x {h}"


ClipAttrApiCore.get_instance()._add_attr(ClipAttrResolution())
