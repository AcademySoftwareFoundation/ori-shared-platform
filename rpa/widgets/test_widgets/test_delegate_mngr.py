try:
    from PySide2 import QtCore, QtWidgets
except ImportError:
    from PySide6 import QtCore, QtWidgets
from functools import partial
import os


TEST_MEDIA_DIR = os.environ.get("TEST_MEDIA_DIR")


class TestDelegateMngr:

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
            partial(self.__permissions_1),
            partial(self.__permissions_2),
            partial(self.__clear_all_permission_delegates),
            partial(self.__permissions_4),
            partial(self.__clear_all_permission_delegates),
            partial(self.__pre_post_delegates_1),
            partial(self.__pre_post_delegates_2),
        ]
        func = tests[self.__test_cnt]
        func()
        self.__test_cnt += 1
        total_tests = len(tests)
        self.__test_iter_cnt.setText(f"{self.__test_cnt}/{total_tests}")

        if self.__test_cnt == total_tests:
            self.__test_cnt = 0
        # else:
        #     QtCore.QTimer.singleShot(200, self.__run_test)

    def __pre_create_clips(self, playlist_id, paths, index, ids):
        print("pre_create_clips: ", playlist_id, paths, index, ids)

    def __post_create_clips(self, out, playlist_id, paths, index, ids):
        print("post_create_clips: ", out, playlist_id, paths, index, ids)

    def __pre_post_delegates_1(self):
        self.__label.setText("Add Pre and Post delegates")
        delegate_mngr = self.__rpa.session_api.delegate_mngr
        rpa_method = self.__rpa.session_api.create_clips

        delegate_mngr.add_pre_delegate(rpa_method, self.__pre_create_clips)
        delegate_mngr.add_post_delegate(rpa_method, self.__post_create_clips)
        assert len(delegate_mngr.get_pre_delegates(rpa_method)) == 1
        assert len(delegate_mngr.get_post_delegates(rpa_method)) == 1

    def __pre_post_delegates_2(self):
        self.__label.setText("Clear Pre and Post delegates")
        delegate_mngr = self.__rpa.session_api.delegate_mngr
        rpa_method = self.__rpa.session_api.create_clips
        delegate_mngr.clear_pre_delegates(rpa_method)
        delegate_mngr.clear_post_delegates(rpa_method)
        assert len(delegate_mngr.get_pre_delegates(rpa_method)) == 0
        assert len(delegate_mngr.get_post_delegates(rpa_method)) == 0

    def __return_true(self, *args, **kwargs):
        return True

    def __return_false(self, *args, **kwargs):
        return False

    def __permissions_create_clips(self, playlist_id, paths, index, ids):
        print("permissions_create_clips")
        print("Args: ", playlist_id, paths, index, ids)
        if index == 1: return False
        return True

    def __permissions_4(self):
        self.__label.setText("Add a logical permission delegate")
        delegate_mngr = self.__rpa.session_api.delegate_mngr
        delegate_mngr.add_permission_delegate(
            self.__rpa.session_api.create_clips, self.__permissions_create_clips)
        print(delegate_mngr.get_permission_delegates(self.__rpa.session_api.create_clips))

    def __clear_all_permission_delegates(self):
        self.__label.setText("Clear all permission delegates")
        delegate_mngr = self.__rpa.session_api.delegate_mngr
        delegate_mngr.clear_permission_delegates(
            self.__rpa.session_api.create_clips)
        print(delegate_mngr.get_permission_delegates(self.__rpa.session_api.create_clips))

    def __permissions_2(self):
        self.__label.setText("Remove the permission delegate that returns False")
        delegate_mngr = self.__rpa.session_api.delegate_mngr
        delegate_mngr.remove_permission_delegate(
            self.__rpa.session_api.create_clips, self.__return_false)

        print(delegate_mngr.get_permission_delegates(self.__rpa.session_api.create_clips))

    def __permissions_1(self):
        self.__label.setText("Add 2 permission delegates, one returning False")
        delegate_mngr = self.__rpa.session_api.delegate_mngr
        delegate_mngr.add_permission_delegate(
            self.__rpa.session_api.create_clips, self.__return_true)
        delegate_mngr.add_permission_delegate(
            self.__rpa.session_api.create_clips, self.__return_false)

        print(delegate_mngr.get_permission_delegates(self.__rpa.session_api.create_clips))

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
