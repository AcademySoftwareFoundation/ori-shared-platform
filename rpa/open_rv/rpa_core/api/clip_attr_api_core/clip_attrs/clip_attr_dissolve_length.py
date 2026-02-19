from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attrs.utils \
    import get_key_in, get_key_out


class ClipAttrDissolveLength:

    @property
    def id_(self)->str:
        return "dissolve_length"

    @property
    def name(self)->str:
        return "Dissolve Length"

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
        return ["dissolve_start"]

    def set_value(self, source_group:str, value:int)->bool:
        if value < 0:
            print("Dissolve length cannot be negative!")
            return False
        if value == 0:
            commands.setIntProperty(f"{source_group}_cross_dissolve.node.active", [0], True)
            commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.startFrame", [float(0)], True)
            commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.numFrames", [float(0)], True)
            return True
        key_in = get_key_in(source_group)
        key_out = get_key_out(source_group)
        if value > key_out - key_in + 1:
            print(f"dissolve length is out of range: {value} is not between {key_in} and {key_out}")
            return False
        commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.numFrames", [float(value)], True)
        # Setup dissolve_start so the dissolve ends at key_out and its length matches
        # the given dissolve length (value), i.e., dissolve_start = key_out - value + 1
        dissolve_start = key_out - value + 1
        # Clamp dissolve_start not to go below key_in
        dissolve_start = max(dissolve_start, key_in)
        commands.setFloatProperty(f"{source_group}_cross_dissolve.parameters.startFrame", [float(float(dissolve_start - key_in + 1))], True)
        commands.setIntProperty(f"{source_group}_cross_dissolve.node.active", [1], True)
        return True

    def get_value(self, source_group:str)->int:
        value = commands.getFloatProperty(f"{source_group}_cross_dissolve.parameters.numFrames")[0]
        return int(value)

ClipAttrApiCore.get_instance()._add_attr(ClipAttrDissolveLength())
