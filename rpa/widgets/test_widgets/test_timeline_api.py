import math
try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets
from functools import partial
import os


TEST_MEDIA_DIR = os.environ.get("TEST_MEDIA_DIR")


def __test(comp, name, expected, actual):
    if comp(expected, actual):
        print(f"\x1b[1;32mPassed: {name}\x1b[0m")
    else:
        print(f"\x1b[1;31mFAIL: {name}. Expected: {expected}, but got: {actual}\x1b[0m")

def test_eq(name, expected, actual):
    eq_func = lambda x,y: x==y
    __test(eq_func, name, expected, actual)

def test_range(name, expected, actual):
    if len(expected) != 2:
        raise TypeError("Expected needs to be an iterable of length 2")
    range_func = lambda x,y: x[0] <= y <= x[1]
    __test(range_func, name, expected, actual)

def test_type(name, expected, actual):
    type_func = lambda x, y: y is x
    __test(type_func, name, expected, actual)


class TestTimelineApi:

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

        self.__rpa.timeline_api.SIG_MODIFIED.connect(self.__timeline_modified)

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
            partial(self.__is_playing),
            partial(self.__is_forward),
            partial(self.__set_playing_1),
            partial(self.__set_playing_2),
            partial(self.__set_playing_3),
            partial(self.__goto_frame_1),
            partial(self.__get_frame_range_1),
            partial(self.__get_current_frame_1),
            partial(self.__select_single_clip),
            partial(self.__goto_frame_1),
            partial(self.__get_frame_range_2),
            partial(self.__get_current_frame_1),
            partial(self.__get_volume),
            partial(self.__set_volume),
            partial(self.__toggle_mute_1),
            partial(self.__toggle_mute_2),
            partial(self.__audio_scrubbing_1),
            partial(self.__audio_scrubbing_2),
            partial(self.__set_playback_mode),
            partial(self.__rpa.session_api.clear),
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

    def __timeline_modified(self):
        start_frame, end_frame = self.__rpa.timeline_api.get_frame_range()
        current_frame = self.__rpa.timeline_api.get_current_frame()

    def __get_frame_range_2(self):
        self.__label.setText("get_frame_range_2")
        start_frame, end_frame = self.__rpa.timeline_api.get_frame_range()
        print("start, end", start_frame, end_frame)

        clip_frames = self.__rpa.timeline_api.get_clip_frames([start_frame, end_frame])
        print("clip_frames", clip_frames)
        clip_ids = self.__rpa.session_api.get_clips(self.__rpa.session_api.get_fg_playlist())
        test_eq("first clip", clip_ids[0], clip_frames[0][0])
        test_eq("last clip", clip_ids[0], clip_frames[1][0])
        test_eq("clip_start_frame", 1001, clip_frames[0][1])
        test_eq("clip_end_frame", 1080, clip_frames[1][1])
        test_eq("seq_start_frame", 1, start_frame)
        test_eq("seq_end_frame", 80, end_frame)

    def __select_single_clip(self):
        self.__label.setText("select_single_clip")
        fg_playlist = self.__rpa.session_api.get_fg_playlist()
        clips = self.__rpa.session_api.get_clips(fg_playlist)
        self.__rpa.session_api.set_active_clips(fg_playlist, clips[0:1])

    def __audio_scrubbing_1(self):
        self.__label.setText("__audio_scrubbing_1")
        state = self.__rpa.timeline_api.is_audio_scrubbing_enabled()
        test_eq("audio scrubbing False", False, state)

        self.__rpa.timeline_api.enable_audio_scrubbing(True)

        state = self.__rpa.timeline_api.is_audio_scrubbing_enabled()
        test_eq("audio scrubbing True", True, state)

    def __audio_scrubbing_2(self):
        self.__label.setText("__audio_scrubbing_2")
        state = self.__rpa.timeline_api.is_audio_scrubbing_enabled()
        test_eq("audio scrubbing True", True, state)

        self.__rpa.timeline_api.enable_audio_scrubbing(False)

        state = self.__rpa.timeline_api.is_audio_scrubbing_enabled()
        test_eq("audio scrubbing False", False, state)

    def __toggle_mute_2(self):
        self.__label.setText("toggle_mute_2")
        self.__rpa.timeline_api.set_mute(False)
        is_mute = self.__rpa.timeline_api.is_mute()
        test_eq("setting mute to false", False, is_mute)

    def __toggle_mute_1(self):
        self.__label.setText("toggle_mute_1")
        self.__rpa.timeline_api.set_mute(True)
        is_mute = self.__rpa.timeline_api.is_mute()
        test_eq("setting mute to true", True, is_mute)

    def __set_volume(self):
        self.__label.setText("set_volume")
        self.__rpa.timeline_api.set_volume(100)
        volume = self.__rpa.timeline_api.get_volume()
        print("volume", volume)

    def __get_volume(self):
        self.__label.setText("get_volume")
        volume = self.__rpa.timeline_api.get_volume()
        test_type("get volume to be int", int, type(volume))
        test_eq("volume", 100, volume)

    def __get_current_frame_1(self):
        self.__label.setText("get_current_frame")
        frame = self.__rpa.timeline_api.get_current_frame()
        clip_frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        print("frame:", frame)
        print("clip_frame:", clip_frame)

    def __get_frame_range_1(self):
        self.__label.setText("get_frame_range")
        start_frame, end_frame = self.__rpa.timeline_api.get_frame_range()
        print("start, end", start_frame, end_frame)

        clip_frames = self.__rpa.timeline_api.get_clip_frames([start_frame, end_frame])
        print("clip_frames", clip_frames)
        clip_ids = self.__rpa.session_api.get_clips(self.__rpa.session_api.get_fg_playlist())
        test_eq("first clip", clip_ids[0], clip_frames[0][0])
        test_eq("last clip", clip_ids[-1], clip_frames[1][0])
        test_eq("clip_start_frame", 1001, clip_frames[0][1])
        test_eq("clip_end_frame", 1034, clip_frames[1][1])
        test_eq("seq_start_frame", 1, start_frame)
        test_eq("seq_end_frame", 118, end_frame)

    def __goto_frame_1(self):
        self.__label.setText("goto_frame_1")
        seq_frame = self.__rpa.timeline_api.get_current_frame()
        print("1 seq_frame", seq_frame)
        clip, clip_frame = self.__rpa.timeline_api.get_clip_frames([seq_frame])[0]
        print("clip frame before", clip_frame)
        print("seq frame before", seq_frame)
        self.__rpa.timeline_api.goto_frame(seq_frame + 10)
        seq_frame = self.__rpa.timeline_api.get_current_frame()
        print("seq_frame", seq_frame)
        clip, clip_frame = self.__rpa.timeline_api.get_clip_frames([seq_frame])[0]
        print("clip frame after", clip_frame)
        print("seq frame after", seq_frame)

    def __is_playing(self):
        self.__label.setText("is_playing")
        playing, _ = self.__rpa.timeline_api.get_playing_state()
        test_eq("is playing False", False, playing)

    def __is_forward(self):
        self.__label.setText("is_forward")
        _, forward = self.__rpa.timeline_api.get_playing_state()
        test_eq("is forward True", True, forward)

    def __set_playing_1(self):
        self.__label.setText("__set_playing_1")
        self.__rpa.timeline_api.set_playing_state(True, True)
        playing, forward = self.__rpa.timeline_api.get_playing_state()
        test_eq("playing True", True, playing)
        test_eq("playing forward True", True, forward)

    def __set_playing_2(self):
        self.__label.setText("__set_playing_2")
        self.__rpa.timeline_api.set_playing_state(True, False)
        _, forward = self.__rpa.timeline_api.get_playing_state()
        test_eq("playing backwards", False, forward)

    def __set_playing_3(self):
        self.__label.setText("__set_playing_3")
        self.__rpa.timeline_api.set_playing_state(False, True)
        playing, forward = self.__rpa.timeline_api.get_playing_state()
        test_eq("not playing ", False, playing)
        test_eq("forwards", True, forward)

    def __set_playback_mode(self):
        self.__label.setText("__set_playback_mode")
        default_mode = self.__rpa.timeline_api.get_playback_mode()
        test_eq("playback mode - default", 0, default_mode)
        self.__rpa.timeline_api.set_playback_mode(1)
        once_mode = self.__rpa.timeline_api.get_playback_mode()
        test_eq("playback mode - once", 1, once_mode)
        self.__rpa.timeline_api.set_playback_mode(2)
        swing_mode = self.__rpa.timeline_api.get_playback_mode()
        test_eq("playback mode - swing", 2, swing_mode)
        self.__rpa.timeline_api.set_playback_mode(0)

    def __set_header(self, text):
        self.__header.setText(text)
        self.__label.setText("")

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
