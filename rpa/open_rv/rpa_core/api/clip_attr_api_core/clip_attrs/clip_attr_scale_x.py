from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrScaleX:

    @property
    def id_(self)->str:
        return "scale_x"

    @property
    def name(self)->str:
        return "Zoom X"

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
        return 1.0

    def set_value(self, source_group:str, value:float)->bool:
        current_value = commands.getFloatProperty(
            f"{source_group}_transform2D.transform.scale")
        commands.setFloatProperty(
            f"{source_group}_transform2D.transform.scale", [value, current_value[1]])
        return True

    def get_value(self, source_group:str)->float:
        value = commands.getFloatProperty(
            f"{source_group}_transform2D.transform.scale")[0]
        return value


ClipAttrApiCore.get_instance()._add_attr(ClipAttrScaleX())
