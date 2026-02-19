from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrMediaPath:

    @property
    def id_(self)->str:
        return "media_path"

    @property
    def name(self)->str:
        return "Media Path"

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

    @property
    def dependent_attr_ids(self):
        return ["audio_fps", "audio_path", "audio_type",
                "media_fps", "media_type", "resolution",
                "media_start_frame", "media_end_frame",
                "media_length", "cut_length", "length_diff"]

    def get_value(self, source_group:str)->str:
        media_movies = commands.getStringProperty(
            f"{source_group}_source.media.movie")
        return media_movies[0]

    def _set_value(self, source_group:str, value:str)->str:
        media_paths = \
            commands.getStringProperty(f"{source_group}_source.media.movie")
        if len(media_paths) > 1:
            video_path, audio_path = media_paths[:2]
            new_media_paths = [value, audio_path]
        else:
            new_media_paths = [value]
        commands.setStringProperty(
            f"{source_group}_source.media.movie", new_media_paths, True)
        return True

ClipAttrApiCore.get_instance()._add_attr(ClipAttrMediaPath())
