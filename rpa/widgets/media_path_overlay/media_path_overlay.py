from typing import List
from PySide2 import QtCore, QtWidgets
import os


class MediaPathOverlay(QtWidgets.QWidget):

    def __init__(self, rpa, main_window):
        super().__init__(main_window)        
        self.__rpa = rpa

        html_overlay = {
            "html": "N/A",
            "x": 0.5,
            "y": 0.5,
            "width": 700,
            "height": 100,
            "is_visible": False
        }
        self.__overlay_id = self.__rpa.viewport_api.create_html_overlay(
            html_overlay)
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        self.__info_icon_path = os.path.join(current_dir, "info.png")

        # Create toggleable push button
        self.__show_media_path_btn = QtWidgets.QPushButton("Show Media Path")
        self.__show_media_path_btn.setCheckable(True)
        self.__show_media_path_btn.setStyleSheet(self._get_style(False))  # Initial unpressed style

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.__show_media_path_btn)
        self.setLayout(layout)
        
        self.__show_media_path_btn.toggled.connect(self.__on_toggled)
        self.__show_media_path_btn.toggled.connect(self.__toggle_media_path)
        self.__rpa.session_api.SIG_CURRENT_CLIP_CHANGED.connect(
            self.__clip_changed)
    
    def __clip_changed(self):        
        self.__rpa.viewport_api.set_html_overlay(
            self.__overlay_id, {"html":self.__get_html()})

    def __on_toggled(self, checked):
        # Update style based on state
        self.__show_media_path_btn.setStyleSheet(self._get_style(checked))

    def __toggle_media_path(self, checked):        
        self.__rpa.viewport_api.set_html_overlay(self.__overlay_id, {
            "is_visible":checked,
            "html":self.__get_html()
        })

    def __get_html(self):
        clip_id = self.__rpa.session_api.get_current_clip()
        media_path = self.__rpa.session_api.get_attr_value(clip_id, "media_path")
        html =f'<p><img src={self.__info_icon_path}>'\
            f'<b><u style="font-size: 24px; color:red;">Media Path:</u></b></p>'\
            f'<p style="font-size: 20px; color:white;">{media_path}</p><br></p>'
        return html

    def _get_style(self, checked):
        if checked:
            return """
                QPushButton {
                    background-color: #28a745;  /* Green */
                    color: white;
                    font-weight: bold;
                    border: 2px solid #1e7e34;
                    border-radius: 6px;
                    font-size: 16px;
                    padding: 8px;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #cccccc;  /* Light gray */
                    color: black;
                    font-weight: normal;
                    border: 2px solid #999999;
                    border-radius: 6px;
                    font-size: 16px;
                    padding: 8px;
                }
            """
