from PySide2 import QtCore
from itview.skin.rpa_skin.attr_utils import make_callables, connect_signals


class AnnotationApiSkin(QtCore.QObject):

    def __init__(self, rpa_tx, session):
        super().__init__()
        self.__rpa_tx = rpa_tx
        self.__session = session
        make_callables(self.__rpa_tx, self)

    def append_transient_point(self, clip_id, frame, token, stroke_point, is_line=False):
        return self.__rpa_tx.append_transient_point(
            clip_id, frame, token, stroke_point, is_line)

    def get_transient_strokes(self, clip_id, frame, token):
        return self.__rpa_tx.get_transient_strokes(clip_id, frame, token)

    def delete_transient_points(self, clip_id, frame, token):
        return self.__rpa_tx.delete_transient_points(clip_id, frame, token)

    def append_strokes(self, clip_id, frame, strokes):
        if not strokes: return
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        clip.annotations.append_strokes(frame, strokes)
        return self.__rpa_tx.append_strokes(clip_id, frame, strokes)

    def set_text(self, clip_id, frame, text):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        clip.annotations.set_text(frame, text)
        return self.__rpa_tx.set_text(clip_id, frame, text)

    def append_texts(self, clip_id, frame, texts):
        if not texts: return
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        clip.annotations.append_texts(frame, texts)
        return self.__rpa_tx.append_texts(clip_id, frame, texts)

    def get_ro_annotations(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.annotations.get_ro_annotations(frame)

    def set_ro_annotations(self, ro_annotations):
        for clip_id, frame_annotations in ro_annotations.items():
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            for frame, annotations in frame_annotations.items():
                clip.annotations.set_ro_annotations(frame, annotations)
        return self.__rpa_tx.set_ro_annotations(ro_annotations)

    def delete_ro_annotations(self, clips):
        for clip_id in clips:
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            clip.annotations.delete_ro()
        return self.__rpa_tx.delete_ro_annotations(clips)

    def get_ro_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.annotations.get_ro_frames()

    def get_ro_note_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.annotations.get_ro_note_frames()

    def set_rw_annotations(self, annotations:dict):
        for clip_id, frame_annotations in annotations.items():
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            for frame, annotation in frame_annotations.items():
                clip.annotations.set_rw_annotation(frame, annotation)
        return self.__rpa_tx.set_rw_annotations(annotations)

    def get_rw_annotation(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.annotations.get_rw_annotation(frame)

    def delete_rw_annotation(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        clip.annotations.delete_rw(frame)
        return self.__rpa_tx.delete_rw_annotation(clip_id, frame)

    def get_rw_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.annotations.get_rw_frames()

    def clear_frame(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        # self.__unset_text_cursor(clip_id, frame)
        clip.annotations.clear(frame)
        return self.__rpa_tx.clear_frame(clip_id, frame)

    def undo(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        # self.__unset_text_cursor(clip_id, frame)
        clip.annotations.undo(frame)
        return self.__rpa_tx.undo(clip_id, frame)

    def redo(self, clip_id, frame):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        # self.__unset_text_cursor(clip_id, frame)
        clip.annotations.redo(frame)
        return self.__rpa_tx.redo(clip_id, frame)

    def set_laser_pointer(self, id, point, color):
        return self.__rpa_tx.set_laser_pointer(id, point, color)

    def set_pointer(self, point):
        return self.__rpa_tx.set_pointer(point)

    # def __unset_text_cursor(self, clip_id, frame):
    #     clip = self.__session.get_clip(clip_id)
    #     if not clip: return
    #     _, text_cursor_position, _ = clip.annotations.get_text_cursor()
    #     if not text_cursor_position: return
    #     clip.annotations.unset_text_cursor(frame)

    def get_annotation_ghosting(self):
        return self.__session.viewport.feedback.annotation_ghosting

    def set_annotation_ghosting(self, value):
        self.__session.viewport.feedback.annotation_ghosting = value
        self.__rpa_tx.set_annotation_ghosting(value)

    def get_annotation_holding(self):
        return self.__session.viewport.feedback.annotation_holding

    def set_annotation_holding(self, value):
        self.__session.viewport.feedback.annotation_holding = value
        self.__rpa_tx.set_annotation_holding(value)
