from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrMediaType:

    @property
    def id_(self)->str:
        return "media_type"

    @property
    def name(self)->str:
        return "Media Type"

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
        media_movie = commands.getStringProperty(
            f"{source_group}_source.media.movie")[0]
        last_dot_pos = media_movie.rfind('.')
        ext = "unknown"
        if last_dot_pos not in (-1, len(media_movie) - 1):
            ext = media_movie[last_dot_pos:]
        return ext


ClipAttrApiCore.get_instance()._add_attr(ClipAttrMediaType())
