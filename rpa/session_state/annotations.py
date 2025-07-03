import os
from dataclasses import dataclass, field
from typing import Dict, List, Union, Optional
from enum import auto, Enum
from rpa.session_state.utils import Point, Color


@dataclass
class Text:
    text: str = None
    position: Point = field(default_factory=Point)
    color: Color = field(default_factory=Color)
    size: int = 8
    __custom_attrs: dict = field(default_factory=dict)

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def __getstate__(self):
        return {
            "text": self.text,
            "position": self.position.__getstate__(),
            "color": self.color.__getstate__(),
            "size" : self.size,
            "class": self.__class__.__name__
        }

    def __setstate__(self, state):
        self.text = state["text"]
        self.position = Point().__setstate__(state["position"])
        self.color = Color().__setstate__(state["color"])
        self.size = state["size"]
        return self


class StrokeMode(int, Enum):
    PEN = 0
    ERASER = auto()


class StrokeBrush(str, Enum):
    CIRCLE = "circle"
    GAUSS = "gauss"


@dataclass
class StrokePoint:
    mode: StrokeMode = StrokeMode.PEN
    brush: StrokeBrush = StrokeBrush.CIRCLE
    width: float = 0.0
    depth: float = 0.0
    color: Color = field(default_factory=Color)
    point: Point = field(default_factory=Point)

    def __getstate__(self):
        return {
            "mode": self.mode,
            "brush": self.brush,
            "width": self.width,
            "depth": self.depth,
            "color": self.color.__getstate__(),
            "point": self.point.__getstate__()
        }

    def __setstate__(self, state):
        self.mode = state["mode"]
        self.brush = state["brush"]
        self.width = state["width"]
        self.depth = state["depth"]
        self.color = Color().__setstate__(state["color"])
        self.point = Point().__setstate__(state["point"])
        return self


@dataclass
class Stroke:
    mode: StrokeMode = StrokeMode.PEN
    brush: StrokeBrush = StrokeBrush.CIRCLE
    width: float = 0.0
    depth: float = 0.0
    color: Color = field(default_factory=Color)
    points: List[Point] = field(default_factory=list)
    __custom_attrs: dict = field(default_factory=dict)

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def __getitem__(self, index):
        return self.points[index]

    def __len__(self):
        return len(self.points)

    def __iter__(self):
        return iter(self.points)

    def __getstate__(self):
        return {
            "mode": self.mode,
            "brush": self.brush,
            "width": self.width,
            "depth": self.depth,
            "color": self.color.__getstate__(),
            "points": [point.__getstate__() for point in self.points],
            "class": self.__class__.__name__
        }

    def __setstate__(self, state):
        self.mode = state["mode"]
        self.brush = state["brush"]
        self.width = state["width"]
        self.depth = state["depth"]
        self.color = Color().__setstate__(state["color"])
        self.points = [Point().__setstate__(point) for point in state["points"]]
        return self


@dataclass
class Annotation:
    annotations:List[Union[Stroke, Text]] = field(default_factory=list)
    creator: str = os.getenv("USER", "unknown")
    frame: int = -1
    date: int = -1
    is_visible: bool = True
    _clear: List[Union[Stroke, Text]] = field(default_factory=list)
    _redo: List[Union[Stroke, Text]] = field(default_factory=list)
    __custom_attrs: dict = field(default_factory=dict)

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def __getstate__(self):
        return {
            "annotations": [annotation.__getstate__() for annotation in self.annotations],
            "creator": self.creator,
            "date": self.date,
            "frame": self.frame,
            "is_visible": self.is_visible
        }

    def __setstate__(self, state):
        self.annotations.clear()
        for annotation in state["annotations"]:
            if annotation["class"] == "Stroke":
                self.annotations.append(Stroke().__setstate__(annotation))
            elif annotation["class"] == "Text":
                self.annotations.append(Text().__setstate__(annotation))

        self.creator = state["creator"]
        self.date = state["date"]
        self.frame = state["frame"]
        self.is_visible = state["is_visible"]
        return self

    def copy(self):
        return Annotation().__setstate__(self.__getstate__())

    def is_empty(self):
        return not self.annotations


