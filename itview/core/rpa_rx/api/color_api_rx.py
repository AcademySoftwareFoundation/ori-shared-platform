try:
    from PySide2 import QtCore
except:
    from PySide6 import QtCore
from itview.attr_utils import make_attrs
from itview.core.rpa_rx.attr_utils import is_valid
from rpa.session_state.color_corrections import \
    ColorTimer, Grade, ColorCorrection


class ColorApiRx(QtCore.QObject):
    def __init__(self, rpa, rpc):
        super().__init__()
        self.__rpa = rpa
        self.__rpc = rpc

        self.__rpa.SIG_CCS_MODIFIED.connect(
            lambda clip_id, frame: self.__rpc.rpc.rpa_tx.color_api.\
                    SIG_CCS_MODIFIED.emit(clip_id, frame))

        self.__rpa.SIG_CC_MODIFIED.connect(
            lambda clip_id, cc_id: self.__rpc.rpc.rpa_tx.color_api.\
                    SIG_CC_MODIFIED.emit(clip_id, cc_id))

        self.__rpa.SIG_CC_NODE_MODIFIED.connect(
            lambda clip_id, cc_id, node_index: self.__rpc.rpc.rpa_tx.color_api.\
                    SIG_CC_NODE_MODIFIED.emit(clip_id, cc_id, node_index))

        make_attrs(self.__rpa, self, is_valid)

    def append_nodes(self, clip_id, cc_id, nodes):
        new_nodes = []
        for node in nodes:
            if node["class_name"] == "ColorTimer":
                new_nodes.append(ColorTimer().__setstate__(node))
            if node["class_name"] == "Grade":
                new_nodes.append(Grade().__setstate__(node))
        self.__rpa.append_nodes(clip_id, cc_id, new_nodes)

    def set_ro_ccs(self, ro_ccs):
        out = {}
        for clip_id, ccs in ro_ccs.items():
            for frame, cc in ccs:
                out.setdefault(clip_id, []).append(
                    (frame,  ColorCorrection().__setstate__(cc)))
        self.__rpa.set_ro_ccs(out)

    def set_frame_ro_ccs(self, clip_id, frame, ccs):
        out = [ColorCorrection().__setstate__(cc) for cc in ccs]
        self.__rpa.set_frame_ro_ccs(clip_id, frame, out)

    def set_rw_ccs(self, rw_ccs):
        out = {}
        for clip_id, ccs in rw_ccs.items():
            for frame, cc in ccs:
                out.setdefault(clip_id, []).append(
                    (frame,  ColorCorrection().__setstate__(cc)))
        self.__rpa.set_rw_ccs(out)

    def update_frame_rw_ccs(self, clip_id, frame, ccs):
        out = [ColorCorrection().__setstate__(cc) for cc in ccs]
        self.__rpa.update_frame_rw_ccs(clip_id, frame, out)
