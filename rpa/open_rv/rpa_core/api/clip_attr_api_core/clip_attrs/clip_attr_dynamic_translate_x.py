from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rpa.open_rv.rpa_core.api import prop_util
from rv import commands as rvc


class ClipAttrDynamicTranslateX:

    @property
    def id_(self)->str:
        return "dynamic_translate_x"

    @property
    def name(self)->str:
        return "Dynamic Pan X"

    @property
    def data_type(self):
        return "float"

    @property
    def is_read_only(self):
        return True

    @property
    def is_keyable(self):
        return True

    @property
    def default_value(self):
        return 0.0

    def get_value(self, source_group:str)->float:
        value = self.default_value
        if rvc.nodeExists(f"{source_group}_secondary_transform"):
            value = rvc.getFloatProperty(
                f"{source_group}_secondary_transform.transform.translate")[0]
            h = rvc.sourceMediaInfo(
                f"{source_group}_source").get("uncropHeight")
            value = prop_util.convert_translate_rv_to_itview(value, h)
        return value

    def _set_value(self, source_group:str, value:float):
        h = rvc.sourceMediaInfo(f"{source_group}_source").get("uncropHeight")
        converted_value = prop_util.convert_translate_itview_to_rv(value, h)

        if rvc.nodeExists(f"{source_group}_secondary_transform"):
            current_translate = rvc.getFloatProperty(
            f"{source_group}_secondary_transform.transform.translate")
            current_translate_x = current_translate[0]
            current_translate_y = current_translate[1]
            if converted_value != current_translate_x:
                rvc.setFloatProperty(
                    f"{source_group}_secondary_transform.transform.translate",
                    [converted_value, current_translate_y])
                return True
        return False


ClipAttrApiCore.get_instance()._add_attr(ClipAttrDynamicTranslateX())
