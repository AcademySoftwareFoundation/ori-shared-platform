try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets
from functools import partial
from rpa.session_state.color_corrections import Grade, ColorTimer
import os


TEST_MEDIA_DIR = os.environ.get("TEST_MEDIA_DIR")


class TestColorApi:

    def __init__(self, rpa, parent_widget):
        self.__rpa = rpa
        self.__session_api = self.__rpa.session_api
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

        self.__clip_ro_id = None
        self.__frame_ro_id = None
        self.__frame_rw_id = None

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
            partial(self.__set_header, "Set clip cc - read write"),
            partial(self.__set_clip_cc_rw),
            partial(self.__create_clip_cc_ro),
            partial(self.__delete_clip_ro),
            partial(self.__create_frame_cc_ro),
            partial(self.__set_frame_cc_ro),
            partial(self.__create_frame_cc_rw),
            partial(self.__set_frame_cc_rw),
            partial(self.__delete_frame_ro),
            partial(self.__set_header, "Clip CCs Tests"),
            partial(self.__get_clip_ccs_1),
            partial(self.__move_clip_cc_1),
            partial(self.__append_clip_ccs_1),
            partial(self.__move_clip_cc_2),
            partial(self.__delete_clip_ccs_2),
            partial(self.__set_header, "Frame CCs Tests"),
            partial(self.__get_frame_ccs),
            partial(self.__move_frame_cc_1),
            partial(self.__delete_frame_ccs_1),
            partial(self.__append_frame_ccs_1),
            partial(self.__move_frame_cc_2),
            partial(self.__delete_frame_ccs_2),
            partial(self.__delete_frame_ccs_3),
            partial(self.__set_header, "CC Tests"),
            partial(self.__append_frame_cc_1),
            partial(self.__get_nodes_1),
            partial(self.__append_nodes),
            partial(self.__create_region_1),
            partial(self.__set_mute_all),
            partial(self.__unset_mute_all),
            partial(self.__set_read_only),
            partial(self.__unset_read_only),
            partial(self.__mute),
            partial(self.__un_mute),
            partial(self.__set_name),
            partial(self.__set_region_falloff_1),
            partial(self.__mute_node_1),
            partial(self.__mute_node_2),
            partial(self.__mute_node_3),
            partial(self.__mute_node_4),
            partial(self.__delete_node_1),
            partial(self.__delete_node_2),
            partial(self.__delete_node_3),
            partial(self.__set_node_properties),
            partial(self.__get_ro_rw_frames),
            partial(self.__set_channel_1),
            partial(self.__set_channel_2),
            partial(self.__set_channel_3),
            partial(self.__set_channel_4),
            partial(self.__set_channel_5),
            partial(self.__set_channel_6),

        ]
        func = tests[self.__test_cnt]
        func()
        self.__test_cnt += 1
        total_tests = len(tests)
        self.__test_iter_cnt.setText(f"{self.__test_cnt}/{total_tests}")

        if self.__test_cnt == len(tests):
            self.__test_cnt = 0
        else:
            QtCore.QTimer.singleShot(100, self.__run_test)

    def __set_channel_1(self):
        self.__label.setText("__set_channel_1")
        assert self.__rpa.color_api.get_channel() == 4
        self.__rpa.color_api.set_channel(0)
        assert self.__rpa.color_api.get_channel() == 0

    def __set_channel_2(self):
        self.__label.setText("__set_channel_2")
        assert self.__rpa.color_api.get_channel() == 0
        self.__rpa.color_api.set_channel(1)
        assert self.__rpa.color_api.get_channel() == 1

    def __set_channel_3(self):
        self.__label.setText("__set_channel_3")
        assert self.__rpa.color_api.get_channel() == 1
        self.__rpa.color_api.set_channel(2)
        assert self.__rpa.color_api.get_channel() == 2

    def __set_channel_4(self):
        self.__label.setText("__set_channel_4")
        assert self.__rpa.color_api.get_channel() == 2
        self.__rpa.color_api.set_channel(3)
        assert self.__rpa.color_api.get_channel() == 3

    def __set_channel_5(self):
        self.__label.setText("__set_channel_5")
        assert self.__rpa.color_api.get_channel() == 3
        self.__rpa.color_api.set_channel(5)
        assert self.__rpa.color_api.get_channel() == 5

    def __set_channel_6(self):
        self.__label.setText("__set_channel_6")
        assert self.__rpa.color_api.get_channel() == 5
        self.__rpa.color_api.set_channel(4)
        assert self.__rpa.color_api.get_channel() == 4

    def __get_ro_rw_frames(self):
        self.__label.setText("__get_ro_rw_frames")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]

        frame_cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        self.__rpa.color_api.delete_ccs(clip_id, frame_cc_ids, current_frame)

        cc_ids = self.__rpa.color_api.append_ccs(
            clip_id, ["pioneer_frame_cc", "resilient_frame_cc"], current_frame)
        self.__rpa.color_api.set_read_only(clip_id, cc_ids[1], True)
        self.__rpa.color_api.append_nodes(clip_id, cc_ids[0], [Grade(gain=(1.0, 0.5, 0.5))])
        self.__rpa.color_api.append_nodes(clip_id, cc_ids[1], [Grade(gain=(0.5, 1.0, 0.5))])

        cc_ids = self.__rpa.color_api.append_ccs(
            clip_id, ["trust_frame_cc", "courage_frame_cc"], current_frame+5)
        self.__rpa.color_api.append_nodes(clip_id, cc_ids[0], [Grade(gain=(0.5, 0.5, 1.0))])
        self.__rpa.color_api.append_nodes(clip_id, cc_ids[1], [Grade(gain=(1.0, 1.0, 0.5))])

        cc_ids = self.__rpa.color_api.append_ccs(
            clip_id, ["open_frame_cc", "pragmatic_frame_cc"], current_frame+10)
        self.__rpa.color_api.set_read_only(clip_id, cc_ids[0], True)
        self.__rpa.color_api.append_nodes(clip_id, cc_ids[0], [Grade(gain=(1.0, 0.5, 1.0))])
        self.__rpa.color_api.append_nodes(clip_id, cc_ids[1], [Grade(gain=(0.2, 0.3, 0.5))])

        ro_frames = self.__rpa.color_api.get_ro_frames(clip_id)
        rw_frames = self.__rpa.color_api.get_rw_frames(clip_id)
        print("ro_frames", ro_frames)
        print("rw_frames", rw_frames)

    def __set_node_properties(self):
        self.__label.setText("__set_node_properties")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        node_count = self.__rpa.color_api.get_node_count(clip_id, cc_id)
        assert node_count == 1

        class_name, slope  = self.__rpa.color_api.get_node_properties(
            clip_id, cc_id, 0, ["class_name", "slope"])
        assert class_name, slope == ("ColorTimer", (1.0, 1.0, 1.0))

        self.__rpa.color_api.set_node_properties(
            clip_id, cc_id, 0, {"class_name":"Grade", "slope":(0.0, 0.0, 1.0)})

        print("class_name, slope", class_name, slope)
        assert class_name, slope == ("ColorTimer", (0.0, 0.0, 1.0))

    def __delete_node_3(self):
        self.__label.setText("delete_node_3")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        node_count = self.__rpa.color_api.get_node_count(clip_id, cc_id)
        assert node_count == 2
        node_index = 1

        self.__rpa.color_api.delete_node(clip_id, cc_id, node_index)

        node_count = self.__rpa.color_api.get_node_count(clip_id, cc_id)
        assert node_count == 1

    def __delete_node_2(self):
        self.__label.setText("delete_node_2")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        node_count = self.__rpa.color_api.get_node_count(clip_id, cc_id)
        assert node_count == 3
        node_index = 2

        self.__rpa.color_api.delete_node(clip_id, cc_id, node_index)

        node_count = self.__rpa.color_api.get_node_count(clip_id, cc_id)
        assert node_count == 2

    def __delete_node_1(self):
        self.__label.setText("delete_node_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        node_count = self.__rpa.color_api.get_node_count(clip_id, cc_id)
        assert node_count == 4
        node_index = 3

        self.__rpa.color_api.delete_node(clip_id, cc_id, node_index)

        node_count = self.__rpa.color_api.get_node_count(clip_id, cc_id)
        assert node_count == 3

    def __mute_node_4(self):
        self.__label.setText("mute_node_4")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        for node_index in [1,2,3]:
            is_mute = self.__rpa.color_api.get_node_properties(
                clip_id, cc_id, node_index, ["mute"])[0]
            assert is_mute == True
            self.__rpa.color_api.set_node_properties(
                clip_id, cc_id, node_index, {"mute": False})
            is_mute = self.__rpa.color_api.get_node_properties(
                clip_id, cc_id, node_index, ["mute"])[0]
            assert is_mute == False

    def __mute_node_3(self):
        self.__label.setText("mute_node_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        node_count = self.__rpa.color_api.get_node_count(clip_id, cc_id)
        assert node_count == 4
        node_index = 1

        node = self.__rpa.color_api.get_node(clip_id, cc_id, node_index)
        expected = {
            'blackpoint': (0, 0, 0),
            'whitepoint': (1, 1, 1),
            'lift': (0, 0, 0),
            'gain': (2, 1, 1),
            'multiply': (1, 1, 1),
            'gamma': (1, 1, 1),
            'mute': False,
            'class_name': 'Grade'}

        for key, value in expected.items():
            assert value == node.get_dict()[key]

        self.__rpa.color_api.set_node_properties(clip_id, cc_id, node_index, {"mute": True})

        node = self.__rpa.color_api.get_node(clip_id, cc_id, node_index)
        expected = {
            'blackpoint': (0, 0, 0),
            'whitepoint': (1, 1, 1),
            'lift': (0, 0, 0),
            'gain': (2, 1, 1),
            'multiply': (1, 1, 1),
            'gamma': (1, 1, 1),
            'mute': True,
            'class_name': 'Grade'}
        for key, value in expected.items():
            assert value == node.get_dict()[key]

    def __mute_node_2(self):
        self.__label.setText("mute_node_2")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        node_count = self.__rpa.color_api.get_node_count(clip_id, cc_id)
        assert node_count == 4
        node_index = 2

        node = self.__rpa.color_api.get_node(clip_id, cc_id, node_index)
        node_dict = node.get_dict()
        expected = {
            'slope': (1, 1, 1),
            'offset': (0, 0, 0),
            'power': (1, 1, 1),
            'saturation': 2,
            'mute': False,
            'class_name': 'ColorTimer'}
        for key, value in expected.items():
            assert value == node_dict[key]

        self.__rpa.color_api.set_node_properties(clip_id, cc_id, node_index, {"mute": True})

        node = self.__rpa.color_api.get_node(clip_id, cc_id, node_index)
        node_dict = node.get_dict()
        expected = {
            'slope': (1, 1, 1),
            'offset': (0, 0, 0),
            'power': (1, 1, 1),
            'saturation': 2,
            'mute': True,
            'class_name': 'ColorTimer'}
        for key, value in expected.items():
            assert value == node_dict[key]

    def __mute_node_1(self):
        self.__label.setText("mute_node_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        node_count = self.__rpa.color_api.get_node_count(clip_id, cc_id)
        assert node_count == 4
        node_index = 3

        node = self.__rpa.color_api.get_node(clip_id, cc_id, node_index)
        expected = {
            'blackpoint': (0, 0, 0),
            'whitepoint': (1, 1, 1),
            'lift': (0, 0, 0),
            'gain': (1, 1, 1),
            'multiply': (1, 1, 1),
            'gamma': (1, 2, 1),
            'mute': False,
            'class_name': 'Grade'}
        for key, value in expected.items():
            assert value == node.get_dict()[key]

        self.__rpa.color_api.set_node_properties(clip_id, cc_id, node_index, {"mute": True})

        node = self.__rpa.color_api.get_node(clip_id, cc_id, node_index)
        expected = {
            'blackpoint': (0, 0, 0),
            'whitepoint': (1, 1, 1),
            'lift': (0, 0, 0),
            'gain': (1, 1, 1),
            'multiply': (1, 1, 1),
            'gamma': (1, 2, 1),
            'mute': True,
            'class_name': 'Grade'}
        for key, value in expected.items():
            assert value == node.get_dict()[key]

    def __set_name(self):
        self.__label.setText("set_name")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        name = self.__rpa.color_api.get_name(clip_id, cc_id)
        assert name == "Creative_Frame_CC"

        name = self.__rpa.color_api.set_name(clip_id, cc_id, "Resilient_Frame_CC")

        name = self.__rpa.color_api.get_name(clip_id, cc_id)
        assert name == "Resilient_Frame_CC"

    def __set_region_falloff_1(self):
        self.__label.setText("set_region_falloff_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        region_falloff = self.__rpa.color_api.get_region_falloff(clip_id, cc_id)
        assert region_falloff == 0.0

        self.__rpa.color_api.set_region_falloff(clip_id, cc_id, 100.0)

        region_falloff = self.__rpa.color_api.get_region_falloff(clip_id, cc_id)
        assert region_falloff == 100.0

    def __set_region_falloff_2(self):
        self.__label.setText("set_region_falloff_2")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        region_falloff = self.__rpa.color_api.get_region_falloff(clip_id, cc_id)
        assert region_falloff == 0.0

        self.__rpa.color_api.set_region_falloff(clip_id, cc_id, 0.0)

        region_falloff = self.__rpa.color_api.get_region_falloff(clip_id, cc_id)
        assert region_falloff == 0.0

    def __mute(self):
        self.__label.setText("mute")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        is_mute = self.__rpa.color_api.is_mute(clip_id, cc_id)
        assert is_mute == False

        is_mute = self.__rpa.color_api.mute(clip_id, cc_id, True)

        is_mute = self.__rpa.color_api.is_mute(clip_id, cc_id)
        assert is_mute == True

    def __un_mute(self):
        self.__label.setText("un_mute")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        is_mute = self.__rpa.color_api.is_mute(clip_id, cc_id)
        assert is_mute == True

        is_mute = self.__rpa.color_api.mute(clip_id, cc_id, False)

        is_mute = self.__rpa.color_api.is_mute(clip_id, cc_id)
        assert is_mute == False

    def __set_read_only(self):
        self.__label.setText("set_read_only")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        is_read_only = self.__rpa.color_api.is_read_only(clip_id, cc_id)
        assert is_read_only == False

        is_read_only = self.__rpa.color_api.set_read_only(clip_id, cc_id, True)

        is_read_only = self.__rpa.color_api.is_read_only(clip_id, cc_id)
        assert is_read_only == True

    def __unset_read_only(self):
        self.__label.setText("unset_read_only")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        is_read_only = self.__rpa.color_api.is_read_only(clip_id, cc_id)
        assert is_read_only == True

        is_read_only = self.__rpa.color_api.set_read_only(clip_id, cc_id, False)

        is_read_only = self.__rpa.color_api.is_read_only(clip_id, cc_id)
        assert is_read_only == False

    def __set_mute_all(self):
        self.__label.setText("set_mute_all")
        clip_id = self.__rpa.session_api.get_current_clip()

        is_mute_all = self.__rpa.color_api.is_mute_all(clip_id)
        assert is_mute_all == False

        is_mute_all = self.__rpa.color_api.mute_all(clip_id, True)

        is_mute_all = self.__rpa.color_api.is_mute_all(clip_id)
        assert is_mute_all == True

    def __unset_mute_all(self):
        self.__label.setText("unset_mute_all")
        clip_id = self.__rpa.session_api.get_current_clip()

        is_mute_all = self.__rpa.color_api.is_mute_all(clip_id)
        assert is_mute_all == True

        is_mute_all = self.__rpa.color_api.mute_all(clip_id, False)

        is_mute_all = self.__rpa.color_api.is_mute_all(clip_id)
        assert is_mute_all == False

    def __create_region_1(self):
        self.__label.setText("create_region_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_id = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)[0]

        has_region = self.__rpa.color_api.has_region(clip_id, cc_id)
        assert has_region == False

        self.__rpa.color_api.create_region(clip_id, cc_id)
        points = [
            (0.25, 0.25), (0.75, 0.25),
            (0.75, 0.75), (0.25, 0.75)]
        self.__rpa.color_api.append_shape_to_region(clip_id, cc_id, points)

    def __append_nodes(self):
        self.__label.setText("__append_nodes")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)

        color_timer_1 = ColorTimer(offset=(0.5, 0.5, 0.5))
        grade_1 = Grade(gain=(2, 1, 1))
        color_timer_2 = ColorTimer(saturation=2)
        grade_2 = Grade(gamma=(1, 2, 1))

        self.__rpa.color_api.append_nodes(
            clip_id, cc_ids[0],
            [color_timer_1, grade_1, color_timer_2, grade_2])
        nodes = self.__rpa.color_api.get_nodes(clip_id, cc_ids[0])
        assert isinstance(nodes[0], ColorTimer)
        assert nodes[0].offset == (0.5, 0.5, 0.5)
        assert isinstance(nodes[1], Grade)
        assert nodes[1].gain == (2, 1, 1)
        assert isinstance(nodes[2], ColorTimer)
        assert nodes[2].saturation == 2
        assert isinstance(nodes[3], Grade)
        assert nodes[3].gamma == (1, 2, 1)

    def __get_nodes_1(self):
        self.__label.setText("__get_nodes_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        nodes = self.__rpa.color_api.get_nodes(clip_id, cc_ids[0])
        print("nodes", nodes)
        assert nodes == []

    def __append_frame_cc_1(self):
        self.__label.setText("append_frame_cc_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        names_before = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_before:", names_before)

        self.__rpa.color_api.append_ccs(clip_id, ["Creative_Frame_CC"], current_frame)

        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        names_after = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_after:", names_after)
        assert names_after == ["Creative_Frame_CC"]

    def __delete_frame_ccs_3(self):
        self.__label.setText("delete_frame_ccs_3")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        names_before = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_before:", names_before)

        self.__rpa.color_api.delete_ccs(clip_id, cc_ids, current_frame)

        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        names_after = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_after:", names_after)
        assert names_after == []

    def __delete_frame_ccs_2(self):
        self.__label.setText("delete_frame_ccs_2")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        names_before = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_before:", names_before)

        self.__rpa.color_api.delete_ccs(clip_id, cc_ids[1:2], current_frame)

        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        names_after = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_after:", names_after)
        assert names_after == ['pragmatic_frame_cc', 'resilient_frame_cc']

    def __move_frame_cc_2(self):
        self.__label.setText("move_frame_cc_2")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        names_before = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_before:", names_before)
        self.__rpa.color_api.move_cc(clip_id, 0, 10, current_frame)
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        names_after = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_after:", names_after)
        assert names_after == ['pragmatic_frame_cc', 'fruitful_frame_cc', 'resilient_frame_cc']

    def __append_frame_ccs_1(self):
        self.__label.setText("append_frame_ccs_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        names_before = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_before:", names_before)
        new_names = ["resilient_frame_cc", "pragmatic_frame_cc", "fruitful_frame_cc"]
        cc_ids = self.__rpa.color_api.append_ccs(clip_id, new_names, current_frame)

        self.__rpa.color_api.create_region(clip_id, cc_ids[0])
        points = [
            (0.25, 0.25), (0.75, 0.25),
            (0.75, 0.75), (0.25, 0.75)]
        self.__rpa.color_api.append_shape_to_region(clip_id, cc_ids[0], points)
        self.__rpa.color_api.append_nodes(clip_id, cc_ids[0], [ColorTimer(offset=(2.0, 1.0, 1.0))])

        self.__rpa.color_api.create_region(clip_id, cc_ids[2])
        points = [
            (0.45, 0.45), (0.95, 0.45),
            (0.95, 0.95), (0.45, 0.95)]
        self.__rpa.color_api.append_shape_to_region(clip_id, cc_ids[2], points)
        self.__rpa.color_api.append_nodes(clip_id, cc_ids[2], [ColorTimer(offset=(-0.5, -0.5, -0.5))])

        for cnt, cc_id in enumerate(cc_ids):
            self.__rpa.color_api.set_read_only(clip_id, cc_id, cnt%2 == 0)
        names_after = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        is_read_only = [self.__rpa.color_api.is_read_only(clip_id, cc_id) for cc_id in cc_ids]
        print("names and is_read_only:", list(zip(names_after, is_read_only)))
        assert names_after == new_names
        assert is_read_only == [True, False, True]

    def __delete_frame_ccs_1(self):
        self.__label.setText("delete_frame_ccs_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        ccs_before = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        print("ccs_before", ccs_before)
        self.__rpa.color_api.delete_ccs(clip_id, ccs_before, current_frame)
        ccs_after = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        print("ccs_after", ccs_after)
        assert ccs_before == ccs_after

    def __move_frame_cc_1(self):
        self.__label.setText("move_frame_cc_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        ccs_before = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        print("ccs_before", ccs_before)
        self.__rpa.color_api.move_cc(clip_id, 0, 10, current_frame)
        ccs_after = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        print("ccs_after", ccs_after)
        assert ccs_before == ccs_after

    def __get_frame_ccs(self):
        self.__label.setText("get_frame_ccs")
        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]
        ccs = self.__rpa.color_api.get_cc_ids(clip_id, frame=current_frame)
        print("ccs", ccs)
        assert len(ccs) == 0

    def __delete_clip_ccs_2(self):
        self.__label.setText("delete_clip_ccs_2")
        clip_id = self.__rpa.session_api.get_current_clip()
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id)
        names_before = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_before:", names_before)

        self.__rpa.color_api.delete_ccs(clip_id, cc_ids[2:3])

        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id)
        names_after = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_after:", names_after)
        assert names_after == ['Clip', 'pragmatic_clip', 'resilient_clip']

    def __move_clip_cc_2(self):
        self.__label.setText("move_clip_cc_2")
        clip_id = self.__rpa.session_api.get_current_clip()
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id)
        names_before = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_before:", names_before)
        self.__rpa.color_api.move_cc(clip_id, 1, 10)
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id)
        names_after = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_after:", names_after)
        assert names_after == ['Clip', 'pragmatic_clip', 'fruitful_clip', 'resilient_clip']

    def __append_clip_ccs_1(self):
        self.__label.setText("__append_clip_ccs_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id)
        names_before = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("names_before:", names_before)
        new_names = ["resilient_clip", "pragmatic_clip", "fruitful_clip"]
        self.__rpa.color_api.append_ccs(clip_id, new_names)
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id)
        for cnt, cc_id in enumerate(cc_ids):
            self.__rpa.color_api.set_read_only(clip_id, cc_id, cnt%2 == 0)
        names_after = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        is_read_only = [self.__rpa.color_api.is_read_only(clip_id, cc_id) for cc_id in cc_ids]
        print("names and is_read_only:", list(zip(names_after, is_read_only)))
        assert names_after == ["Clip"] + new_names
        assert is_read_only == [True, False, True, False]

    def __move_clip_cc_1(self):
        self.__label.setText("__move_clip_cc_1")
        clip_id = self.__rpa.session_api.get_current_clip()
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id)
        cc_names_before = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        self.__rpa.color_api.move_cc(cc_ids[0], 0, 10)
        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id)
        cc_names_after = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        print("cc_names_before:", cc_names_before)
        print("cc_names_after:", cc_names_after)
        assert cc_names_before == cc_names_after

    def __get_clip_ccs_1(self):
        self.__label.setText("get_clip_ccs_1")

        clip_id = self.__rpa.session_api.get_current_clip()
        current_frame = self.__rpa.timeline_api.get_current_frame()
        _, current_frame = self.__rpa.timeline_api.get_clip_frames([current_frame])[0]

        clip_cc_ids = self.__rpa.color_api.get_cc_ids(clip_id)
        assert len(clip_cc_ids) == 1

        frame_cc_ids = self.__rpa.color_api.get_cc_ids(clip_id, current_frame)
        self.__rpa.color_api.delete_ccs(clip_id, frame_cc_ids, current_frame)

        cc_ids = self.__rpa.color_api.get_cc_ids(clip_id)
        cc_names = [self.__rpa.color_api.get_name(clip_id, cc_id) for cc_id in cc_ids]
        assert len(cc_ids) == 1

    def __set_header(self, text):
        self.__header.setText(text)
        self.__label.setText("")

    def __set_clip_cc_rw(self):
        self.__label.setText("Set Clip cc Read write")
        cguid = self.__rpa.session_api.get_current_clip()
        ccs = self.__rpa.color_api.get_cc_ids(cguid)
        values = {"offset": (0.0, 0.1, 0.0)}
        self.__rpa.color_api.set_node_properties(cguid, ccs[0], 0, values)

    def __create_clip_cc_ro(self):
        self.__label.setText("Create and set Clip cc Read only")
        cguid = self.__rpa.session_api.get_current_clip()
        self.__clip_ro_id = self.__rpa.color_api.append_ccs(cguid, ["ClipRO"])[0]
        self.__rpa.color_api.append_nodes(cguid, self.__clip_ro_id, [ColorTimer()])
        self.__rpa.color_api.append_nodes(cguid, self.__clip_ro_id, [Grade()])
        self.__rpa.color_api.set_read_only(cguid, self.__clip_ro_id, True)
        values = {"slope": (1.5, 0.0, 1.5)}
        self.__rpa.color_api.set_node_properties(cguid, self.__clip_ro_id, 0, values)

    def __swap_clip_ccs(self):
        self.__label.setText("Swap clip ccs")
        cguid = self.__rpa.session_api.get_current_clip()
        self.__rpa.color_api.move_cc(cguid, 1, 0)

    def __delete_clip_ro(self):
        self.__label.setText("delete ClipRO")
        cguid = self.__rpa.session_api.get_current_clip()
        self.__rpa.color_api.delete_ccs(cguid, [self.__clip_ro_id])

    def __create_frame_cc_ro(self):
        self.__label.setText("Create Frame cc (1001) Read only")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__frame_ro_id = self.__rpa.color_api.append_ccs(cguid, ["FrameCCRO"], frame)[0]
        self.__rpa.color_api.append_nodes(cguid, self.__frame_ro_id, [ColorTimer()])
        self.__rpa.color_api.append_nodes(cguid, self.__frame_ro_id, [Grade()])
        self.__rpa.color_api.set_read_only(cguid, self.__frame_ro_id, True)

    def __set_frame_cc_ro(self):
        self.__label.setText("Set Frame cc (1001) Read only")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        values = {"blackpoint": (1.5, 1.5, 1.5)}
        self.__rpa.color_api.set_node_properties(cguid, self.__frame_ro_id, 1, values)

    def __create_frame_cc_rw(self):
        self.__label.setText("Create Frame cc (1001) Read write")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__frame_rw_id = self.__rpa.color_api.append_ccs(cguid, ["FrameCCRW"], frame)[0]
        self.__rpa.color_api.append_nodes(cguid, self.__frame_rw_id, [ColorTimer()])
        self.__rpa.color_api.append_nodes(cguid, self.__frame_rw_id, [Grade()])

    def __set_frame_cc_rw(self):
        self.__label.setText("Set Frame cc (1001) Read write")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        values = {"lift": (0.5, 0.5, 0.5)}
        self.__rpa.color_api.set_node_properties(cguid, self.__frame_rw_id, 1, values)

    def __delete_frame_ro(self):
        self.__label.setText("delete FrameRO")
        cguid = self.__rpa.session_api.get_current_clip()
        frame = self.__rpa.timeline_api.get_current_frame()
        _, frame = self.__rpa.timeline_api.get_clip_frames([frame])[0]
        self.__rpa.color_api.delete_ccs(cguid, [self.__frame_ro_id], frame)

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
