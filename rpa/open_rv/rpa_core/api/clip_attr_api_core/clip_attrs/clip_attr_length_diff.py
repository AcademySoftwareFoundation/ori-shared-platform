import numpy as np
from rpa.open_rv.rpa_core.api.clip_attr_api_core.clip_attr_api_core \
    import ClipAttrApiCore
from rv import commands


class ClipAttrLengthDiff:

    @property
    def id_(self)->str:
        return "length_diff"

    @property
    def name(self)->str:
        return "Length Diff"

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

    def get_value(self, source_group:str)->int:
        smi = commands.sourceMediaInfo(f"{source_group}_source")
        start_frame = smi.get("startFrame")
        end_frame = smi.get("endFrame")
        media_length = end_frame - start_frame + 1

        cut_in = commands.getIntProperty(f"{source_group}_source.cut.in")[0]
        cut_out = commands.getIntProperty(f"{source_group}_source.cut.out")[0]
        cut_in = start_frame if cut_in == (np.iinfo(np.int32).max * -1) else cut_in
        cut_out = end_frame if cut_out == (np.iinfo(np.int32).max) else cut_out
        cut_length = cut_out - cut_in + 1

        length_diff = media_length - cut_length
        return length_diff


ClipAttrApiCore.get_instance()._add_attr(ClipAttrLengthDiff())
