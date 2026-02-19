"""Color corrector module."""
from PySide2 import QtCore

from rpa.api.color_api import ColorApi as _ColorApi
from itview.skin.rpa_tx.attr_utils import make_default_methods


class ColorApiTx(QtCore.QObject):

    SIG_CCS_MODIFIED = QtCore.Signal(str, object) # clip_id, frame
    SIG_CC_MODIFIED = QtCore.Signal(str, str) # clip_id, cc_id
    SIG_CC_NODE_MODIFIED = QtCore.Signal(str, str, int) # clip_id, cc_id, node_index

    def __init__(self, rpc):
        super().__init__()
        self.__rpc = rpc
        make_default_methods(
            _ColorApi, "color_api", self)

    @property
    def _rpc(self):
        return self.__rpc

    def append_nodes(self, clip_id, cc_id, nodes):
        return self.__rpc.rpa_rx.color_api.append_nodes(
            clip_id, cc_id,
            [node.__getstate__() for node in nodes])

    def set_ro_ccs(self, ro_ccs):
        out = {}
        for clip_id, ccs in ro_ccs.items():
            for frame, cc in ccs:
                out.setdefault(clip_id, []).append(
                    (frame,  cc.__getstate__()))
        return self.__rpc.rpa_rx.color_api.set_ro_ccs(out)

    def set_frame_ro_ccs(self, clip_id, frame, ccs):
        out = [cc.__getstate__() for cc in ccs]
        return self.__rpc.rpa_rx.color_api.set_frame_ro_ccs(clip_id, frame, out)

    def set_rw_ccs(self, rw_ccs):
        out = {}
        for clip_id, ccs in rw_ccs.items():
            for frame, cc in ccs:
                out.setdefault(clip_id, []).append(
                    (frame,  cc.__getstate__()))
        return self.__rpc.rpa_rx.color_api.set_rw_ccs(out)

    def update_frame_rw_ccs(self, clip_id, frame, ccs):
        out = [cc.__getstate__() for cc in ccs]
        return self.__rpc.rpa_rx.color_api.update_frame_rw_ccs(clip_id, frame, out)

    def set_transient_points(self, clip_id, cc_id, token, points):
        return self.__rpc.rpc.rpa_rx.color_api.set_transient_points(
            clip_id, cc_id, token, points)

    def append_transient_points(self, clip_id, cc_id, token, points):
        return self.__rpc.rpc.rpa_rx.color_api.append_transient_points(
            clip_id, cc_id, token, points)
