from PySide2 import QtCore
from rpa.api.annotation_api import AnnotationApi as _AnnotationApi
from itview.skin.rpa_tx.attr_utils import make_default_methods
from rpa.session_state.annotations import Stroke


class AnnotationApiTx(QtCore.QObject):
    SIG_MODIFIED = QtCore.Signal()

    def __init__(self, rpc):
        super().__init__()
        self.__rpc = rpc
        make_default_methods(_AnnotationApi, "annotation_api", self)

    @property
    def _rpc(self):
        return self.__rpc

    def append_transient_point(self, clip_id, frame, token, stroke_point, is_line=False):
        return self.__rpc.rpc.rpa_rx.annotation_api.append_transient_point(
            clip_id, frame, token, stroke_point.__getstate__(), is_line)

    def get_transient_strokes(self, clip_id, frame, token):
        res = self.__rpc.rpa_rx.annotation_api.get_transient_strokes(
            clip_id, frame, token)
        return [Stroke().__setstate__(s) for s in res]

    def append_strokes(self, clip_id, frame, strokes):
        return self.__rpc.rpa_rx.annotation_api.append_strokes(
            clip_id, frame, [stroke.__getstate__() for stroke in strokes])

    def set_text(self, clip_id, frame, text):
        return self.__rpc.rpa_rx.annotation_api.set_text(
            clip_id, frame, text.__getstate__())

    def append_texts(self, clip_id, frame, texts):
        return self.__rpc.rpa_rx.annotation_api.append_texts(
            clip_id, frame, [text.__getstate__() for text in texts])

    def set_rw_annotations(self, annotations):
        out = {}
        for clip, frame_annotations in annotations.items():
            for frame, annotation in frame_annotations.items():
                out.setdefault(clip, {})[frame] = annotation.__getstate__()
        return self.__rpc.rpa_rx.annotation_api.set_rw_annotations(out)

    def set_ro_annotations(self, annotations):
        out = {}
        for clip, frame_annotations in annotations.items():
            for frame, annotations in frame_annotations.items():
                out.setdefault(clip, {})[frame] = \
                    [annotation.__getstate__() for annotation in annotations]
        return self.__rpc.rpa_rx.annotation_api.set_ro_annotations(out)

    def set_laser_pointer(self, id, point, color):
        return self.__rpc.rpc.rpa_rx.annotation_api.set_laser_pointer(
            id, point.__getstate__(), color.__getstate__())

    def set_pointer(self, stroke_point):
        stroke_point = None if stroke_point is None else stroke_point.__getstate__()
        return self.__rpc.rpc.rpa_rx.annotation_api.set_pointer(stroke_point)
