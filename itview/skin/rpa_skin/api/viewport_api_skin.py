from PySide2 import QtCore
from itview.skin.rpa_skin.attr_utils import make_callables, connect_signals
from typing import List, Optional, Tuple


class ViewportApiSkin(QtCore.QObject):
    SIG_CURRENT_CLIP_GEOMETRY_CHANGED = QtCore.Signal(object) # geometry

    def __init__(self, rpa_tx, session):
        super().__init__()
        self.__rpa_tx = rpa_tx
        self.__session = session
        make_callables(self.__rpa_tx, self)
        connect_signals(self.__rpa_tx, self)

        self.SIG_CURRENT_CLIP_GEOMETRY_CHANGED.connect(
            self.__session.viewport.set_current_clip_geometry)

    def create_html_overlay(self, html_overlay):
        self.__session.viewport.create_html_overlay(html_overlay)
        return self.__rpa_tx.create_html_overlay(html_overlay)

    def set_html_overlay(self, id:str, html_overlay):
        self.__session.viewport.set_html_overlay(id, html_overlay)
        return self.__rpa_tx.set_html_overlay(id, html_overlay)

    def get_html_overlay(self, id:str):
        return self.__session.viewport.get_html_overlay_data(id)

    def get_html_overlay_ids(self):
        return self.__session.viewport.get_html_overlay_ids()

    def delete_html_overlays(self, ids):
        self.__session.viewport.delete_html_overlays(ids)
        return self.__rpa_tx.delete_html_overlays(ids)

    def create_opengl_overlay(self, recipe: dict) -> str:
        self.__session.viewport.create_opengl_overlay(recipe)
        return self.__rpa_tx.create_opengl_overlay(recipe)

    def set_opengl_overlay(self, id: str, recipe: dict) -> bool:
        self.__session.viewport.set_opengl_overlay(id, recipe)
        return self.__rpa_tx.set_opengl_overlay(id, recipe)

    def get_opengl_overlay_ids(self) -> List[str]:
        return self.__session.viewport.get_opengl_overlay_ids()

    def delete_opengl_overlays(self, ids: List[str]) -> bool:
        self.__session.viewport.delete_opengl_overlays(ids)
        return self.__rpa_tx.delete_opengl_overlays(ids)

    def is_flipped_x(self):
        return self.__session.viewport.transforms.flip_x

    def flip_x(self, state):
        self.__session.viewport.transforms.flip_x = state
        return self.__rpa_tx.flip_x(state)

    def is_flipped_y(self):
        return self.__session.viewport.transforms.flip_y

    def flip_y(self, state):
        self.__session.viewport.transforms.flip_y = state
        return self.__rpa_tx.flip_y(state)

    def is_feedback_visible(self, category:int)-> bool:
        return self.__session.viewport.feedback.is_visible

    def set_feedback_visibility(self, category:int, value:bool):
        self.__session.viewport.feedback.is_visible = value
        self.__rpa_tx.set_feedback_visibility(category, value)

    def set_text_cursor(self, position, size)-> bool:
        self.__session.viewport.set_text_cursor(position, size)
        return self.__rpa_tx.set_text_cursor(position, size)

    def is_text_cursor_set(self)-> bool:
        return self.__session.viewport.is_text_cursor_set()

    def unset_text_cursor(self)-> bool:
        self.__session.viewport.unset_text_cursor()
        return self.__rpa_tx.unset_text_cursor()

    def set_cross_hair_cursor(self, position)-> bool:
        self.__session.viewport.set_cross_hair_cursor(position)
        return self.__rpa_tx.set_cross_hair_cursor(position)

    def get_current_clip_geometry(self)-> Optional[List[Tuple[float, float]]]:
        return self.__session.viewport.get_current_clip_geometry()

    def set_rotation(self, angle):
        self.__session.viewport.rotation = angle
        return self.__rpa_tx.set_rotation(angle)

    def get_rotation(self):
        return self.__session.viewport.rotation

    def get_mask(self):
        return self.__session.viewport.mask

    def set_mask(self, mask):
        self.__session.viewport.mask = mask
        return self.__rpa_tx.set_mask(mask)
