try:
    from PySide2 import QtCore
except:
    from PySide6 import QtCore
from itview.attr_utils import make_attrs
from itview.core.rpa_rx.attr_utils import is_valid
from rpa.session_state.utils import Point


class ViewportApiRx(QtCore.QObject):

    def __init__(self, rpa, rpc):
        super().__init__()
        self.__rpa = rpa
        self.__rpc = rpc

        self.__rpa.SIG_CURRENT_CLIP_GEOMETRY_CHANGED.connect(
            lambda geometry: self.__rpc.rpc.rpa_tx.viewport_api.\
                SIG_CURRENT_CLIP_GEOMETRY_CHANGED.emit(geometry))

        make_attrs(self.__rpa, self, is_valid)

    def set_text_cursor(self, position:Point, size:int)-> bool:
        return self.__rpa.set_text_cursor(
            Point().__setstate__(position), size)

    def set_cross_hair_cursor(self, position:Point)-> bool:
        return self.__rpa.set_cross_hair_cursor(
            Point().__setstate__(position) if position else None)
