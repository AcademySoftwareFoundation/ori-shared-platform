from rpa.open_rv.rpa_core.api import prop_util
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrTranslateY:

    @property
    def id_(self)->str:
        return "pan_y"

    @property
    def name(self)->str:
        return "Pan Y"

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
        return 0.0

    def set_value(self, source_group:str, value:float)->bool:
        current_value = commands.getFloatProperty(
            f"{source_group}_transform2D.transform.translate")

        h = commands.sourceMediaInfo(
            f"{source_group}_source").get("uncropHeight")
        converted_value = prop_util.convert_translate_itview_to_rv(value, h)

        commands.setFloatProperty(
            f"{source_group}_transform2D.transform.translate",
            [current_value[0], converted_value])
        return True

    def get_value(self, source_group:str)->float:
        value = commands.getFloatProperty(
            f"{source_group}_transform2D.transform.translate")

        h = commands.sourceMediaInfo(f"{source_group}_source").get("uncropHeight")
        converted_value = prop_util.convert_translate_rv_to_itview(value[1], h)
        return converted_value


ClipAttrApiCore.get_instance()._add_attr(ClipAttrTranslateY())
