from rpa.open_rv.rpa_core.api import prop_util
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrTranslateX:

    @property
    def id_(self)->str:
        return "pan_x"

    @property
    def name(self)->str:
        return "Pan X"

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
            [converted_value, current_value[1]])
        return True

    def get_value(self, source_group:str)->float:
        value = commands.getFloatProperty(
            f"{source_group}_transform2D.transform.translate")

        h = commands.sourceMediaInfo(
            f"{source_group}_source").get("uncropHeight")
        converted_value = prop_util.convert_translate_rv_to_itview(value[0], h)
        return converted_value


ClipAttrApiCore.get_instance()._add_attr(ClipAttrTranslateX())
