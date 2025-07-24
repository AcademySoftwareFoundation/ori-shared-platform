from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrRotation:

    @property
    def id_(self)->str:
        return "rotation"

    @property
    def name(self)->str:
        return "Rotation"

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
        commands.setFloatProperty(
            f"{source_group}_transform2D.transform.rotate", [value])
        return True

    def get_value(self, source_group:str)->float:
        value = commands.getFloatProperty(
            f"{source_group}_transform2D.transform.rotate")[0]
        return value


ClipAttrApiCore.get_instance()._add_attr(ClipAttrRotation())
