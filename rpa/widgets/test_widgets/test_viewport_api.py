from PySide2 import QtCore, QtWidgets
from functools import partial
import os


TEST_MEDIA_DIR = os.environ.get("TEST_MEDIA_DIR")


class TestViewportApi:

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
            print("For overlays, make sure there is a png image with opacity with the name one.png")
            print("For masks, make sure there is a tif image with opacity with the name one.tif")
            return
        
        tests = [
            partial(self.__create_clips),
            partial(self.__create_html_overlay),
            partial(self.__set_html_overlay),
            partial(self.__hide_html_overlay),
            partial(self.__show_html_overlay),
            partial(self.__get_html_overlay),
            partial(self.__delete_html_overlays),
            partial(self.__set_mask_1),
            partial(self.__remove_mask),
            partial(self.__get_current_clip_geometry),
            partial(self.__scale_on_point_1),
            partial(self.__scale_on_point_2),
            partial(self.__scale_on_point_3),
            partial(self.__scale_on_point_4),
            partial(self.__scale_on_point_5),
            partial(self.__scale_on_point_1),
            partial(self.__drag),
            partial(self.__set_scale_1),
            partial(self.__set_scale_2),
            partial(self.__set_scale_3),
            partial(self.__set_scale_4),
            partial(self.__flip_x_1),
            partial(self.__flip_x_2),
            partial(self.__flip_y_1),
            partial(self.__flip_y_2),
            partial(self.__fit_to_window_1),
            partial(self.__fit_to_window_2),
            partial(self.__fit_to_width_1),
            partial(self.__fit_to_width_2),
            partial(self.__fit_to_height_1),
            partial(self.__fit_to_height_2),
            partial(self.__fit_to_window_1),
            partial(self.__fit_to_window_1),
            partial(self.__display_msg_1),
            partial(self.__set_mask_1),
            partial(self.__display_msg_1),
            partial(self.__scale_on_point_1),
            partial(self.__scale_on_point_2),
            partial(self.__scale_on_point_3),
            partial(self.__scale_on_point_4),
            partial(self.__scale_on_point_5),
            partial(self.__scale_on_point_1),
            partial(self.__drag),
            partial(self.__set_scale_1),
            partial(self.__set_scale_2),
            partial(self.__set_scale_3),
            partial(self.__set_scale_4),
            partial(self.__flip_x_1),
            partial(self.__flip_x_2),
            partial(self.__flip_y_1),
            partial(self.__flip_y_2),
            partial(self.__fit_to_window_1),
            partial(self.__fit_to_window_2),
            partial(self.__fit_to_width_1),
            partial(self.__fit_to_width_2),
            partial(self.__fit_to_height_1),
            partial(self.__fit_to_height_2),
            partial(self.__fit_to_window_1),
            partial(self.__fit_to_window_1),
            partial(self.__remove_mask)
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

    def __create_html_overlay(self):
        self.__label.setText("create_html_overlay")
        html_1 = """
<h1 style='color:green;text-align: center; font-size:62px'><u>HTML Overlay 1</u></h1>
<p>&nbsp;</p>
<table class="demoTable" style="height: 47px;">
<thead>
<tr style="height: 18px; font-size:42px">
<td style="height: 18px; width: 500px;"><span style="color: red;">Header 1</span></td>
<td style="height: 18px; width: 302.188px;"><span style="color: red;">Header 2</span></td>
<td style="height: 18px; width: 302.188px;"><span style="color: red;">Header 3</span></td>
</tr>
</thead>
<tbody>
<tr style="height: 29px; font-size:32px">
<td style="height: 29px; width: 500px; color: blue"><b>Value 1</b></td>
<td style="height: 29px; width: 302.188px; color: yellow"><u>Value 2</u></td>
<td style="height: 29px; width: 302.188px; color: green"><i>Value 3</i></td>
</tr>
</tbody>
</table>
"""
        html_2 = """
<h1 style='color:green;text-align: center; font-size:62px'><u>HTML Overlay 2</u></h1>
<p>&nbsp;</p>
<table class="demoTable" style="height: 47px;">
<thead>
<tr style="height: 18px; font-size:42px">
<td style="height: 18px; width: 500px;"><span style="color: red;">Header 1</span></td>
<td style="height: 18px; width: 302.188px;"><span style="color: red;">Header 2</span></td>
<td style="height: 18px; width: 302.188px;"><span style="color: red;">Header 3</span></td>
</tr>
</thead>
<tbody>
<tr style="height: 29px; font-size:32px">
<td style="height: 29px; width: 500px; color: blue"><b>Value 1</b></td>
<td style="height: 29px; width: 302.188px; color: yellow"><u>Value 2</u></td>
<td style="height: 29px; width: 302.188px; color: green"><i>Value 3</i></td>
</tr>
</tbody>
</table>
"""
        self.overlay_id_1 = self.__rpa.viewport_api.create_html_overlay({
            "html":html_1, "x":0.5, "y":0.6, "width":500, "height":500})
        self.overlay_id_2 = self.__rpa.viewport_api.create_html_overlay({
            "html":html_2, "x":0.1, "y":0.3, "width":300, "height":500})
        self.overlay_id_3 = self.__rpa.viewport_api.create_html_overlay({
            "html":html_1, "x":0.7, "y":0.7, "width":400, "height":600})
        self.overlay_id_4 = self.__rpa.viewport_api.create_html_overlay({
            "html":html_2, "x":0.8, "y":0.2, "width":600, "height":750})

    def __set_html_overlay(self):
        self.__label.setText("__set_html_overlay")
        image_path = os.path.join(TEST_MEDIA_DIR, "one.png")
        html_3 = f"""<img src="{image_path}">"""
        self.__rpa.viewport_api.set_html_overlay(self.overlay_id_4, {"html":html_3})
        self.__rpa.viewport_api.set_html_overlay(
            self.overlay_id_3,
            {"html":html_3, "x":0.1, "y":0.3, "width":300, "height":400})

    def __hide_html_overlay(self):
        self.__label.setText("__hide_html_overlay")
        self.__rpa.viewport_api.set_html_overlay(self.overlay_id_1, {"is_visible":False})
        self.__rpa.viewport_api.set_html_overlay(self.overlay_id_2, {"is_visible":False})

    def __show_html_overlay(self):
        self.__label.setText("__show_html_overlay")
        self.__rpa.viewport_api.set_html_overlay(
            self.overlay_id_1, {"is_visible":True})
        self.__rpa.viewport_api.set_html_overlay(
            self.overlay_id_2, {"is_visible":True})

    def __get_html_overlay(self):
        self.__label.setText("__get_html_overlay")
        ids = self.__rpa.viewport_api.get_html_overlay_ids()
        print("num of html overlays: ", len(ids))
        print("html overlays ids: ", ids)
        html_overlay = self.__rpa.viewport_api.get_html_overlay(ids[0])
        print("html_overlay", html_overlay)

    def __delete_html_overlays(self):
        self.__label.setText("__delete_html_overlays")
        ids = self.__rpa.viewport_api.get_html_overlay_ids()
        print("num of html overlays: ", len(ids))
        is_success = self.__rpa.viewport_api.delete_html_overlays(ids)
        print("html_overlay", is_success)
        ids = self.__rpa.viewport_api.get_html_overlay_ids()
        print("num of html overlays: ", len(ids))

    def __display_msg_1(self):
        self.__label.setText("display_msg")
        self.__rpa.viewport_api.display_msg("Resilient")

    def __fit_to_height_1(self):
        self.__label.setText("fit_to_height_1")
        self.__rpa.viewport_api.fit_to_height(True)

    def __fit_to_height_2(self):
        self.__label.setText("fit_to_height_2")
        self.__rpa.viewport_api.fit_to_height(False)

    def __fit_to_width_1(self):
        self.__label.setText("fit_to_width_1")
        self.__rpa.viewport_api.fit_to_width(True)

    def __fit_to_width_2(self):
        self.__label.setText("fit_to_width_2")
        self.__rpa.viewport_api.fit_to_width(False)

    def __fit_to_window_1(self):
        self.__label.setText("toggle_fit_to_window_1")
        self.__rpa.viewport_api.fit_to_window(True)

    def __fit_to_window_2(self):
        self.__label.setText("fit_to_window_2")
        self.__rpa.viewport_api.fit_to_window(False)

    def __flip_x_1(self):
        self.__label.setText("flip_x_1")
        self.__rpa.viewport_api.flip_x(True)

    def __flip_x_2(self):
        self.__label.setText("flip_x_2")
        self.__rpa.viewport_api.flip_x(False)

    def __flip_y_1(self):
        self.__label.setText("flip_y_1")
        self.__rpa.viewport_api.flip_y(True)

    def __flip_y_2(self):
        self.__label.setText("flip_y_2")
        self.__rpa.viewport_api.flip_y(False)

    def __set_scale_1(self):
        self.__label.setText("set_scale_1")
        self.__rpa.viewport_api.set_scale(2, 1)
        print(self.__rpa.viewport_api.get_scale())

    def __set_scale_2(self):
        self.__label.setText("set_scale_2")
        self.__rpa.viewport_api.set_scale(1, 2)
        print(self.__rpa.viewport_api.get_scale())

    def __set_scale_3(self):
        self.__label.setText("set_scale_3")
        self.__rpa.viewport_api.set_scale(3)
        print(self.__rpa.viewport_api.get_scale())

    def __set_scale_4(self):
        self.__label.setText("set_scale_3")
        self.__rpa.viewport_api.set_scale(1)
        print(self.__rpa.viewport_api.get_scale())

    def __drag(self):
        self.__label.setText("drag")
        self.__rpa.viewport_api.start_drag((500, 230))
        self.__rpa.viewport_api.drag((400, 130))
        self.__rpa.viewport_api.end_drag()

    def __scale_on_point_1(self):
        self.__label.setText("scale_on_point_1")
        self.__rpa.viewport_api.scale_on_point(
            (500, 230), 1.0, 1, False, False)
        print(self.__rpa.viewport_api.get_scale())

    def __scale_on_point_2(self):
        self.__label.setText("scale_on_point_2")
        self.__rpa.viewport_api.scale_on_point(
            (500, 230), -1.0, 1, False, False)
        print(self.__rpa.viewport_api.get_scale())

    def __scale_on_point_3(self):
        self.__label.setText("scale_on_point_3")
        self.__rpa.viewport_api.scale_on_point(
            (500, 230), -1.0, 1, True, False)
        print(self.__rpa.viewport_api.get_scale())

    def __scale_on_point_4(self):
        self.__label.setText("scale_on_point_4")
        self.__rpa.viewport_api.scale_on_point(
            (500, 230), -1.0, 1, False, True)
        print(self.__rpa.viewport_api.get_scale())

    def __scale_on_point_5(self):
        self.__label.setText("scale_on_point_5")
        self.__rpa.viewport_api.scale_on_point(
            (500, 130), 1.0, 1, True, True)
        print(self.__rpa.viewport_api.get_scale())

    def __get_current_clip_geometry(self):
        self.__label.setText("get_current_clip_geometry")
        print(self.__rpa.viewport_api.get_current_clip_geometry())

    def __set_mask_1(self):
        self.__label.setText("set_mask_1")        
        self.__rpa.viewport_api.set_mask(os.path.join(TEST_MEDIA_DIR, "one.tif"),)

    def __remove_mask(self):
        self.__label.setText("remove_mask")
        self.__rpa.viewport_api.set_mask(None)

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
