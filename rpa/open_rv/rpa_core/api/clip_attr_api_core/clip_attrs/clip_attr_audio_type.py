from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrAudioType:

    @property
    def id_(self)->str:
        return "audio_type"

    @property
    def name(self)->str:
        return "Audio Type"

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
        source_name = f"{source_group}_source"
        smis = commands.sourceMediaInfoList(source_name)
        src_medias = commands.getStringProperty(
            source_name + ".media.movie")

        audio_path = "N/A"

        if len(smis) == 1 and smis[0].get("hasAudio"):
            audio_path = src_medias[0]
        elif len(smis) == 2:
            has_video = [smi.get("hasVideo", False) for smi in smis]
            has_audio = [smi.get("hasAudio", False) for smi in smis]

            video_count = has_video.count(True)
            audio_count = has_audio.count(True)

            if all(has_audio) or (video_count == 1 and audio_count == 1):
                audio_path = src_medias[1]
            elif all(has_video) and audio_count == 1:
                audio_path = next(
                    (smi.get("file") for smi in smis if smi.get("hasAudio")),
                    audio_path)

        last_dot_pos = audio_path.rfind('.')
        ext = "N/A"
        if last_dot_pos not in (-1, len(audio_path) - 1):
            ext = audio_path[last_dot_pos:]
        return ext


ClipAttrApiCore.get_instance()._add_attr(ClipAttrAudioType())
