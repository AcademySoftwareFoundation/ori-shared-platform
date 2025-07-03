from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrFlipY:

    @property
    def id_(self)->str:
        return "flip_y"

    @property
    def name(self)->str:
        return "Flip Y"

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
        commands.setIntProperty(
            f"{source_group}_transform2D.transform.flip", [1 if value else 0])
        return True

    def get_value(self, source_group:str)->bool:
        flipped = commands.getIntProperty(
            f"{source_group}_transform2D.transform.flip")[0]
        return flipped == 1


ClipAttrApiCore.get_instance()._add_attr(ClipAttrFlipY())
