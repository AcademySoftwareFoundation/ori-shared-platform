import math
import time
from collections import deque
try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore
from OpenGL import GL

from rv import commands as rvc
from rv import extra_commands as rve

from rpa.session_state.annotations import \
    Stroke, StrokeMode, StrokeBrush, Text
from rpa.session_state.utils import Color, Point, itview_to_screen, image_to_itview
from rpa.open_rv.rpa_core.api.utils import \
    rv_to_image, rv_to_itview, image_to_rv, itview_to_rv
from rpa.open_rv.rpa_core.api import prop_util


LASER_POINT_DELAY = 1.0
LASER_TRAIL_DELAY = 0.05
LASER_TRAIL_MAX_POINTS = 1000


class AnnotationApiCore(QtCore.QObject):
    SIG_MODIFIED = QtCore.Signal()

    PRG_ANNO_LOADING_STARTED = QtCore.Signal(int)
    PRG_ANNO_LOADED = QtCore.Signal(int, int)
    PRG_ANNO_LOADING_COMPLETED = QtCore.Signal()

    PRG_ANNO_DELETION_STARTED = QtCore.Signal(int)
    PRG_ANNO_DELETED = QtCore.Signal(int, int)
    PRG_ANNO_DELETION_COMPLETED = QtCore.Signal()

    def __init__(self, session):
        super().__init__()
        self.__session = session
        self.__laser_point = {}
        self.__laser_trail = deque(maxlen=LASER_TRAIL_MAX_POINTS)
        self.__laser_timer = QtCore.QTimer(self)
        self.__laser_timer.setSingleShot(True)
        self.__laser_timer.timeout.connect(lambda: rvc.redraw())
        self.__pen_stroke_point = None

    def _update_visibility(self, clip_id=None):
        is_visible = self.__session.viewport.feedback.is_visible
        if clip_id:
            _, paint_node = self.__get_source_and_paint_node(clip_id)
            prop = f"{paint_node}.paint.show"
            if not rvc.propertyExists(prop): return
            prop_util.set_property(prop, [is_visible])
            return
        paint_nodes = self.__find_paint_nodes()
        for paint_node in paint_nodes:
            prop = f"{paint_node}.paint.show"
            if not rvc.propertyExists(prop): continue
            prop_util.set_property(prop, [is_visible])

    def append_transient_point(self, clip_id, frame, token, stroke_point, is_line=False):
        source_node, paint_node = self.__get_source_and_paint_node(clip_id)
        if None in (source_node, paint_node):
            return False
        smi = rvc.sourceMediaInfo(source_node)
        width = smi["width"]
        height = smi["height"]
        name = self.__get_transient_stroke_name(paint_node, frame, token, True)
        prop_util.set_property(f"{paint_node}.{name}.width", [image_to_rv(width, height, stroke_point.width)])
        prop_util.set_property(f"{paint_node}.{name}.color", [stroke_point.color.__getstate__()])
        prop_util.set_property(f"{paint_node}.{name}.brush", [stroke_point.brush])
        prop_util.set_property(f"{paint_node}.{name}.mode", [stroke_point.mode])
        prop = f"{paint_node}.{name}.points"
        point = itview_to_rv(width, height, *(stroke_point.point.__getstate__()))
        if is_line:
            if rvc.propertyExists(prop):
                points = prop_util.get_property(prop)
                rvc.deleteProperty(prop)
                prop_util.set_property(prop, [points[0], point])
            else:
                prop_util.set_property(prop, [point])
        else:
            prop_util.append_property(prop, [point])
        if name not in prop_util.get_property(f"{paint_node}.frame:{frame}.order"):
            prop_util.append_property(f"{paint_node}.frame:{frame}.order", [name])
        return True

    def get_transient_stroke(self, clip_id, frame, token):
        source_node, paint_node = self.__get_source_and_paint_node(clip_id)
        if None in (source_node, paint_node):
            return None
        name = self.__get_transient_stroke_name(paint_node, frame, token)
        if name is None:
            return None
        smi = rvc.sourceMediaInfo(source_node)
        width = smi["width"]
        height = smi["height"]
        return Stroke(
            mode=StrokeMode(prop_util.get_property(f"{paint_node}.{name}.mode")[0]),
            brush=StrokeBrush(prop_util.get_property(f"{paint_node}.{name}.brush")[0]),
            width=rv_to_image(width, height, prop_util.get_property(f"{paint_node}.{name}.width")[0]),
            color=Color(*prop_util.get_property(f"{paint_node}.{name}.color")[0]),
            points=[Point(*rv_to_itview(width, height, *point)) for point in prop_util.get_property(f"{paint_node}.{name}.points")]
        )

    def delete_transient_points(self, clip_id, frame, token):
        source_node, paint_node = self.__get_source_and_paint_node(clip_id)
        if None in (source_node, paint_node):
            return False
        names = []
        transient_token = f":transient:{token}"
        for name in prop_util.get_property(f"{paint_node}.frame:{frame}.order"):
            if transient_token in name:
                prop_util.delete_property(f"{paint_node}.{name}.width")
                prop_util.delete_property(f"{paint_node}.{name}.color")
                prop_util.delete_property(f"{paint_node}.{name}.brush")
                prop_util.delete_property(f"{paint_node}.{name}.mode")
                prop_util.delete_property(f"{paint_node}.{name}.points")
            else:
                names.append(name)
        prop_util.set_property(f"{paint_node}.frame:{frame}.order", names)
        rvc.redraw()
        return True

    def append_strokes(self, clip_id, frame, strokes):
        if not strokes: return False
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.annotations.append_strokes(frame, strokes)
        annotation = clip.annotations.get_rw_annotation(frame)
        self.__append_rw_annotations(clip_id, frame, annotation.creator, strokes)
        self.SIG_MODIFIED.emit()
        return True

    def set_text(self, clip_id, frame, text):
        source_node, paint_node = self.__get_source_and_paint_node(clip_id)
        if source_node is None: return False
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        text = clip.annotations.set_text(frame, text)

        rv_name = text.get_custom_attr("rv_text")
        if rv_name: self.__set_text_properties(source_node, paint_node, text)
        else:
            annotation = clip.annotations.get_rw_annotation(frame)
            if annotation: creator_name = annotation.creator
            else: creator_name = "not_available"
            self.__append_rw_annotations(
                clip_id, frame, creator_name, [text])

        self.SIG_MODIFIED.emit()
        return True

    def append_texts(self, clip_id, frame, texts):
        if not texts: return False
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.annotations.append_texts(frame, texts)
        annotation = clip.annotations.get_rw_annotation(frame)
        self.__append_rw_annotations(clip_id, frame, annotation.creator, texts)
        self.SIG_MODIFIED.emit()
        return True

    def get_ro_annotations(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.annotations.get_ro_annotations(frame)

    def set_ro_annotations(self, ro_annotations):
        total_clips = len(ro_annotations.keys())
        self.PRG_ANNO_LOADING_STARTED.emit(total_clips)
        count = 0
        for clip_id, frame_annotations in ro_annotations.items():
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            count = count + 1
            source_node, _ = self.__get_source_and_paint_node(clip_id)
            _, paint_node = self.__get_stack_and_paint_node(clip_id)
            for frame, annotations in frame_annotations.items():
                clip.annotations.set_ro_annotations(frame, annotations)
                seq_frame = prop_util.convert_frame(frame, source_node)
                self.__redraw_annotations(source_node, paint_node, seq_frame, annotations)
            self.PRG_ANNO_LOADED.emit(count, total_clips)
        self.PRG_ANNO_LOADING_COMPLETED.emit()
        self.SIG_MODIFIED.emit()
        return True

    def delete_ro_annotations(self, clips):
        self.PRG_ANNO_DELETION_STARTED.emit(len(clips))
        for index, clip_id in enumerate(clips):
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            _, paint_node = self.__get_stack_and_paint_node(clip_id)
            source_node, _ = self.__get_source_and_paint_node(clip_id)
            if source_node is None: continue
            for frame in clip.annotations.get_ro_frames():
                frame = prop_util.convert_frame(frame, source_node)
                self.__delete_all_annotations(paint_node, frame)
            clip.annotations.delete_ro()
            self.PRG_ANNO_DELETED.emit(index+1, len(clips))
        self.PRG_ANNO_DELETION_COMPLETED.emit()
        self.SIG_MODIFIED.emit()
        return True

    def get_ro_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.annotations.get_ro_frames()

    def set_rw_annotations(self, annotations):
        for clip_id, frame_annotations in annotations.items():
            for frame, annotation in frame_annotations.items():
                clip = self.__session.get_clip(clip_id)
                if not clip: continue
                clip.annotations.set_rw_annotation(frame, annotation)
                self._redraw_rw_annotations(clip_id, frame)
                self.SIG_MODIFIED.emit()
        return True

    def get_rw_annotation(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.annotations.get_rw_annotation(frame)

    def delete_rw_annotation(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.annotations.delete_rw(frame)
        _, paint_node = self.__get_source_and_paint_node(clip_id)
        self.__delete_all_annotations(paint_node, frame)
        self.SIG_MODIFIED.emit()
        return True

    def get_rw_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.annotations.get_rw_frames()

    def clear_frame(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        clip.annotations.clear(frame)
        self._redraw_rw_annotations(clip_id, frame)
        self.SIG_MODIFIED.emit()
        return True

    def undo(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        clip.annotations.undo(frame)
        self._redraw_rw_annotations(clip_id, frame)
        self.SIG_MODIFIED.emit()
        return True

    def redo(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        clip.annotations.redo(frame)
        self._redraw_rw_annotations(clip_id, frame)
        self.SIG_MODIFIED.emit()
        return True

    def set_laser_pointer(self, id, point, color):
        now = time.time()
        record = (id, point, color, now)
        self.__laser_point[id] = record
        self.__laser_trail.appendleft(record)
        self.__laser_timer.start(LASER_POINT_DELAY * 1000.0)
        rvc.redraw()
        return True

    def set_pointer(self, stroke_point):
        self.__pen_stroke_point = stroke_point
        rvc.redraw()
        return True

    def _redraw_ro_annotations(self, clip_id=None):
        """ This method is called on every clip changed. """
        if not clip_id:
            clip_id = self.__session.viewport.current_clip
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        source_node, _ = self.__get_source_and_paint_node(clip_id)
        _, paint_node = self.__get_stack_and_paint_node(clip_id)
        ro_frames = clip.annotations.get_ro_frames()
        if ro_frames:
            annotations = {}
            for frame in ro_frames:
                annotations.setdefault(clip.id, {})[frame] = \
                    clip.annotations.get_ro_annotations(frame)
            self.set_ro_annotations(annotations)
            return
        for frame in ro_frames:
            annotations = clip.annotations.get_ro_annotations(frame)
            annotation_names = []
            for annotation in annotations:
                if not annotation.is_visible: continue
                for annotation in annotation.annotations:
                    if isinstance(annotation, Stroke):
                        if self.__session.viewport.feedback.are_strokes_visible:
                            name = annotation.get_custom_attr("rv_pen")
                            if name: annotation_names.append(name)
                    elif isinstance(annotation, Text):
                        if self.__session.viewport.feedback.are_texts_visible:
                            name = annotation.get_custom_attr("rv_text")
                            if name: annotation_names.append(name)
            frame = prop_util.convert_frame(frame, source_node)
            prop = f"{paint_node}.frame:{frame}.order"
            if not rvc.propertyExists(prop):
                rvc.newProperty(prop, rvc.StringType, len(annotation_names))
            rvc.setStringProperty(prop, annotation_names, True)

    def _redraw_rw_annotations(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if clip is None: return
        annotation = clip.annotations.get_rw_annotation(frame)
        source_node, paint_node = self.__get_source_and_paint_node(clip_id)
        if source_node and annotation:
            self.__redraw_annotations(
                source_node, paint_node, frame, [annotation])
        else:
            self.__delete_all_annotations(paint_node, frame)

    def __append_rw_annotations(self, clip_id, frame, creator, annotations):
        source_node, paint_node = self.__get_source_and_paint_node(clip_id)
        if source_node is None: return

        next_id = prop_util.get_property(f"{paint_node}.paint.nextId")[0]
        annotation_names = []
        for annotation in annotations:
            next_id += 1
            if isinstance(annotation, Stroke):
                name = f"pen:{next_id}:{frame}:{creator}"
                annotation.set_custom_attr("rv_pen", name)
                self.__set_stroke_properties(source_node, paint_node, annotation)
            elif isinstance(annotation, Text):
                name = f"text:{next_id}:{frame}:{creator}"
                annotation.set_custom_attr("rv_text", name)
                self.__set_text_properties(source_node, paint_node, annotation)
            annotation_names.append(name)
            prop_util.set_property(f"{paint_node}.paint.nextId", [next_id])
        prop_util.append_property(f"{paint_node}.frame:{frame}.order", annotation_names)

    def __redraw_annotations(self, source_node, paint_node, frame, annotations):
        self.__delete_all_annotations(paint_node, frame)
        next_id = prop_util.get_property(f"{paint_node}.paint.nextId")[0]
        annotation_names = []
        for annotation in annotations:
            creator = annotation.creator
            if not annotation.is_visible: continue
            for annotation in annotation.annotations:
                if isinstance(annotation, Stroke):
                    if self.__session.viewport.feedback.are_strokes_visible:
                        next_id += 1
                        name = f"pen:{next_id}:{frame}:{creator}"
                        annotation_names.append(name)
                        annotation.set_custom_attr("rv_pen", name)
                        self.__set_stroke_properties(
                            source_node, paint_node, annotation)
                elif isinstance(annotation, Text):
                    if self.__session.viewport.feedback.are_texts_visible:
                        next_id += 1
                        name = f"text:{next_id}:{frame}:{creator}"
                        annotation_names.append(name)
                        annotation.set_custom_attr("rv_text", name)
                        self.__set_text_properties(
                            source_node, paint_node, annotation)
                prop_util.set_property(f"{paint_node}.paint.nextId", [next_id])
        prop_util.append_property(f"{paint_node}.frame:{frame}.order", annotation_names)

    def __set_stroke_properties(self, source_node, paint_node, stroke):
        smi = rvc.sourceMediaInfo(source_node)
        width, height = smi["width"], smi["height"]
        name = stroke.get_custom_attr("rv_pen")
        prop_util.set_property(
                f"{paint_node}.{name}.width",
                [image_to_rv(width, height, stroke.width)])
        prop_util.set_property(
            f"{paint_node}.{name}.color",
            [stroke.color.__getstate__()])
        prop_util.set_property(
            f"{paint_node}.{name}.brush", [stroke.brush])
        prop_util.set_property(
            f"{paint_node}.{name}.mode", [stroke.mode])
        prop_util.set_property(
            f"{paint_node}.{name}.points",
            [itview_to_rv(width, height, *point.__getstate__()) \
                for point in stroke.points])

    def __set_text_properties(self, source_node, paint_node, text):
        smi = rvc.sourceMediaInfo(source_node)
        width, height = smi["width"], smi["height"]
        name = text.get_custom_attr("rv_text")
        prop_util.set_property(
            f"{paint_node}.{name}.text", [text.text])
        prop_util.set_property(
            f"{paint_node}.{name}.color",
            [text.color.__getstate__()])
        prop_util.set_property(
            f"{paint_node}.{name}.position",
            [itview_to_rv(
                width, height,
                *text.position.__getstate__())])
        prop_util.set_property(
            f"{paint_node}.{name}.size",
            [image_to_rv(width, height, text.size)])

    def render(self, event):
        current_clip_id = self.__session.viewport.current_clip
        if current_clip_id is None: return
        self.__render_pen(event)

        sources = rvc.sourcesAtFrame(rvc.frame())
        if len(sources) != 1:
            return
        source = sources[0]

        now = time.time()

        # Remove all the old laser points
        to_delete = set()
        for id, record in self.__laser_point.items():
            if record[3] < now - LASER_POINT_DELAY:
                to_delete.add(id)
        for id in to_delete:
            del self.__laser_point[id]
        # if not self.__laser_point and not self.__rv_active_text.position:
        if not self.__laser_point: return

        # Remove all the old trail points
        while self.__laser_trail and self.__laser_trail[-1][3] < now - LASER_TRAIL_DELAY:
            self.__laser_trail.pop()
        trails = {}
        for record in self.__laser_trail:
            trails.setdefault(record[0], []).append(record)

        radius = 3
        slices = 15
        incr = 2 * math.pi / slices

        smi = rvc.sourceMediaInfo(source)
        geometry = rvc.imageGeometry(source)
        x0, y0 = geometry[0]
        x1, y1 = geometry[2]
        w, h = x1 - x0, y1 - y0

        domain = event.domain()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, domain[0], 0, domain[1], -1000000, +1000000)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE)

        # Draw Line to indicate text position
        # if self.__rv_active_text.position:
        #     GL.glEnable(GL.GL_BLEND)
        #     GL.glLineWidth(float(3))
        #     GL.glColor(1.0, 1.0, 1.0, 1.0)
        #     GL.glBegin(GL.GL_LINES)
        #     GL.glVertex(self.__rv_active_text.position.x, self.__rv_active_text.position.y)
        #     active_text = clip.annotations.active_text
        #     if active_text: text_cursor_size = active_text.text
        #     else: text_cursor_size = 1.0
        #     GL.glVertex(
        #         self.__rv_active_text.position.x,
        #         self.__rv_active_text.position.y + (5 * text_cursor_size))
        #     GL.glEnd()

        # Draw trails for laser point
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_DONT_CARE)
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glLineWidth(float(2 * radius))
        for id, trail in trails.items():
            GL.glBegin(GL.GL_LINE_STRIP)
            count = float(len(trail))
            for order, past in enumerate(trail):
                id, point, color, ts = past
                x, y = point.__getstate__()
                x = x * w + x0
                y = y * h + y0
                r, g, b, a = color.__getstate__()
                GL.glColor4f(r, g, b, 1.0 - order / count)
                GL.glVertex2f(x, y)
            GL.glEnd()
        GL.glLineWidth(1)

        # Draw pointers
        for id, record in self.__laser_point.items():
            id, point, color, ts = record
            x, y = point.__getstate__()
            x = x * w + x0
            y = y * h + y0
            r, g, b, a = color.__getstate__()

            # Outer background circle
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE)
            GL.glBegin(GL.GL_TRIANGLE_FAN)
            GL.glColor4f(r, g, b, 0.04)
            GL.glVertex2f(x, y)
            GL.glColor4f(r, g, b, 0.0)
            for i in range(0, slices + 1):
                angle = incr * i
                dx = math.cos(angle) * radius * 5
                dy = math.sin(angle) * radius * 5
                GL.glVertex2f(x + dx, y + dy)
            GL.glEnd()

            # Flair
            flair = radius * 12
            GL.glBegin(GL.GL_TRIANGLE_FAN)
            GL.glColor4f(r, g, b, 0.05)
            GL.glVertex2f(x, y)
            GL.glColor4f(r, g, b, 0.0)
            GL.glVertex2f(x - radius, y + radius)
            GL.glVertex2f(x - flair, y)
            GL.glVertex2f(x - radius, y - radius)
            GL.glVertex2f(x, y - flair)
            GL.glVertex2f(x + radius, y - radius)
            GL.glVertex2f(x + flair, y)
            GL.glVertex2f(x + radius, y + radius)
            GL.glVertex2f(x, y + flair)
            GL.glVertex2f(x - radius, y + radius)
            GL.glEnd()

            # Inner dark circle
            GL.glBlendFunc(GL.GL_ONE, GL.GL_ZERO)
            GL.glBegin(GL.GL_TRIANGLE_FAN)
            GL.glColor4f(r, g, b, 1.0)
            GL.glVertex2f(x, y)
            GL.glColor4f(r, g, b, 0.4)
            for i in range(0, slices + 1):
                angle = incr * i
                dx = math.cos(angle) * radius
                dy = math.sin(angle) * radius
                GL.glVertex2f(x + dx, y + dy)
            GL.glEnd()

        GL.glDisable(GL.GL_BLEND)

    def __render_pen(self, event):
        if self.__pen_stroke_point is None:
            return

        sources = rvc.sourcesAtFrame(rvc.frame())
        if len(sources) != 1:
            return
        source = sources[0]

        smi = rvc.sourceMediaInfo(source)
        width = smi["width"]
        height = smi["height"]
        geometry = rvc.imageGeometry(source)

        domain = event.domain()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, domain[0], 0, domain[1], -1000000, +1000000)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        stroke_point = self.__pen_stroke_point
        radius = itview_to_screen(geometry, image_to_itview(width, height, stroke_point.width))
        slices = 64
        incr = 2 * math.pi / slices
        x, y = itview_to_screen(geometry, *stroke_point.point.__getstate__())
        r, g, b, a = stroke_point.color.__getstate__()
        is_eraser = stroke_point.mode == StrokeMode.ERASER

        GL.glLineWidth(1)
        if is_eraser:
            GL.glLineStipple(4, 0xAAAA)
            GL.glEnable(GL.GL_LINE_STIPPLE)
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glColor4f(r, g, b, 1.0)
        for i in range(slices):
            angle = incr * i
            dx = math.cos(angle) * radius
            dy = math.sin(angle) * radius
            GL.glVertex2f(x + dx, y + dy)
        GL.glEnd()

        if is_eraser:
            GL.glDisable(GL.GL_LINE_STIPPLE)
        GL.glDisable(GL.GL_BLEND)
        GL.glDisable(GL.GL_LINE_SMOOTH)

    def __find_paint_nodes(self):
        return rvc.nodesOfType("RVPaint")

    def __get_source_and_paint_node(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        source_node = clip.get_custom_attr("rv_source_group")
        if not source_node:
            return None, None
        source_node = f"{source_node}_source"
        paint_node = rve.associatedNode("RVPaint", source_node)
        return source_node, paint_node

    def __get_stack_and_paint_node(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        stack_node = clip.get_custom_attr("rv_stack_group")
        if not stack_node:
            return None, None
        paint_node = rvc.closestNodesOfType("RVPaint", stack_node)
        if not paint_node:
            return None, None
        paint_node = paint_node[0]
        return stack_node, paint_node

    def __delete_all_annotations(self, paint_node, frame):
        for name in prop_util.get_property(f"{paint_node}.frame:{frame}.order"):
            if "pen" in name:
                prop_util.delete_property(f"{paint_node}.{name}.width")
                prop_util.delete_property(f"{paint_node}.{name}.color")
                prop_util.delete_property(f"{paint_node}.{name}.brush")
                prop_util.delete_property(f"{paint_node}.{name}.mode")
                prop_util.delete_property(f"{paint_node}.{name}.points")
            if "text" in name:
                prop_util.delete_property(f"{paint_node}.{name}.text")
                prop_util.delete_property(f"{paint_node}.{name}.color")
                prop_util.delete_property(f"{paint_node}.{name}.position")
                prop_util.delete_property(f"{paint_node}.{name}.size")
            prop_util.delete_property(f"{paint_node}.{name}")
        prop_util.delete_property(f"{paint_node}.frame:{frame}.order")

    def __get_transient_stroke_name(self, paint_node, frame, token, create=False):
        transient_token = f":transient:{token}"
        for name in prop_util.get_property(f"{paint_node}.frame:{frame}.order"):
            if transient_token in name:
                return name
        if not create:
            return None
        next_id = prop_util.get_property(f"{paint_node}.paint.nextId")[0]
        name = f"pen:{next_id}:{frame}:transient:{token}"
        return name
