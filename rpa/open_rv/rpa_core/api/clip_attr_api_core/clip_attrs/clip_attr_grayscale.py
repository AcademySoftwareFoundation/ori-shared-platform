from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrGrayscale:

    @property
    def id_(self)->str:
        return "grayscale"

    @property
    def name(self)->str:
        return "Grayscale"

    @property
    def data_type(self):
        return "bool"

    @property
    def is_read_only(self):
        return False

    @property
    def is_keyable(self):
        return False

    @property
    def default_value(self):
        return False

    def set_value(self, source_group:str, value:bool)->bool:
        prop = f"{source_group}_colorPipeline_0.color.saturation"
        if commands.propertyExists(prop):
            commands.setFloatProperty(prop, [0.0 if value else 1.0])
        return True

    def get_value(self, source_group:str)->bool:
        prop = f"{source_group}_colorPipeline_0.color.saturation"
        if not commands.propertyExists(prop):
            return False
        value = commands.getFloatProperty(prop)[0]
        return value == 0.0


ClipAttrApiCore.get_instance()._add_attr(ClipAttrGrayscale())
