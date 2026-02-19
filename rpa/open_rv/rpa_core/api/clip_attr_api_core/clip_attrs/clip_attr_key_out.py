from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attrs.utils \
    import get_key_in, get_key_out, validate_cross_dissolve, has_frame_edits


class ClipAttrKeyOut:

    @property
    def id_(self)->str:
        return "key_out"

    @property
    def name(self)->str:
        return "Key Out"

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

    @property
    def dependent_attr_ids(self):
        return ["cut_length", "length_diff", "dissolve_start", "dissolve_length"]

    def set_value(self, source_group:str, value:int)->bool:

        if has_frame_edits(source_group):
            print("key_out change is not allowed when frame edits are present")
            return False

        key_in = get_key_in(source_group)
        if value < key_in:
            print("key_out change is not allowed when smaller than key_in")
            return False

        if not isinstance(value, int):
            value = self.default_value

        if not commands.propertyExists(f"{source_group}_source.custom.keyout"):
            commands.newProperty(f"{source_group}_source.custom.keyout", commands.IntType, 1)

        commands.setIntProperty(f"{source_group}_source.custom.keyout", [value], True)

        validate_cross_dissolve(source_group)
        return True

    def get_value(self, source_group:str)->int:
        return get_key_out(source_group)


ClipAttrApiCore.get_instance()._add_attr(ClipAttrKeyOut())
