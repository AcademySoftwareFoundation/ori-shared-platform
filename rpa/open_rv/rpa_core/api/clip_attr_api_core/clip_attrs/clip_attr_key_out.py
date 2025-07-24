import numpy as np
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


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
        return ["cut_length", "length_diff"]

    def set_value(self, source_group:str, value:int)->bool:
        cut_in = commands.getIntProperty(f"{source_group}_source.cut.in")[0]
        smi = commands.sourceMediaInfo(f'{source_group}_source')
        key_in = smi.get("startFrame") if cut_in == (np.iinfo(np.int32).max * -1) else cut_in

        value = max(value, key_in)
        commands.setIntProperty(f"{source_group}_source.cut.out", [value])
        return True

    def get_value(self, source_group:str)->int:
        cut_out = commands.getIntProperty(f"{source_group}_source.cut.out")[0]
        smi = commands.sourceMediaInfo(f"{source_group}_source")
        key_out = smi.get("endFrame") if cut_out == (np.iinfo(np.int32).max) else cut_out
        return key_out


ClipAttrApiCore.get_instance()._add_attr(ClipAttrKeyOut())
