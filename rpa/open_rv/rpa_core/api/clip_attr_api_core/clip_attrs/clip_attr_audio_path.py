from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrAudioPath:

    @property
    def id_(self)->str:
        return "audio_path"

    @property
    def name(self)->str:
        return "Audio Path"

    @property
    def data_type(self):
        return "path"

    @property
    def is_read_only(self):
        return False

    @property
    def is_keyable(self):
        return False

    @property
    def default_value(self):
        return ""

    @property
    def dependent_attr_ids(self):
        return ["audio_type"]

    def set_value(self, source_group:str, value:str):
        if value is None or value == "N/A":
            return False

        source_name = f"{source_group}_source"
        media_paths = \
            commands.getStringProperty(f"{source_group}_source.media.movie")
        if len(media_paths) > 1:
            video_path, audio_path = media_paths[:2]
            new_media_paths = [video_path, value]
        else:
            video_path = media_paths[0]
            new_media_paths = [video_path, value]
        commands.setStringProperty(
            f"{source_group}_source.media.movie", new_media_paths, True)

        smis = commands.sourceMediaInfoList(source_name)
        if len(smis) == 2:
            both_with_video = all(smi.get("hasVideo") for smi in smis)
            both_with_audio = all(smi.get("hasAudio") for smi in smis)

            has_video = [smi.get("hasVideo") for smi in smis]
            has_audio = [smi.get("hasAudio") for smi in smis]

            if both_with_audio and has_video.count(True) == 1:
                commands.setIntProperty(
                    f"{source_name}.group.noMovieAudio", [1])

            if both_with_video and \
                (both_with_audio or has_audio.count(True) == 1):
                commands.setIntProperty(
                    f"{source_name}.group.noMovieAudio", [0])
        
        return True

    def get_value(self, source_group:str)->str:
        audio_path = "N/A"
        source_name = f"{source_group}_source"
        smis = commands.sourceMediaInfoList(source_name)

        if len(smis) == 1 and smis[0].get("hasAudio"):
            audio_path = smis[0].get("file")
        elif len(smis) > 1:
            smis = smis[:2]
            src_media0 = smis[0] # audio file
            src_media1 = smis[1] # video file
            both_with_audio = all(smi.get("hasAudio") for smi in smis)
            has_audio = [smi.get("hasAudio") for smi in smis]

            # if both medias have audio, audio file is used as audio_path
            if both_with_audio:
                audio_path = src_media0.get("file")
            elif has_audio.count(True) == 1:
                audio_path = src_media0.get("file") if \
                    src_media0.get("hasAudio") else src_media1.get("file")

        return audio_path


ClipAttrApiCore.get_instance()._add_attr(ClipAttrAudioPath())
