try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets
from functools import partial
import uuid
from rpa.session_state.annotations import \
    Stroke, StrokeMode, StrokeBrush, StrokePoint, Text, Annotation
from rpa.session_state.utils import Color, Point
import os


TEST_MEDIA_DIR = os.environ.get("TEST_MEDIA_DIR")


class TestAnnotationApi:

    def __init__(self, rpa, parent_widget):
        self.__rpa = rpa
        self.__test_cnt = 0

        self.__view = QtWidgets.QWidget(parent_widget)

        self.__test_iter_cnt = QtWidgets.QLabel(self.__view)
        self.__test_iter_cnt.setText(str(0))
        self.__header = QtWidgets.QLabel(self.__view)
        self.__label = QtWidgets.QLabel(self.__view)
        self.__status = QtWidgets.QLabel(self.__view)
        self.__run_test_btn = QtWidgets.QPushButton(self.__view)
        self.__run_test_btn.setText("Run Test")

        self.__layout = QtWidgets.QVBoxLayout()
        self.__layout.addWidget(self.__test_iter_cnt)
        self.__layout.addWidget(self.__header)
        self.__layout.addWidget(self.__label)
        self.__layout.addWidget(self.__status)
        self.__layout.addWidget(self.__run_test_btn)

        self.__view.setLayout(self.__layout)

        self.__run_test_btn.clicked.connect(self.__run_test)

    @property
    def view(self):
        return self.__view

    def __run_test(self):

        if not TEST_MEDIA_DIR:
            print("++++++++")
            print("Kindly set TEST_MEDIA_DIR environment variable to point to directory with test media!")
            print("The test media folder should have 9 media files that are named one.mp4, two.mp4,... nine.mp4")
            return

        tests = [
            partial(self.__create_clips),
            partial(self.__set_header, "1 Create, Show, Hide and Delete Annotations"),
            partial(self.__set_ro_annotations),
            partial(self.__create_transient_points_1),
            partial(self.__delete_transient_points),
            partial(self.__append_strokes_1),
            partial(self.__set_text_1),
            partial(self.__append_strokes_2),
            partial(self.__set_text_2),
            partial(self.__append_texts_1),
            partial(self.__set_rw_annotation),
            partial(self.__hide_all),
            partial(self.__show_all),
            partial(self.__delete_rw_annotations),
            partial(self.__delete_ro_annotations),
            partial(self.__set_header, "2 Undo Redo Annotations"),
            partial(self.__set_ro_annotations),
            partial(self.__create_transient_points_1),
            partial(self.__undo),
            partial(self.__delete_transient_points),
            partial(self.__append_strokes_1),
            partial(self.__set_text_1),
            partial(self.__append_strokes_2),
            partial(self.__set_text_2),
            partial(self.__append_texts_1),
            partial(self.__undo),
            partial(self.__undo),
            partial(self.__undo),
            partial(self.__undo),
            partial(self.__undo),
            partial(self.__undo),
            partial(self.__undo),
            partial(self.__redo),
            partial(self.__redo),
            partial(self.__redo),
            partial(self.__redo),
            partial(self.__redo),
            partial(self.__redo),
            partial(self.__clear_frame),
            partial(self.__redo),
            partial(self.__undo),
            partial(self.__undo),
            partial(self.__undo),
            partial(self.__undo),
            partial(self.__undo),
            partial(self.__clear_frame),
            partial(self.__redo),
            partial(self.__undo),
            partial(self.__delete_rw_annotations),
            partial(self.__undo),
            partial(self.__delete_ro_annotations),
            partial(self.__set_header, "3 Cut, Copy, Paste"),
            partial(self.__draw_annotations),
            partial(self.__goto_secound_clip),
            partial(self.__delete_rw_annotations),
            partial(self.__goto_first_clip),
            partial(self.__delete_ro_annotations),
            partial(self.__draw_annotations),
            partial(self.__goto_secound_clip),
            partial(self.__delete_rw_annotations),
            partial(self.__goto_first_clip),
            partial(self.__delete_rw_annotations),
            partial(self.__delete_ro_annotations),
            partial(self.__set_header, "4 Frames having annotations"),
            partial(self.__create_annotaions_at_difference_frames),
            partial(self.__set_header, "5 Pointers Test"),
            partial(self.__set_pointers),
        ]
        func = tests[self.__test_cnt]
        func()
        self.__test_cnt += 1
        total_tests = len(tests)
        self.__test_iter_cnt.setText(f"{self.__test_cnt}/{total_tests}")

        if self.__test_cnt == total_tests:
            self.__test_cnt = 0
        else:
            QtCore.QTimer.singleShot(200, self.__run_test)

    def __set_header(self, text):
        self.__header.setText(text)
        self.__label.setText("")

    def __draw_annotations(self):
        self.__label.setText("Draw Annotations")
        self.__set_ro_annotations()
        self.__set_rw_annotation()
        self.__append_strokes_1()
        self.__append_strokes_2()
        self.__append_texts_1()
        self.__set_text_1()
        self.__set_text_2()

    def __cut(self):
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__rpa.annotation_api.cut(cguid, frame)

    def __copy(self):
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__rpa.annotation_api.copy(cguid, frame)

    def __goto_first_clip(self):
        fg_playlist_id = self.__rpa.session_api.get_fg_playlist()
        clip_id = self.__rpa.session_api.get_clips(fg_playlist_id)[0]
        self.__rpa.session_api.set_current_clip(clip_id)

    def __goto_secound_clip(self):
        fg_playlist_id = self.__rpa.session_api.get_fg_playlist()
        clip_id = self.__rpa.session_api.get_clips(fg_playlist_id)[1]
        self.__rpa.session_api.set_current_clip(clip_id)

    def __paste(self):
        clip_id = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__rpa.annotation_api.paste(clip_id, frame)

    def __set_pointers(self):
        value = 0.0
        while value < 1.0:
            self.__rpa.annotation_api.set_laser_pointer("pointer_id_1", Point(value, value), Color(1.0, 0.0, 0.0, 1.0))
            value += 0.1
            QtCore.QThread.msleep(20)

        value = 0.0
        while value < 1.0:
            stroke_point = StrokePoint(
                StrokeMode.PEN, StrokeBrush.GAUSS,
                30.0, 0.0, Color(1.0, 1.0, 0.0, 1.0), Point(value, value))
            self.__rpa.annotation_api.set_pointer(stroke_point)
            value += 0.1
            QtCore.QThread.msleep(100)

    def __create_annotaions_at_difference_frames(self):
        self.__label.setText("Create Annotations at various frames")

        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]

        points = [
            Point(x=0.0, y=0.25),
            Point(x=1.0, y=0.25)]
        s1 = Stroke(
            StrokeMode.PEN, StrokeBrush.CIRCLE, 12.0, 0.0, Color(0.2, 1.0, 0.7, 1.0), points)
        self.__rpa.annotation_api.append_strokes(cguid, frame + 5, [s1])

        t1 = Text("Faith!", Point(0.05, 0.45), Color(0.2, 1.0, 0.7, 1.0))
        self.__rpa.annotation_api.append_texts(cguid, frame + 10, [t1])

        self.__set_ro_annotations()
        self.__set_rw_annotation()

        points = [Point(x=0.0, y=0.25), Point(x=1.0, y=0.25)]
        s1 = Stroke(
            StrokeMode.PEN, StrokeBrush.CIRCLE, 12.0, 0.0, Color(0.2, 1.0, 0.7, 1.0), points)
        t1 = Text("Joy!", Point(0.05, 0.45), Color(0.2, 1.0, 0.7, 1.0))
        self.__rpa.annotation_api.set_ro_annotations(
            {cguid: {frame + 7: [Annotation([s1, t1], "maria-r", -1)]}})

        value = 0.0
        while value < 1.0:
            self.__rpa.annotation_api.append_transient_point(
                cguid, 1008, "local",
                StrokePoint(
                    StrokeMode.PEN, StrokeBrush.CIRCLE,
                    12.0, 0.0, Color(0.0, 0.0, 1.0, 1.0), Point(value, value)))
            value += 0.1
            QtCore.QThread.msleep(20)

        print("RO Frames: ", self.__rpa.annotation_api.get_ro_frames(cguid))
        print("RW Frames: ", self.__rpa.annotation_api.get_rw_frames(cguid))

    def __create_clips(self):
        self.__label.setText("Create Clips")
        self.__rpa.session_api.clear()
        pguid = self.__rpa.session_api.get_fg_playlist()
        paths = [
            os.path.join(TEST_MEDIA_DIR, "one.mp4"),
            os.path.join(TEST_MEDIA_DIR, "two.mp4"),
            os.path.join(TEST_MEDIA_DIR, "three.mp4")
        ]
        self.__rpa.session_api.create_clips(pguid, paths)
        self.__rpa.session_api.set_active_clips(pguid, [])

    def __hide_all(self):
        self.__rpa.viewport_api.set_feedback_visibility(1, False)
        print("Are annotations visible: ", self.__rpa.viewport_api.is_feedback_visible(1))

    def __show_all(self):
        self.__rpa.viewport_api.set_feedback_visibility(1, True)
        print("Are annotations visible: ", self.__rpa.viewport_api.is_feedback_visible(1))

    def __set_ro_annotations(self):
        self.__label.setText("Set RO Annotations")

        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]

        points = [
            Point(x=0.0, y=0.25),
            Point(x=1.0, y=0.25)]
        s1 = Stroke(
            StrokeMode.PEN, StrokeBrush.CIRCLE, 12.0, 0.0, Color(0.2, 1.0, 0.7, 1.0), points)

        points = [
            Point(x=0.05, y=0.0),
            Point(x=0.05, y=1.0)]
        s2 = Stroke(
            StrokeMode.PEN, StrokeBrush.GAUSS, 20.0, 0.0, Color(1.0, 0.70, 0.5, 1.0), points)

        t1 = Text("Cannot undo me!", Point(0.05, 0.45), Color(0.2, 1.0, 0.7, 1.0))
        t2 = Text("Nor can you clear me!", Point(0.05, 0.30), Color(1.0, 0.70, 0.5, 1.0))

        self.__rpa.annotation_api.set_ro_annotations(
            {cguid: {frame: [
                    Annotation([t1, s1], "user-a", -1),
                    Annotation([s2, t2], "user-b", -2)]}})

        self.__rpa.annotation_api.set_ro_annotations(
            {cguid: {frame: [Annotation([t1, s1, t2, s2], "user-a", -1)]}})

    def __set_rw_annotation(self):
        self.__label.setText("Set RW Annotation")

        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]

        points = [
            Point(x=0.0, y=0.90),
            Point(x=1.0, y=0.90)]
        s1 = Stroke(
            StrokeMode.PEN, StrokeBrush.CIRCLE, 12.0, 0.0, Color(0.5, 0.2, 0.8, 1.0), points)

        points = [
            Point(x=0.9, y=0.0),
            Point(x=0.9, y=1.0)]
        s2 = Stroke(
            StrokeMode.PEN, StrokeBrush.GAUSS, 20.0, 0.0, Color(0.3, 0.4, 0.6, 1.0), points)

        t1 = Text("Courage", Point(0.4, 0.25), Color(0.2, 1.0, 0.7, 1.0))
        t2 = Text("Resilient", Point(0.4, 0.10), Color(1.0, 0.70, 0.5, 1.0))

        self.__rpa.annotation_api.set_rw_annotations(
            {cguid: {frame:Annotation([s1, t1, s2, t2], "maria-r",-1)}})

    def __append_texts_1(self):
        self.__label.setText("Append Texts 1")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]

        t1 = Text("Creative", Point(0.6, 0.65), Color(0.2, 1.0, 0.4, 1.0))
        t2 = Text("Pragmatic", Point(0.8, 0.40), Color(1.0, 0.70, 0.5, 1.0))

        self.__rpa.annotation_api.append_texts(cguid, frame, [t1, t2])

    def __create_transient_points_1(self):
        self.__label.setText("Draw Transient Points")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        value = 0.0
        while value < 1.0:
            self.__rpa.annotation_api.append_transient_point(
                cguid, frame, "local",
                StrokePoint(
                    StrokeMode.PEN, StrokeBrush.CIRCLE,
                    12.0, 0.0, Color(0.0, 0.0, 1.0, 1.0), Point(value, value)))
            value += 0.1
            QtCore.QThread.msleep(20)

    def __delete_transient_points(self):
        self.__label.setText("Delete Transient Points")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__rpa.annotation_api.delete_transient_points(cguid, frame, "local")

    def __append_strokes_1(self):
        self.__label.setText("Append Strokes 1")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]

        points = [
            Point(x=0.0, y=0.5),
            Point(x=1.0, y=0.5)]
        s1 = Stroke(
            StrokeMode.PEN, StrokeBrush.CIRCLE, 12.0, 0.0, Color(0.0, 1.0, 0.0, 1.0), points)

        points = [
            Point(x=0.5, y=0.0),
            Point(x=0.5, y=1.0)]
        s2 = Stroke(
            StrokeMode.PEN, StrokeBrush.GAUSS, 20.0, 0.0, Color(1.0, 1.0, 0.0, 1.0), points)

        self.__rpa.annotation_api.append_strokes(cguid, frame, [s1, s2])

    def __append_strokes_2(self):
        self.__label.setText("Append Strokes 2")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]

        points = [
            Point(x=0.0, y=0.75),
            Point(x=1.0, y=0.75)]
        s1 = Stroke(
            StrokeMode.PEN, StrokeBrush.CIRCLE, 20.0, 0.0, Color(0.0, 1.0, 1.0, 1.0), points)

        points = [
            Point(x=0.75, y=0.0),
            Point(x=0.75, y=1.0)]
        s2 = Stroke(
            StrokeMode.PEN, StrokeBrush.GAUSS, 10.0, 0.0, Color(0.5, 1.0, 0.5, 1.0), points)

        self.__rpa.annotation_api.append_strokes(cguid, frame, [s1, s2])

    def __delete_rw_annotations(self):
        self.__label.setText("Delete RW Annotations")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__rpa.annotation_api.delete_rw_annotation(cguid, frame)

    def __delete_ro_annotations(self):
        self.__label.setText("Delete RO Annotations")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__rpa.annotation_api.delete_ro_annotations([cguid])

    def __undo(self):
        self.__label.setText("Undo")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__rpa.annotation_api.undo(cguid, frame)

    def __redo(self):
        self.__label.setText("Redo")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__rpa.annotation_api.redo(cguid, frame)

    def __set_text_1(self):
        self.__label.setText("Set Text 1")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]

        position = Point(0.45, 0.45)
        size = 12
        self.__rpa.viewport_api.set_text_cursor(position, size)
        self.__rpa.annotation_api.set_text(
            cguid, frame, Text("All things are possible!", position, Color(0.2, 1.0, 0.7, 1.0), size))
        self.__rpa.viewport_api.unset_text_cursor()

    def __set_text_2(self):
        self.__label.setText("Set Text 2")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]

        position = Point(0.25, 0.25)
        size = 12
        self.__rpa.viewport_api.set_text_cursor(position, size)
        self.__rpa.annotation_api.set_text(
            cguid, frame, Text("Amazing!", position, Color(1.0, 0.0, 0.0, 1.0), size))
        self.__rpa.viewport_api.unset_text_cursor()

    def __clear_frame(self):
        self.__label.setText("Clear Frame")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__rpa.annotation_api.clear_frame(
            cguid, frame)
