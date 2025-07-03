from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrAudioFps:

    @property
    def id_(self)->str:
        return "audio_fps"

    @property
    def name(self)->str:
        return "Audio FPS"

    @property
    def data_type(self):
        return "float"

    @property
    def is_read_only(self):
        return False

    @property
    def is_keyable(self):
        return False

    @property
    def default_value(self):
        return 24.0

    def set_value(self, source_group:str, value:float)->bool:
        source_name = f"{source_group}_source"
        if not isinstance(value, float):
            value = self.default_value
        commands.setFloatProperty(
            f"{source_name}.group.fps", [value])
        return True

    def get_value(self, source_group:str)->bool:
        source_name = f"{source_group}_source"
        audio_fps = commands.getFloatProperty(
            f"{source_name}.group.fps")[0]

        if audio_fps == 0.0:
            smis = commands.sourceMediaInfoList(f"{source_group}_source")
            for smi in smis:
                if (smi.get("hasAudio") or smi.get("hasVideo")):
                    audio_fps = float(smi.get("fps"))
                    break

        # In order to play media and audio at correct FPS,
        # update playback FPS and source FPS by setting the group.fps once again
        commands.setFloatProperty(
            f"{source_name}.group.fps", [audio_fps])

        return audio_fps


ClipAttrApiCore.get_instance()._add_attr(ClipAttrAudioFps())
