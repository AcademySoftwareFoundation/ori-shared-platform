from dataclasses import dataclass, field, fields
import os
from rpa.utils.sequential_uuid_generator import SequentialUUIDGenerator
import uuid


@dataclass
class Feedback:
    is_visible:bool = True
    are_strokes_visible:bool = True
    are_texts_visible:bool = True
    are_clip_ccs_visible:bool = True
    are_frame_ccs_visible:bool = True
    are_region_ccs_visible:bool = True
    annotation_ghosting:bool = False
    annotation_holding:bool = False

@dataclass
class Transforms:
    flip_x:bool = False
    flip_y:bool = False


class TextCursor:
    def __init__(self):
        self.__position = None
        self.__size = None

    @property
    def position(self):
        return self.__position

    @property
    def size(self):
        return self.__size

    def set(self, position, size):
        self.__position = position
        self.__size = size

    def is_set(self):
        if self.__position and self.__size:
            return True
        return False

    def unset(self):
        self.__position = None
        self.__size = None

@dataclass
class HtmlOverlay:
    html:str = ""
    x:float = 0.5
    y:float = 0.5
    width:float = 500
    height:float = 500
    bg_opacity:float = 0.0
    is_visible:bool = True
    use_web_engine:bool = False
    placement:str = None
    border_width:float = 0.0
    border_color:list[float] = field(default_factory=lambda: [1.0, 1.0, 1.0, 1.0])
    border_dashed:bool = False
    content_width:object = None
    content_height:object = None
    __custom_attrs: dict = field(default_factory=dict)

    def set_custom_attr(self, attr_id, value):
        self.__custom_attrs[attr_id] = value
        return True

    def get_custom_attr(self, attr_id):
        return self.__custom_attrs.get(attr_id)

    def get_custom_attr_ids(self):
        return list(self.__custom_attrs.keys())


class Viewport:
    def __init__(self):
        self.__fg = None
        self.__bg = None
        self.current_clip = None
        self.bg_mode = 0
        self.source_frame_lock = False
        self.mix_mode = 0
        self.feedback = Feedback()
        self.__transforms = Transforms()
        self.color_channel = 4
        self.fstop = 0.0
        self.gamma = 1.0
        self.rotation = 0
        self.__text_cursor = TextCursor()
        self.__cross_hair_cursor = None
        seed = os.environ.get("HTML_OVERLAY_UUID_SEED")
        if seed is None: seed = uuid.uuid4().hex
        self.__overlay_uuid_generator = SequentialUUIDGenerator(seed)
        self.__html_overlays = {}
        self.__opengl_overlays: dict[str, OpenGlOverlay] = {}
        self.__current_clip_geometry = None
        self.mask = None

    def create_html_overlay(self, html_overlay_data):
        overlay_id = self.__overlay_uuid_generator.next_uuid()
        self.__html_overlays[overlay_id] = HtmlOverlay(**html_overlay_data)
        return overlay_id

    def set_html_overlay(self, id, html_overlay_data):
        html_overlay = self.__html_overlays.get(id)
        if html_overlay is None: return False
        field_names = {f.name for f in fields(html_overlay)}
        for key, value in html_overlay_data.items():
            if key in field_names:
                setattr(html_overlay, key, value)
        return True

    def get_html_overlay(self, overlay_id):
        return self.__html_overlays.get(overlay_id)

    def get_html_overlay_data(self, id):
        html_overlay = self.__html_overlays.get(id)
        if html_overlay is None: return False
        out = {
            "html": html_overlay.html,
            "x": html_overlay.x,
            "y": html_overlay.y,
            "width": html_overlay.width,
            "height": html_overlay.height,
            "is_visible": html_overlay.is_visible
        }
        return out

    def get_html_overlays(self):
        return list(self.__html_overlays.values())

    def get_html_overlay_ids(self):
        return list(self.__html_overlays.keys())

    def delete_html_overlays(self, ids):
        for id in ids: self.__html_overlays.pop(id, None)
        return True

    def create_opengl_overlay(self, recipe):
        overlay_id = self.__overlay_uuid_generator.next_uuid()
        self.__opengl_overlays[overlay_id] = recipe
        return overlay_id

    def set_opengl_overlay(self, id, recipe):
        opengl_overlay = self.__opengl_overlays.get(id)
        if opengl_overlay is None: return False
        opengl_overlay.update(recipe)
        self.__opengl_overlays[id] = opengl_overlay
        return True

    def get_opengl_overlay(self, id):
        return self.__opengl_overlays[id]

    def get_opengl_overlays(self):
        return list(self.__opengl_overlays.values())

    def get_opengl_overlay_ids(self):
        return list(self.__opengl_overlays.keys())

    def delete_opengl_overlays(self, ids):
        for id in ids:
            self.__opengl_overlays.pop(id, None)
        return True

    @property
    def fg(self):
        return self.__fg

    @fg.setter
    def fg(self, id):
        if id is None:
            self.__fg, self.__bg = None, None
            return
        if self.__fg == id: return
        if self.__bg == id:
            self.__fg, self.__bg = self.__bg, self.__fg
        else:
            self.__fg = id

    @property
    def bg(self):
        return self.__bg

    @bg.setter
    def bg(self, id):
        if self.__bg == id: return
        if id is None:
            self.__bg = None
            return
        if self.__fg == id:
            self.__bg = None
        else:
            self.__bg = id

    @property
    def transforms(self):
        return self.__transforms

    def set_text_cursor(self, position, size):
        return self.__text_cursor.set(position, size)

    def is_text_cursor_set(self):
        return self.__text_cursor.is_set()

    def unset_text_cursor(self):
        return self.__text_cursor.unset()

    def set_cross_hair_cursor(self, position):
        self.__cross_hair_cursor = position

    @property
    def text_cursor(self):
        return self.__text_cursor

    @property
    def cross_hair_cursor(self):
        return self.__cross_hair_cursor

    def set_current_clip_geometry(self, geometry):
        self.__current_clip_geometry = geometry

    def get_current_clip_geometry(self):
        return self.__current_clip_geometry