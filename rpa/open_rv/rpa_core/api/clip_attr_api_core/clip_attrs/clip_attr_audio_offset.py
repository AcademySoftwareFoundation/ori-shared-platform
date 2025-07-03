from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrAudioOffset:

    @property
    def id_(self)->str:
        return "audio_offset"

    @property
    def name(self)->str:
        return "Audio Offset"

    @property
    def data_type(self):
        return "int"

    @property
    def is_read_only(self):
        return False

    @property
    def is_keyable(self):
        return False

    @property
    def default_value(self):
        return 0

    def set_value(self, source_group:str, value:float)->bool:
        fps = commands.getFloatProperty(
            f"{source_group}_source.group.fps")[0]
        if fps == 0.0:
            fps = commands.fps()

        duration = self.__itview_to_rv_conversion(source_group, value, fps)
        commands.setFloatProperty(
            f"{source_group}_source.group.audioOffset", [duration])
        return True

    def get_value(self, source_group:str)->float:
        value = commands.getFloatProperty(
            f"{source_group}_source.group.audioOffset")[0]
        fps = commands.getFloatProperty(
            f"{source_group}_source.group.fps")[0]
        if fps == 0.0:
            fps = commands.fps()

        audio_offset = self.__rv_to_itview_conversion(source_group, value, fps)
        return audio_offset

    def __itview_to_rv_conversion(
        self, source_group:str, value:int, fps:float)->float:
        start_frame = \
            commands.sourceMediaInfo(
                f"{source_group}_source").get("startFrame")
        if value == start_frame:
            return 0.0

        adjusted_value = value - start_frame
        return adjusted_value / fps

    def __rv_to_itview_conversion(
        self, source_group:str, value:float, fps:float)->int:
        start_frame = \
            commands.sourceMediaInfo(
                f"{source_group}_source").get("startFrame")
        if value == 0.0:
            return start_frame

        float_offset = (value * fps)
        int_offset = int(float_offset)
        frac = float_offset - int_offset
        offset = float(int_offset + 1.0) if frac >= 0.5 else float(int_offset)

        return start_frame + offset


ClipAttrApiCore.get_instance()._add_attr(ClipAttrAudioOffset())