class Annotations:
    """ Defines annotations in a particular clip. """

    def __init__(self):
        self.ro_annos: Dict[int, List[Annotation]] = {}
        self.rw_annos: Dict[int, Annotation] = {}
        self.is_visible: bool = True
        self.__active_text: Optional[Text] = None
        self.__custom_attrs: dict = field(default_factory=dict)

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())

    def __getstate__(self):
        return {
            "ro_annos": {frame:[anno.__getstate__() for anno in annos] for frame, annos in self.ro_annos.items()},
            "rw_annos": {frame:anno.__getstate__() for frame, anno in self.rw_annos.items()},
            "is_visible": self.is_visible
        }

    def __setstate__(self, state):
        self.ro_annos = {frame: [Annotation().__setstate__(anno) for anno in annos] for frame, annos in state["ro_annos"].items()}
        self.rw_annos = {frame: Annotation().__setstate__(anno) for frame, anno in state["rw_annos"].items()}
        self.is_visible = state["is_visible"]
        return self

    def get_ro_annotations(self, frame):
        return self.ro_annos.get(frame, [])

    def get_rw_annotation(self, frame):
        return self.rw_annos.get(frame, None)

    def get_ro_frames(self):
        return list(self.ro_annos.keys())

    def get_rw_frames(self):
        frames = []
        for frame, annotation in self.rw_annos.items():
            if annotation.annotations:
                frames.append(frame)
        return frames

    def set_ro_annotations(self, frame, annotations):
        self.ro_annos[frame] = annotations

    def set_rw_annotation(self, frame, annotation):
        self.rw_annos[frame] = annotation

    def append_strokes(self, frame, strokes):
        annotation = self.rw_annos.get(frame, None)
        if not annotation:
            annotation = Annotation(strokes)
            self.rw_annos[frame] = annotation
        else:
            annotation.annotations.extend(strokes)

    def append_texts(self, frame, texts):
        texts = [Text().__setstate__(text.__getstate__()) for text in texts]
        annotation = self.rw_annos.get(frame, None)
        if not annotation:
            annotation = Annotation(texts)
            self.rw_annos[frame] = annotation
        else:
            annotation.annotations.extend(texts)

    def set_text(self, frame, text:Text):
        annotation = self.rw_annos.get(frame, None)
        if not annotation:
            self.rw_annos[frame] = Annotation([text])
            return text

        text_to_edit = None
        for anno in annotation.annotations:
            if isinstance(anno, Text) and \
            anno.position == text.position:
                text_to_edit = anno
                break

        if text_to_edit:
            text_to_edit.__setstate__(text.__getstate__())
            return text_to_edit
        else:
            annotation.annotations.append(text)
            return text

    def delete_ro(self):
        self.ro_annos = {}

    def delete_rw(self, frame):
        if frame in self.rw_annos:
            del self.rw_annos[frame]

    def clear(self, frame):
        annotation = self.rw_annos.get(frame, None)
        if not annotation: return
        annotation._clear = annotation.annotations[:]
        annotation.annotations = []

    def undo(self, frame):
        annotation = self.rw_annos.get(frame, None)
        if not annotation: return
        if annotation._clear:
            annotation.annotations = annotation._clear[:]
            annotation._clear = []
            return
        if not annotation.annotations: return
        drawing = annotation.annotations.pop(-1)
        annotation._redo.append(drawing)

    def redo(self, frame):
        annotation = self.rw_annos.get(frame, None)
        if not annotation: return
        if annotation._clear:
            annotation.annotations = annotation._clear[:]
            annotation._clear = []
            return
        if not annotation._redo: return
        drawing = annotation._redo.pop(-1)
        annotation.annotations.append(drawing)

    def delete(self):
        pass