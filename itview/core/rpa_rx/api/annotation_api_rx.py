try:
    from PySide2 import QtCore
except:
    from PySide6 import QtCore
from itview.attr_utils import make_attrs
from itview.core.rpa_rx.attr_utils import is_valid
from rpa.session_state.annotations import \
    StrokePoint, Stroke, Text, Annotation
from rpa.session_state.utils import Point, Color


class AnnotationApiRx(QtCore.QObject):
    def __init__(self, rpa, rpc):
        super().__init__()
        self.__rpa = rpa
        self.__rpc = rpc
        self.__rpa.SIG_MODIFIED.connect(
            lambda: self.__rpc.rpc.rpa_tx.annotation_api.SIG_MODIFIED.emit())

        make_attrs(self.__rpa, self, is_valid)

    def append_transient_point(self, clip_id, frame, token, stroke_point, is_line=False):
        return self.__rpa.append_transient_point(
            clip_id, frame, token, StrokePoint().__setstate__(stroke_point), is_line)

    def get_transient_strokes(self, clip_id, frame, token):
        res = self.__rpa.get_transient_strokes(
            clip_id, frame, token)
        return [s.__getstate__() for s in res]

    def append_strokes(self, clip_id, frame, strokes):
        return self.__rpa.append_strokes(
            clip_id, frame, [Stroke().__setstate__(stroke) for stroke in strokes])

    def set_text(self, clip_id, frame, text):
        return self.__rpa.set_text(
            clip_id, frame, Text().__setstate__(text))

    def append_texts(self, clip_id, frame, texts):
        return self.__rpa.append_texts(
            clip_id, frame, [Text().__setstate__(text) for text in texts])

    def set_rw_annotations(self, annotations):
        out = {}
        for clip, frame_annotations in annotations.items():
            for frame, annotation in frame_annotations.items():
                out.setdefault(clip, {})[int(frame)] = \
                    Annotation().__setstate__(annotation)
        return self.__rpa.set_rw_annotations(out)

    def set_ro_annotations(self, annotations):
        out = {}
        for clip, frame_annotations in annotations.items():
            for frame, annotations in frame_annotations.items():
                out.setdefault(clip, {})[int(frame)] = \
                    [Annotation().__setstate__(annotation) \
                        for annotation in annotations]
        return self.__rpa.set_ro_annotations(out)

    def set_laser_pointer(self, id, point, color):
        return self.__rpa.set_laser_pointer(
            id, Point().__setstate__(point), Color().__setstate__(color))

    def set_pointer(self, stroke_point):
        stroke_point = None if stroke_point is None else \
            StrokePoint().__setstate__(stroke_point)
        return self.__rpa.set_pointer(stroke_point)
