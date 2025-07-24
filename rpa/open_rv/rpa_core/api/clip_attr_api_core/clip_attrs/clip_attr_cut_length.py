import numpy as np
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrCutLength:

    @property
    def id_(self)->str:
        return "cut_length"

    @property
    def name(self)->str:
        return "Cut Length"

    @property
    def data_type(self):
        return "int"

    @property
    def is_read_only(self):
        return True

    @property
    def is_keyable(self):
        return False

    @property
    def default_value(self):
        return 0

    def get_value(self, source_group:str)->str:
        smi = commands.sourceMediaInfo(f"{source_group}_source")
        cut_in = commands.getIntProperty(f"{source_group}_source.cut.in")[0]
        cut_out = commands.getIntProperty(f"{source_group}_source.cut.out")[0]
        cut_in = smi.get("startFrame") if cut_in == (np.iinfo(np.int32).max * -1) else cut_in
        cut_out = smi.get("endFrame") if cut_out == (np.iinfo(np.int32).max) else cut_out

        cut_length = cut_out - cut_in + 1
        return cut_length


ClipAttrApiCore.get_instance()._add_attr(ClipAttrCutLength())
