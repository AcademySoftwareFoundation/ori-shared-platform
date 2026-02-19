from PySide2 import QtCore
from rpa.api.viewport_api import ViewportApi as _ViewportApi
from itview.skin.rpa_tx.attr_utils import make_default_methods
from rpa.session_state.utils import Point


class ViewportApiTx(QtCore.QObject):
    SIG_CURRENT_CLIP_GEOMETRY_CHANGED = QtCore.Signal(object) # geometry

    def __init__(self, rpc):
        super().__init__()
        self.__rpc = rpc
        make_default_methods(_ViewportApi, "viewport_api", self)

    @property
    def _rpc(self):
        return self.__rpc

    def set_html_overlay(self, id:str, html_overlay):
        return self.__rpc.rpc.rpa_rx.viewport_api.set_html_overlay(
            id, html_overlay)

    def set_text_cursor(self, position:Point, size:int)-> bool:
        return self.__rpc.rpa_rx.viewport_api.set_text_cursor(
            position.__getstate__(), size)

    def set_cross_hair_cursor(self, position:Point)-> bool:
        return self.__rpc.rpa_rx.viewport_api.set_cross_hair_cursor(
            position.__getstate__() if position else None)

    def set_scale(self, horizontal, vertical):
        return self.__rpc.rpc.rpa_rx.viewport_api.set_scale(
            horizontal, vertical)

    def set_translation(self, dx, dy):
        return self.__rpc.rpc.rpa_rx.viewport_api.set_translation(
            dx, dy)

    def set_rotation(self, angle):
        return self.__rpc.rpc.rpa_rx.viewport_api.set_rotation(
            angle)
