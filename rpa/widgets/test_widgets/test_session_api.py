try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets
from functools import partial
import uuid
from collections import deque
import os


TEST_MEDIA_DIR = os.environ.get("TEST_MEDIA_DIR")

class TestSessionApi:

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
            partial(self.__set_header, "1 Session must always have a FG playlist!"),
            partial(self.__clear_session),
            partial(self.__test_2),
            partial(self.__test_3),
            partial(self.__restore_deleted_playlists),
            partial(self.__test_2),
            partial(self.__clear_session),
            partial(self.__create_playlists_1),
            partial(self.__clear_session),
            partial(self.__create_playlists_1),
            partial(self.__test_7),
            partial(self.__test_8),
            partial(self.__test_8),
            partial(self.__test_8),
            partial(self.__test_8),
            partial(self.__test_8),
            partial(self.__test_8),
            partial(self.__test_8),
            partial(self.__test_8),
            partial(self.__create_playlists_1),
            partial(self.__test_9),
            partial(self.__delete_playlists_permanently),
            partial(self.__clear_session),
            partial(self.__set_header, "3 FG & BG  Management"),
            partial(self.__create_playlists_2),
            partial(self.__test_12),
            partial(self.__set_bg_mode_wipe),
            partial(self.__swap_fg_and_bg_playlists),
            partial(self.__set_bg_mode_none),
            partial(self.__set_bg_mode_side_by_side),
            partial(self.__swap_fg_and_bg_playlists),
            partial(self.__set_bg_mode_none),
            partial(self.__set_bg_mode_top_bottom),
            partial(self.__swap_fg_and_bg_playlists),
            partial(self.__set_bg_mode_none),
            partial(self.__set_bg_mode_pip),
            partial(self.__swap_fg_and_bg_playlists),
            partial(self.__set_bg_mode_wipe),
            partial(self.__test_13),
            partial(self.__test_14),
            partial(self.__test_15),
            partial(self.__restore_deleted_playlists),
            partial(self.__test_16),
            partial(self.__clear_session),
            partial(self.__set_header, "4 Move Playlists"),
            partial(self.__create_playlists_3),
            partial(self.__move_playlists_to_index_1),
            partial(self.__move_playlists_to_index_2),
            partial(self.__move_playlists_to_index_3),
            partial(self.__clear_session),
            partial(self.__create_playlists_3),
            partial(self.__move_playlists_up),
            partial(self.__move_playlists_up),
            partial(self.__move_playlists_down),
            partial(self.__move_playlists_down),
            partial(self.__move_playlists_top),
            partial(self.__move_playlists_bottom),
            partial(self.__test_21),
            partial(self.__clear_session),
            partial(self.__set_header, "6 Clip Operations"),
            partial(self.__create_playlists_4),
            partial(self.__move_clip_after_creation),
            partial(self.__clear_session),
            partial(self.__create_playlists_4),
            partial(self.__test_22),
            partial(self.__test_23),
            partial(self.__set_playlist_one_to_fg),
            partial(self.__move_clips_to_index_1),
            partial(self.__move_clips_to_index_2),
            partial(self.__move_clips_to_index_3),
            partial(self.__move_clips_up),
            partial(self.__move_clips_down),
            partial(self.__move_clips_top),
            partial(self.__move_clips_bottom),
            partial(self.__test_23),
            partial(self.__set_playlist_three_to_fg),
            partial(self.__set_playlist_one_to_fg),
            partial(self.__set_playlist_three_to_fg),
            partial(self.__test_33),
            partial(self.__create_playlists_5),
            partial(self.__test_34),
            partial(self.__test_35),
            partial(self.__clear_session),
            partial(self.__set_header, "7 Setting Clip Attrs"),
            partial(self.__create_playlists_5),
            partial(self.__test_36),
            partial(self.__test_37),
            partial(self.__test_38),
            partial(self.__clear_session),
            partial(self.__create_clips),
            partial(self.__custom_attrs_1),
            partial(self.__clear_session),
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

    def __move_playlists_to_index_1(self):
        pl_ids = self.__rpa.session_api.get_playlists()
        pl_names = [self.__rpa.session_api.get_playlist_name(pl_id) for pl_id in pl_ids]
        assert pl_names == ['one 1', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen']

        to_move = [pl_ids[3], pl_ids[5], pl_ids[7]]
        self.__rpa.session_api.move_playlists_to_index(1, to_move)

        pl_ids = self.__rpa.session_api.get_playlists()
        pl_names = [self.__rpa.session_api.get_playlist_name(pl_id) for pl_id in pl_ids]
        assert pl_names == ['one 1', 'four', 'six', 'eight', 'two', 'three', 'five', 'seven', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen']

    def __move_playlists_to_index_2(self):
        pl_ids = self.__rpa.session_api.get_playlists()
        pl_names = [self.__rpa.session_api.get_playlist_name(pl_id) for pl_id in pl_ids]
        assert pl_names == ['one 1', 'four', 'six', 'eight', 'two', 'three', 'five', 'seven', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen']

        to_move = [pl_ids[3], pl_ids[5], pl_ids[7]]
        self.__rpa.session_api.move_playlists_to_index(4, to_move)

        pl_ids = self.__rpa.session_api.get_playlists()
        pl_names = [self.__rpa.session_api.get_playlist_name(pl_id) for pl_id in pl_ids]
        assert pl_names == ['one 1', 'four', 'six', 'two', 'eight', 'three', 'seven', 'five', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen']

    def __move_playlists_to_index_3(self):
        pl_ids = self.__rpa.session_api.get_playlists()
        pl_names = [self.__rpa.session_api.get_playlist_name(pl_id) for pl_id in pl_ids]
        assert pl_names == ['one 1', 'four', 'six', 'two', 'eight', 'three', 'seven', 'five', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen']

        to_move = [pl_ids[3], pl_ids[5], pl_ids[7]]
        self.__rpa.session_api.move_playlists_to_index(len(pl_ids) + 5, to_move)

        pl_ids = self.__rpa.session_api.get_playlists()
        pl_names = [self.__rpa.session_api.get_playlist_name(pl_id) for pl_id in pl_ids]
        assert pl_names == ['one 1', 'four', 'six', 'eight', 'seven', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'two', 'three', 'five']

    def __post_set_custom_session_attr(self, out, attr_id, value):
        print("__post_set_custom_session_attr", out, attr_id, value)

    def __post_set_custom_playlist_attr(self, out, playlist_id, attr_id, value):
        print("__post_set_custom_playlist_attr", out, playlist_id, attr_id, value)

    def __post_set_custom_clip_attr(self, out, clip_id, attr_id, value):
        print("__post_set_custom_clip_attr", out, clip_id, attr_id, value)

    def __custom_attrs_1(self):
        self.__label.setText("custom_attrs_1")
        delegate_mngr = self.__rpa.session_api.delegate_mngr

        delegate_mngr.add_post_delegate(
            self.__rpa.session_api.set_custom_session_attr,
            self.__post_set_custom_session_attr)
        delegate_mngr.add_post_delegate(
            self.__rpa.session_api.set_custom_playlist_attr,
            self.__post_set_custom_playlist_attr)
        delegate_mngr.add_post_delegate(
            self.__rpa.session_api.set_custom_clip_attr,
            self.__post_set_custom_clip_attr)

        attr_id = "session_attr_id_1"
        attr_value = "session_attr_value_1"
        value = self.__rpa.session_api.get_custom_session_attr(attr_id)
        assert value is None
        self.__rpa.session_api.set_custom_session_attr((attr_id), attr_value)
        print(self.__rpa.session_api.get_custom_session_attr_ids())
        value = self.__rpa.session_api.get_custom_session_attr((attr_id))
        assert value == attr_value

        pl_id = self.__rpa.session_api.get_fg_playlist()
        attr_id = "playlist_attr_id_1"
        attr_value = "playlist_attr_value_1"
        value = self.__rpa.session_api.get_custom_playlist_attr(pl_id, attr_id)
        assert value is None
        self.__rpa.session_api.set_custom_playlist_attr(pl_id, attr_id, attr_value)
        print(self.__rpa.session_api.get_custom_playlist_attr_ids(pl_id))
        value = self.__rpa.session_api.get_custom_playlist_attr(pl_id, attr_id)
        assert value == attr_value

        cl_id = self.__rpa.session_api.get_current_clip()
        attr_id = "clip_attr_id_1"
        attr_value = "clip_attr_value_1"
        value = self.__rpa.session_api.get_custom_clip_attr(cl_id, attr_id)
        assert value is None
        self.__rpa.session_api.set_custom_clip_attr(cl_id, attr_id, attr_value)
        print(self.__rpa.session_api.get_custom_clip_attr_ids(cl_id))
        value = self.__rpa.session_api.get_custom_clip_attr(cl_id, attr_id)
        assert value == attr_value

    def __set_header(self, text):
        self.__header.setText(text)

    def __move_clip_after_creation(self):
        self.__label.setText("Move Clip After Creation")
        pguid = self.__rpa.session_api.get_fg_playlist()
        cguid = uuid.uuid4().hex
        path =  os.path.join(TEST_MEDIA_DIR, "one.mp4")
        self.__rpa.session_api.create_clips(pguid, [path], ids=[cguid])
        self.__rpa.session_api.move_clips_by_offset(-1, [cguid])

    def __clear_session(self):
        self.__label.setText("Clear Session")
        self.__session_api.clear()

    def __test_2(self):
        self.__label.setText("Delete permanently the only playlist")
        self.__session_api.delete_playlists_permanently(
            self.__session_api.get_playlists())

    def __test_3(self):
        self.__label.setText("Delete the only playlist")
        self.__session_api.delete_playlists(
            self.__session_api.get_playlists())

    def __restore_deleted_playlists(self):
        self.__label.setText("Restore deleted playlist")
        self.__session_api.restore_playlists(
            self.__session_api.get_deleted_playlists())

    def __create_playlists_1(self):
        self.__label.setText("Create list of Playlists with Clips")
        all_ids = []
        names = ["one", "two"]
        ids = [uuid.uuid4().hex for _ in  names]
        all_ids.extend(ids)
        self.__session_api.create_playlists(names, ids=ids)
        names = ["three", "four"]
        ids = [uuid.uuid4().hex for _ in  names]
        all_ids.extend(ids)
        self.__session_api.create_playlists(names, ids=ids)
        names = ["five", "six"]
        ids = [uuid.uuid4().hex for _ in  names]
        all_ids.extend(ids)
        self.__session_api.create_playlists(names, ids=ids)
        names = ["seven", "eight"]
        ids = [uuid.uuid4().hex for _ in  names]
        all_ids.extend(ids)
        self.__session_api.create_playlists(names, ids=ids)

        self.__session_api.delete_playlists_permanently(
            [self.__session_api.get_playlists()[0]])
        count = 0
        paths = deque([
            os.path.join(TEST_MEDIA_DIR, "five.mp4"),
            os.path.join(TEST_MEDIA_DIR, "six.mp4"),
            os.path.join(TEST_MEDIA_DIR, "seven.mp4"),
            os.path.join(TEST_MEDIA_DIR, "eight.mp4"),
            os.path.join(TEST_MEDIA_DIR, "nine.mp4"),
            os.path.join(TEST_MEDIA_DIR, "one.mp4"),
            os.path.join(TEST_MEDIA_DIR, "two.mp4"),
            os.path.join(TEST_MEDIA_DIR, "three.mp4"),
            os.path.join(TEST_MEDIA_DIR, "four.mp4")
        ])
        for playlist_id in all_ids:
            paths.rotate(1)
            __paths = list(paths)
            ids = [uuid.uuid4().hex for _ in  __paths]
            self.__session_api.create_clips(playlist_id, __paths, ids=ids)
            count += 2

    def __test_7(self):
        self.__label.setText("Set FG Playlist")
        playlist = self.__session_api.get_playlists()[4]
        self.__session_api.set_fg_playlist(playlist)

    def __test_8(self):
        self.__label.setText("Delete FG playlist")
        self.__session_api.delete_playlists_permanently(
            [self.__session_api.get_fg_playlist()])

    def __test_9(self):
        playlist = self.__session_api.get_playlists()[3]
        self.__session_api.set_bg_playlist(playlist)

    def __delete_playlists_permanently(self):
        playlists = self.__session_api.get_playlists()
        playlists = [playlists[0], playlists[1]]
        self.__session_api.delete_playlists_permanently(playlists)

    def __test_10(self):
        self.__label.setText("Set parent of 'six' to be 'two'")
        playlist = self.__session_api.get_playlists(
            self.__session_api.get_playlists(
                self.__session_api.get_playlists()[0])[1])[1]
        parent_playlist = self.__session_api.get_playlists()[1]
        self.__session_api.set_playlists_parent([playlist], parent_playlist)

    def __test_11(self):
        self.__label.setText("Set parent of 'six' to be 'session'")
        playlist = self.__session_api.get_playlists(
            self.__session_api.get_playlists()[1])[0]
        self.__session_api.set_playlists_parent(
            [playlist], None)

    def __create_playlists_2(self):
        self.__label.setText("Create Playlists")
        all_ids = []
        names = ["one", "two"]
        ids = [uuid.uuid4().hex for _ in  names]
        all_ids.extend(ids)
        self.__session_api.create_playlists(names, ids=ids)
        names = ["three", "four"]
        ids = [uuid.uuid4().hex for _ in  names]
        all_ids.extend(ids)
        self.__session_api.create_playlists(names, ids=ids)
        names = ["five", "six"]
        ids = [uuid.uuid4().hex for _ in  names]
        all_ids.extend(ids)
        self.__session_api.create_playlists(names, ids=ids)
        playlist = self.__session_api.get_playlists()[0]
        self.__session_api.delete_playlists_permanently([playlist])

        paths = [
            os.path.join(TEST_MEDIA_DIR, "five.mp4"),
            os.path.join(TEST_MEDIA_DIR, "six.mp4")]

        ids = [uuid.uuid4().hex for _ in  paths]
        self.__session_api.create_clips(all_ids[0], paths, ids=ids)

        paths = [
            os.path.join(TEST_MEDIA_DIR, "seven.mp4"),
            os.path.join(TEST_MEDIA_DIR, "eight.mp4")]
        ids = [uuid.uuid4().hex for _ in  paths]
        self.__session_api.create_clips(all_ids[1], paths, ids=ids)

        paths = [
            os.path.join(TEST_MEDIA_DIR, "seven.mp4"),
            os.path.join(TEST_MEDIA_DIR, "one.mp4")]
        ids = [uuid.uuid4().hex for _ in  paths]
        self.__session_api.create_clips(all_ids[2], paths, ids=ids)

        paths = [os.path.join(TEST_MEDIA_DIR, "two.mp4")]
        ids = [uuid.uuid4().hex for _ in  paths]
        self.__session_api.create_clips(all_ids[3], paths, ids=ids)

        paths = [os.path.join(TEST_MEDIA_DIR, "three.mp4")]
        ids = [uuid.uuid4().hex for _ in  paths]
        self.__session_api.create_clips(all_ids[4], paths, ids=ids)

        paths = [os.path.join(TEST_MEDIA_DIR, "four.mp4")]
        ids = [uuid.uuid4().hex for _ in  paths]
        self.__session_api.create_clips(all_ids[5], paths, ids=ids)

    def __test_12(self):
        self.__label.setText("Set BG Playlist")
        playlist = self.__session_api.get_playlists()[4]
        self.__session_api.set_bg_playlist(playlist)

    def __set_bg_mode_none(self):
        self.__label.setText("Set BG Mode - None")
        self.__session_api.set_bg_mode(0)

    def __set_bg_mode_wipe(self):
        self.__label.setText("Set BG Mode - Wipe")
        self.__session_api.set_bg_mode(1)

    def __set_bg_mode_side_by_side(self):
        self.__label.setText("Set BG Mode - Side by Side")
        self.__session_api.set_bg_mode(2)

    def __set_bg_mode_top_bottom(self):
        self.__label.setText("Set BG Mode - Top Bottom")
        self.__session_api.set_bg_mode(3)

    def __set_bg_mode_pip(self):
        self.__label.setText("Set BG Mode - PIP")
        self.__session_api.set_bg_mode(4)

    def __swap_fg_and_bg_playlists(self):
        self.__label.setText("Set FG to be BG Playlist")
        self.__session_api.set_fg_playlist(
            self.__session_api.get_bg_playlist())

    def __test_13(self):
        self.__label.setText("Change FG Playlist")
        playlist = self.__session_api.get_playlists()[2]
        self.__session_api.set_fg_playlist(
            playlist)

    def __test_14(self):
        self.__label.setText("Change BG Playlist")
        playlist = self.__session_api.get_playlists()[1]
        self.__session_api.set_bg_playlist(playlist)

    def __test_15(self):
        self.__label.setText("Delete BG Playlist")
        self.__session_api.delete_playlists(
            [self.__session_api.get_bg_playlist()])

    def __test_16(self):
        self.__label.setText("Set BG playlist")
        playlist = self.__session_api.get_playlists()[1]
        self.__session_api.set_bg_playlist(playlist)

    def __create_playlists_3(self):
        self.__label.setText("Create Playlists with Clips")
        names = ["one 1", "two", "three", "four", "five"]
        ids = [uuid.uuid4().hex for _ in  names]
        self.__session_api.create_playlists(names, ids=ids)

        names = ["six", "seven", "eight", "nine", "ten"]
        ids = [uuid.uuid4().hex for _ in  names]
        self.__session_api.create_playlists(names, ids=ids)

        names = ["eleven", "twelve", "thirteen"]
        ids = [uuid.uuid4().hex for _ in  names]
        self.__session_api.create_playlists(names, ids=ids)

        names = ["fourteen", "fifteen"]
        ids = [uuid.uuid4().hex for _ in  names]
        self.__session_api.create_playlists(names, ids=ids)

        playlist = self.__session_api.get_playlists()[0]
        self.__session_api.delete_playlists_permanently([playlist])

    def __move_playlists_up(self):
        self.__label.setText("Move playlists up")
        playlists_to_move = [
            self.__session_api.get_playlists()[2],
            self.__session_api.get_playlists()[3]
        ]
        self.__session_api.move_playlists_by_offset(-1, playlists_to_move)

    def __move_playlists_down(self):
        self.__label.setText("Move playlists down")
        playlists_to_move = [
            self.__session_api.get_playlists()[0],
            self.__session_api.get_playlists()[2],
        ]
        self.__session_api.move_playlists_by_offset(1, playlists_to_move)

    def __move_playlists_top(self):
        self.__label.setText("Move playlists top")
        playlists = self.__session_api.get_playlists()
        playlists_to_move = [playlists[0], playlists[1]]
        self.__session_api.move_playlists_by_offset(-len(playlists), playlists_to_move)

    def __move_playlists_bottom(self):
        self.__label.setText("Move playlists bottom")
        playlists = self.__session_api.get_playlists()
        playlists_to_move = [playlists[0], playlists[1]]
        self.__session_api.move_playlists_by_offset(len(playlists), playlists_to_move)

    def __test_21(self):
        self.__label.setText("Set Playlist Name")
        playlist = self.__session_api.get_playlists()[0]
        self.__session_api.set_playlist_name(playlist, "yes we can")

    def __create_playlists_4(self):
        self.__label.setText("Create Playlists 4")
        playlist_one = self.__session_api.get_playlists()[0]
        self.__session_api.set_playlist_name(playlist_one, "one")
        self.__session_api.create_playlists( ["two"], ids=[uuid.uuid4().hex])
        self.__session_api.create_playlists(["three"], ids=[uuid.uuid4().hex])
        paths = deque([
            os.path.join(TEST_MEDIA_DIR, "five.mp4"),
            os.path.join(TEST_MEDIA_DIR, "six.mp4"),
            os.path.join(TEST_MEDIA_DIR, "seven.mp4"),
            os.path.join(TEST_MEDIA_DIR, "eight.mp4"),
            os.path.join(TEST_MEDIA_DIR, "nine.mp4"),
            os.path.join(TEST_MEDIA_DIR, "one.mp4"),
            os.path.join(TEST_MEDIA_DIR, "two.mp4"),
            os.path.join(TEST_MEDIA_DIR, "three.mp4"),
            os.path.join(TEST_MEDIA_DIR, "four.mp4")
        ])
        ids = [uuid.uuid4().hex for _ in  paths]
        self.__session_api.create_clips(playlist_one, list(paths), ids=ids)
        paths = deque(list(paths)[:5])
        paths.rotate(2)
        ids = [uuid.uuid4().hex for _ in  paths]
        playlist_two = self.__session_api.get_playlists()[1]
        self.__session_api.create_clips(playlist_two, list(paths), ids=ids)

    def __test_22(self):
        self.__label.setText("Select Clips")

        playlist = self.__session_api.get_playlists()[0]
        clips = self.__session_api.get_clips(playlist)
        self.__session_api.set_active_clips(
            playlist, [clips[1], clips[3], clips[5]])

        playlist = self.__session_api.get_playlists()[1]
        clips = self.__session_api.get_clips(playlist)
        self.__session_api.set_active_clips(
            playlist, [clips[0], clips[2], clips[4]])

    def __test_23(self):
        self.__label.setText("Set Playlist 'two' as FG")
        playlist = self.__session_api.get_playlists()[1]
        self.__session_api.set_fg_playlist(playlist)

    def __set_playlist_one_to_fg(self):
        self.__label.setText("Set Playlist 'one' as FG")
        playlist = self.__session_api.get_playlists()[0]
        self.__session_api.set_fg_playlist(playlist)

    def __move_clips_to_index_1(self):
        self.__label.setText("Move clips to index 1")
        playlist = self.__session_api.get_playlists()[0]
        clips = self.__session_api.get_active_clips(playlist)
        self.__session_api.move_clips_to_index(1, clips)

    def __move_clips_to_index_2(self):
        self.__label.setText("Move clips to index 2")
        playlist = self.__session_api.get_playlists()[0]
        clips = self.__session_api.get_active_clips(playlist)
        self.__session_api.move_clips_to_index(3, clips)

    def __move_clips_to_index_3(self):
        self.__label.setText("Move clips to index 2")
        playlist = self.__session_api.get_playlists()[0]
        active_clips = self.__session_api.get_active_clips(playlist)
        clips = self.__session_api.get_clips(playlist)
        self.__session_api.move_clips_to_index(len(clips) + 5, active_clips)

    def __move_clips_up(self):
        self.__label.setText("Move clips of Playlist 'one' up")
        playlist = self.__session_api.get_playlists()[0]
        clips = self.__session_api.get_active_clips(playlist)
        self.__session_api.move_clips_by_offset(-1, clips)

    def __move_clips_down(self):
        self.__label.setText("Move clips of Playlist 'one' down")
        playlist = self.__session_api.get_playlists()[0]
        clips = self.__session_api.get_active_clips(playlist)
        self.__session_api.move_clips_by_offset(1, clips)

    def __move_clips_top(self):
        self.__label.setText("Move clips of Playlist 'one' top")
        playlist = self.__session_api.get_playlists()[0]
        clips = self.__session_api.get_active_clips(playlist)
        self.__session_api.move_clips_by_offset(
            -len(self.__session_api.get_clips(playlist)), clips)

    def __move_clips_bottom(self):
        self.__label.setText("Move clips of Playlist 'one' bottom")
        playlist = self.__session_api.get_playlists()[0]
        clips = self.__session_api.get_active_clips(playlist)
        self.__session_api.move_clips_by_offset(
            len(self.__session_api.get_clips(playlist)), clips)

    def __set_playlist_three_to_fg(self):
        self.__label.setText("Set playlist 'three' to be FG")
        playlist = self.__session_api.get_playlists()[1]
        self.__session_api.set_fg_playlist(playlist)

    def __test_33(self):
        self.__label.setText("Delete permanently Clips in playlist 'three'")
        playlist = self.__session_api.get_playlists()[1]
        clips = self.__session_api.get_active_clips(playlist)
        self.__session_api.delete_clips_permanently(clips)

    def __create_playlists_5(self):
        self.__label.setText("Create Playlists 5")
        self.__session_api.clear()
        playlist = self.__session_api.get_playlists()[0]
        self.__session_api.set_playlist_name(playlist, "one")
        paths = [
            os.path.join(TEST_MEDIA_DIR, "one.mp4"),
            os.path.join(TEST_MEDIA_DIR, "two.mp4"),
            os.path.join(TEST_MEDIA_DIR, "three.mp4"),
            os.path.join(TEST_MEDIA_DIR, "four.mp4")
        ]
        ids = [uuid.uuid4().hex for _ in  paths]
        self.__session_api.create_clips(playlist, list(paths), ids=ids)

    def __test_34(self):
        self.__label.setText("Select Clips")
        playlist = self.__session_api.get_playlists()[0]
        clips = self.__session_api.get_clips(playlist)
        self.__session_api.set_active_clips(
            playlist, [clips[1], clips[2]])

    def __test_35(self):
        self.__label.setText("De-Select Clips")
        playlist = self.__session_api.get_playlists()[0]
        clips = self.__session_api.get_clips(playlist)
        self.__session_api.set_active_clips(playlist, [])

    def __test_36(self):
        self.__label.setText("Set single attr value of a single clip")
        playlist = self.__session_api.get_playlists()[0]
        clip = self.__session_api.get_current_clip()
        attr_values = [(playlist, clip, "rotation", 45.0)]
        self.__session_api.set_attr_values(attr_values)

    def __test_37(self):
        self.__label.setText("Set single attr value of multiple clips")
        playlist = self.__session_api.get_playlists()[0]
        clips = self.__session_api.get_clips(playlist)
        attr_values = [(playlist, clip, "grayscale", True) for clip in clips]
        self.__session_api.set_attr_values(attr_values)

    def __test_38(self):
        self.__label.setText("Set multiple attr values of single clip")
        playlist = self.__session_api.get_playlists()[0]
        clip = self.__session_api.get_current_clip()
        attr_values = [
            (playlist, clip, "rotation", 45.0),
            (playlist, clip, "grayscale", False),
            (playlist, clip, "flip_x", True),
            (playlist, clip, "flip_y", True),
            (playlist, clip, "scale_x", 2.0),
            (playlist, clip, "scale_y", 3.0),
            (playlist, clip, "pan_x", 10.0),
            (playlist, clip, "pan_y", 20.0)
        ]
        self.__session_api.set_attr_values(attr_values)


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
