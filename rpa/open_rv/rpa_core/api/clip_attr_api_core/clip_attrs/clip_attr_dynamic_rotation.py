from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands as rvc


class ClipAttrDynamicRotation:

    @property
    def id_(self)->str:
        return "dynamic_rotation"

    @property
    def name(self)->str:
        return "Dynamic Rotation"

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
                f"{source_group}_secondary_transform.transform.rotate")[0]
        return value

    def _set_value(self, source_group:str, value:float):
        if rvc.nodeExists(f"{source_group}_secondary_transform"):
            current_value = rvc.getFloatProperty(
            f"{source_group}_secondary_transform.transform.rotate")[0]
            if current_value != value:
                rvc.setFloatProperty(
                    f"{source_group}_secondary_transform.transform.rotate", [value])
                return True
        return False


ClipAttrApiCore.get_instance()._add_attr(ClipAttrDynamicRotation())
