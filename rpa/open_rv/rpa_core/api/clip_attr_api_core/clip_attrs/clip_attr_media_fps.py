import os
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands

try:
    DEFAULT_FPS = os.environ.get("FPS")
    if not DEFAULT_FPS:
        DEFAULT_FPS = os.environ.get("DEFAULT_FPS")
    DEFAULT_FPS = float(DEFAULT_FPS)
except:
    DEFAULT_FPS = 24.0


class ClipAttrMediaFps:

    @property
    def id_(self)->str:
        return "media_fps"

    @property
    def name(self)->str:
        return "Media FPS"

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

    @property
    def dependent_attr_ids(self):
        return ["audio_fps"]

    def set_value(self, source_group:str, value:float)->bool:
        source_name = f"{source_group}_source"
        if not isinstance(value, float):
            value = self.default_value

        if not commands.propertyExists(f"{source_name}.custom.fps"):
            # create a new property called custom.fps to store Video FPS
            commands.newProperty(f"{source_name}.custom.fps", commands.FloatType, 1)

        commands.setFloatProperty(
                f"{source_name}.custom.fps", [value], True)
        commands.setFPS(value)
        return True

    def get_value(self, source_group:str)->bool:
        source_name = f"{source_group}_source"
        media_fps = commands.sourceMediaInfo(source_name).get("fps")
        if media_fps == 0:
            media_fps = DEFAULT_FPS

        if not commands.propertyExists(f"{source_name}.custom.fps"):
            # create a new property called custom.fps to store Video FPS
            commands.newProperty(f"{source_name}.custom.fps", commands.FloatType, 1)

        initial_value = commands.getFloatProperty(
            f"{source_name}.custom.fps")
        if not initial_value:
            commands.setFloatProperty(
                f"{source_name}.custom.fps", [media_fps], True)

        custom_fps = commands.getFloatProperty(
            f"{source_name}.custom.fps")[0]

        return custom_fps


ClipAttrApiCore.get_instance()._add_attr(ClipAttrMediaFps())
