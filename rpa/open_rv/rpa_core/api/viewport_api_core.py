import math
import os
import re
from dataclasses import dataclass
import imageio.v3 as iio
import numpy as np
from OpenGL import GL
try:
    from PySide2 import QtGui, QtCore
except ImportError:
    from PySide6 import QtGui, QtCore
from rv import commands as rvc
from rv import extra_commands as rve
from rv import runtime
from rpa.open_rv.rpa_core.api import prop_util
from rpa.session_state.utils import Point, itview_to_screen


def render_html_to_image(width, height, html):
    doc = QtGui.QTextDocument()
    doc.setHtml(html)
    doc.setTextWidth(width)

    image = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)
    image.fill(QtCore.Qt.transparent)

    painter = QtGui.QPainter(image)
    doc.drawContents(painter)
    painter.end()

    image = image.mirrored(False, True)
    return image

def qimage_to_gl_texture(image):
    ptr = image.bits()
    ptr = ptr[: image.byteCount()]
    img_array = np.frombuffer(ptr, dtype=np.uint8).reshape(
        (image.height(), image.width(), 4))

    tex_id = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, tex_id)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, image.width(), image.height(), 0,
                    GL.GL_BGRA, GL.GL_UNSIGNED_BYTE, img_array)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    return tex_id


def _speed_pow2(value, speed=1.0, num=1.0):
    """
    Helper function to calculate new scale/zoom based on current scale, zoom speed and delta
    :param value: current scale
    :type value: float
    :param speed: zoom speed
    :type speed: float
    :param num: delta (positive of zoom in, negative for out)
    :type num: float
    :return: new scale
    :rtype: float
    """
    return 2.0 ** ((round(speed * math.log(abs(value)) / math.log(2)) + num) / speed)


@dataclass(frozen=True)
class FlipMode:
    NONE: str = "None"
    BOTH: str = "Both"
    HORIZ: str = "Horizontally"
    VERT: str = "Vertically"


class ViewportApiCore(QtCore.QObject):
    SIG_CURRENT_CLIP_GEOMETRY_CHANGED = QtCore.Signal(object) # geometry

    def __init__(
        self, session, session_api, annotation_api, color_api):
        super().__init__()
        self.__session = session
        self.__session_api = session_api
        self.__annotation_api = annotation_api
        self.__color_api = color_api

        # Masks
        self.__width = 1024
        self.__height = 1024
        self.__texture = None
        self.__display = None
        self.__recipes = []

        # Overlays
        self.__active_html_overlay = None

        # Transforms
        self.__start_pointer = None
        self.__cache_scale = [None, None]
        self.__cache_translation = [None, None]
        self.__transform = False
        self.__dynamic_transform = False
        self.__frame = None

        self.__viewport_widget = None
        self.__last_mouse_pos = [0.0, 0.0]

        self.__last_geometry = None

    def create_html_overlay(self, html_overlay):
        id = self.__session.viewport.create_html_overlay(html_overlay)
        html_overlay = self.__session.viewport.get_html_overlay(id)
        self.__set_html_overlay_texture(html_overlay)
        return id

    def set_html_overlay(self, id:str, html_overlay):
        is_success = \
            self.__session.viewport.set_html_overlay(id, html_overlay)
        if is_success:
            html_overlay = self.__session.viewport.get_html_overlay(id)
            self.__set_html_overlay_texture(html_overlay)
        return is_success

    def __set_html_overlay_texture(self, html_overlay):
        old_texture_id = html_overlay.get_custom_attr("gl_texture_id")
        if old_texture_id is not None:
            GL.glDeleteTextures([old_texture_id])
        image = render_html_to_image(
            html_overlay.width, html_overlay.height, html_overlay.html)
        texture_id = qimage_to_gl_texture(image)
        html_overlay.set_custom_attr("gl_texture_id", texture_id)
        rvc.redraw()

    def get_html_overlay(self, id:str):
        return self.__session.viewport.get_html_overlay_data(id)

    def get_html_overlay_ids(self):
        return self.__session.viewport.get_html_overlay_ids()

    def delete_html_overlays(self, ids):
        is_success = self.__session.viewport.delete_html_overlays(ids)
        rvc.redraw()
        return is_success

    def start_drag(self, pointer):
        self.__down_point = rve.translation()
        self.__start_pointer = (float(pointer[0]), float(pointer[1]))
        return True

    def drag(self, pointer):
        if self.__start_pointer is None:
            return

        pointer = (float(pointer[0]), float(pointer[1]))
        pixel_info = rvc.sourceAtPixel(pointer)
        if len(pixel_info) == 0:
            return False
        current_camera_space = \
            rvc.eventToCameraSpace(pixel_info[0]["name"], pointer)
        reference_camera_space = rvc.eventToCameraSpace(
                pixel_info[0]["name"], self.__start_pointer)
        camera_space_change = [current_camera_space[0] - reference_camera_space[0],
                               current_camera_space[1] - reference_camera_space[1]]

        current_scale = rvc.getFloatProperty("#RVDispTransform2D.transform.scale")
        h_scale = current_scale[0]
        v_scale = current_scale[1]
        diff = [self.__down_point[0] + (camera_space_change[0] / h_scale),
                self.__down_point[1] + (camera_space_change[1] / v_scale)]
        self.set_translation(*diff)
        return True

    def end_drag(self):
        self.__start_pointer = None
        self.__down_point = None
        return True

    def get_current_clip_geometry(self):
        clip_id = self.__session.viewport.current_clip
        if not clip_id: return
        clip = self.__session.get_clip(self.__session.viewport.current_clip)
        source_node = clip.get_custom_attr("rv_source_group")
        if not source_node: return
        return rvc.imageGeometry(f"{source_node}_source")

    def scale_on_point(
        self, scale_point, delta, speed, vertical_lock, horizontal_lock):
        old_scale = rvc.getFloatProperty("#RVDispTransform2D.transform.scale")
        x_sign = -1.0 if old_scale[0] < 0 else 1.0
        y_sign = -1.0 if old_scale[1] < 0 else 1.0
        new_scale = list(old_scale)
        if not horizontal_lock:
            new_scale[0] = _speed_pow2(old_scale[0], speed, delta)
        if not vertical_lock:
            new_scale[1] = _speed_pow2(old_scale[1], speed, delta)

        margins = rvc.margins()
        view_size = rvc.viewSize()
        center = [float(view_size[0] - margins[0] - margins[1]) / 2.0 + float(margins[0]),
                  float(view_size[1] - margins[2] - margins[3]) / 2.0 + float(margins[3])]
        normalizer = max(float(view_size[1] - margins[2] - margins[3]), 0.01)
        focus = [((center[0] - scale_point[0]) / (abs(old_scale[0]) * normalizer)),
                 ((center[1] - scale_point[1]) / (abs(old_scale[1]) * normalizer))]
        focus = [focus[0] * x_sign, focus[1] * y_sign]

        down_point = rve.translation()
        diff = [(focus[0] / abs(old_scale[0]) - focus[0] / new_scale[0]) * abs(old_scale[0]) + down_point[0],
                (focus[1] / abs(old_scale[1]) - focus[1] / new_scale[1]) * abs(old_scale[1]) + down_point[1]]

        new_scale = [new_scale[0] * x_sign, new_scale[1] * y_sign]

        self.set_translation(0.0, 0.0)
        self.set_scale(*new_scale)
        self.set_translation(*diff)
        return True

    def set_scale(self, horizontal, vertical=None):
        self.__cache_scale = self.get_scale()
        horizontal = float(horizontal)
        if vertical: vertical = float(vertical)
        else: vertical = horizontal
        rvc.setFloatProperty(
            "#RVDispTransform2D.transform.scale", [horizontal, vertical])
        return True

    def get_scale(self):
        return prop_util.get_property("#RVDispTransform2D.transform.scale")[0]

    def flip_x(self, state):
        current_scale = \
            rvc.getFloatProperty("#RVDispTransform2D.transform.scale")
        current_h_scale = current_scale[0]
        current_v_scale = current_scale[1]
        new_h_scale = (current_h_scale * -1)

        current_translation = \
            rvc.getFloatProperty("#RVDispTransform2D.transform.translate")
        current_dx = current_translation[0]
        current_dy = current_translation[1]
        new_dx = (current_dx * -1)

        self.set_translation(0.0, 0.0)
        self.set_scale(new_h_scale, current_v_scale)
        self.set_translation(new_dx, current_dy)

        self.__session.viewport.transforms.flip_x = state

        new_scale = rvc.getFloatProperty("#RVDispTransform2D.transform.scale")
        h_scale = new_scale[0]
        v_scale = new_scale[1]

        if h_scale < 0 and v_scale < 0:
            mode = FlipMode.BOTH
        elif h_scale > 0 and v_scale < 0:
            mode = FlipMode.VERT
        elif h_scale < 0 and state:
            mode = FlipMode.HORIZ
        else:
            mode = FlipMode.NONE

        self.display_msg(f"Flipped: {mode}")
        return True

    def flip_y(self, state):
        current_scale = \
            rvc.getFloatProperty("#RVDispTransform2D.transform.scale")
        current_h_scale = current_scale[0]
        current_v_scale = current_scale[1]
        new_v_scale = (current_v_scale * -1)

        current_translation = \
            rvc.getFloatProperty("#RVDispTransform2D.transform.translate")
        current_dx = current_translation[0]
        current_dy = current_translation[1]
        new_dy = (current_dy * -1)

        self.set_translation(0.0, 0.0)
        self.set_scale(current_h_scale, new_v_scale)
        self.set_translation(current_dx, new_dy)

        self.__session.viewport.transforms.flip_y = state

        scale = rvc.getFloatProperty("#RVDispTransform2D.transform.scale")
        h_scale = scale[0]
        v_scale = scale[1]

        if h_scale < 0 and v_scale < 0:
            mode = FlipMode.BOTH
        elif h_scale < 0 and v_scale > 0:
            mode = FlipMode.HORIZ
        elif v_scale < 0 and state:
            mode = FlipMode.VERT
        else:
            mode = FlipMode.NONE

        self.display_msg(f"Flipped: {mode}")
        return True

    def fit_to_window(self, state):
        if state:
            view_width, view_height = rvc.viewSize()
            image_width, image_height = self.__get_current_dimensions()
            margins = rvc.margins()
            dimensions = [view_width - margins[0] - margins[1],
                          view_height - margins[2] - margins[3]]

            ia = image_width/image_height
            va = dimensions[0]/dimensions[1]

            new_scale = max(min(ia/va, va/ia), 1.0)
            translation = [0.0, 0.0]
        else:
            new_scale = self.__cache_scale[0] if self.__cache_scale[0] else 1.0
            translation = self.__cache_translation if self.__cache_translation[0] else [0.0, 0.0]
        self.set_scale(new_scale)
        self.set_translation(*translation)
        self.display_msg(f"Fit to Window: {'enabled' if state else 'disabled'}")
        return True

    def fit_to_width(self, state):
        if state:
            view_width, view_height = rvc.viewSize()
            image_width, image_height = self.__get_current_dimensions()
            margins = rvc.margins()
            dimensions = [view_width - margins[0] - margins[1],
                          view_height - margins[2] - margins[3]]

            ia = image_width/image_height
            va = dimensions[0]/dimensions[1]

            new_scale = 1.0 if ia>va else float(va/ia)
            translation = [0.0, 0.0]
            background_mode = self.__session_api.get_bg_mode()
            top_to_bottom = 3
            if background_mode == top_to_bottom:
                new_scale = 2.0
        else:
            new_scale = self.__cache_scale[0] if self.__cache_scale[0] else 1.0
            translation = self.__cache_translation if self.__cache_translation[0] else [0.0, 0.0]

        self.set_scale(new_scale)
        self.set_translation(*translation)
        self.display_msg(f"Fit to Width: {'enabled' if state else 'disabled'}")
        return True

    def fit_to_height(self, state):
        if state:
            view_width, view_height = rvc.viewSize()
            image_width, image_height = self.__get_current_dimensions()
            margins = rvc.margins()
            dimensions = [view_width - margins[0] - margins[1],
                          view_height - margins[2] - margins[3]]

            ia = image_height/image_width
            va = dimensions[1]/dimensions[0]

            new_scale = 1.0 if ia>va else float(va/ia)
            translation = [0.0, 0.0]
            background_mode = self.__session_api.get_bg_mode()
            side_by_side = 2
            if background_mode == side_by_side:
                new_scale = 2.0
        else:
            new_scale = self.__cache_scale[0] if self.__cache_scale[0] else 1.0
            translation = self.__cache_translation if self.__cache_translation[0] else [0.0, 0.0]
        self.set_scale(new_scale)
        self.set_translation(*translation)
        self.display_msg(f"Fit to Height: {'enabled' if state else 'disabled'}")
        return True

    def display_msg(self, message:str, duration:float=2.0):
        view_render_mu = \
            f"""require view_render;
            view_render.display_feedback("{message}", {duration});
            """
        runtime.eval(view_render_mu, [])
        return True

    def set_text_cursor(self, position, size)-> bool:
        clip_id = self.__session.viewport.current_clip
        if not clip_id: return False

        clip = self.__session.get_clip(clip_id)
        source_node = clip.get_custom_attr("rv_source_group")
        if not source_node: return False

        source_node = f"{source_node}_source"
        geometry = rvc.imageGeometry(source_node)
        position = Point(
            *itview_to_screen(geometry, position.x, position.y))
        is_success = self.__session.viewport.set_text_cursor(position, size)
        rvc.redraw()
        return is_success

    def is_text_cursor_set(self)-> bool:
        return self.__session.viewport.is_text_cursor_set()

    def unset_text_cursor(self)-> bool:
        is_success = self.__session.viewport.unset_text_cursor()
        rvc.redraw()
        return is_success

    def set_cross_hair_cursor(self, position)-> bool:
        clip_id = self.__session.viewport.current_clip
        if not clip_id: return False

        clip = self.__session.get_clip(clip_id)
        source_node = clip.get_custom_attr("rv_source_group")
        if not source_node: return False

        source_node = f"{source_node}_source"
        geometry = rvc.imageGeometry(source_node)
        if position:
            position = Point(
                *itview_to_screen(geometry, position.x, position.y))
        self.__session.viewport.set_cross_hair_cursor(position)
        rvc.redraw()
        return True

    def set_translation(self, dx, dy):
        """
        Set new camera location to display
        :param dx: x axis translation
        :type dx: float
        :param dy: y axis translation
        :type dy: float
        """
        self.__cache_translation = self.get_translation()
        rvc.setFloatProperty("#RVDispTransform2D.transform.translate", [float(dx), float(dy)])

    def __get_current_dimensions(self):
        """
        Get current dimension of the image
        :return: width, height of the current image, (0, 0) if no image rendered
        :rtype: tuple
        """
        sources = rvc.sourcesAtFrame(rvc.frame())
        if len(sources) == 0:
            return 0, 0
        smi = rvc.sourceMediaInfo(sources[0])
        return smi["width"], smi["height"]

    def get_translation(self):
        return prop_util.get_property("#RVDispTransform2D.transform.translate")[0]

    def set_mask(self, mask):
        self.__unload_mask()

        # No Mask
        if mask is None:
            return True

        # Mask: image path
        if os.path.exists(mask):
            # check for alpha channel
            image = iio.imread(mask)
            if image.shape[2] != 4:
                raise RuntimeError(f"Mask does not have an alpha channel: {mask}")
            # convert into floats if necessary
            if image.dtype == np.uint8:
                image = image.astype(np.float32)
                image /= 255.0
            elif image.dtype == np.uint16:
                image = image.astype(np.float32)
                image /= 65535.0
            height, width = image.shape[:2]

            self.__load_mask_image(width, height, image)

        # Mask: recipe
        elif self.__get_mask_recipes(mask):
            if self.__recipes:
                self.__display = GL.glGenLists(1)

        # Mask: none of the above
        else:
            return False

        return True

    def __unload_mask(self):
        if self.__texture is not None:
            GL.glDeleteTextures([self.__texture])
            self.__texture = None

        if self.__display is not None:
            GL.glDeleteLists(self.__display, 1)
            self.__display = None

    def __get_mask_recipes(self, mask):
        self.__recipes.clear()
        recipe_pattern = re.compile(r'([0-9.]+)(?:@([0-9.]+))?')
        match = recipe_pattern.match(mask)
        if match is not None:
            for recipe in mask.split("&"):
                match = recipe_pattern.match(recipe)
                if match is not None:
                    ratio = float(match.group(1))
                    opacity = float(match.group(2)) if match.group(2) else 1.0
                    self.__recipes.append((ratio, opacity))
        return True

    def __load_mask_image(self, width, height, data):
        self.__width = width
        self.__height = height

        self.__texture = GL.glGenTextures(1)

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.__texture)

        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0, GL.GL_RGBA, GL.GL_FLOAT, data)

    def __get_mask_rect(self, width, height, geometry, translate_x, translate_y, scale_x, scale_y, rotation=None):
        g = [np.array(p) for p in geometry]
        center = 0.5 * (g[0] + g[2])
        size = np.array([
            scale_x * np.linalg.norm(g[1] - g[0]),
            scale_y * np.linalg.norm(g[3] - g[0])])
        pixel_size = size / np.array([width, height])
        translate = np.array([translate_x, translate_y]) * pixel_size
        lb = center + translate - 0.5 * size
        rt = lb + size
        rb = np.array([rt[0], lb[1]])
        lt = np.array([lb[0], rt[1]])

        if rotation is not None:
            transformed_center = 0.5 * (lb + rt)
            def rotate_point(point, center, angle):
                theta = np.radians(-angle)
                rotation_matrix = np.array(
                [[np.cos(theta), -np.sin(theta)],
                 [np.sin(theta), np.cos(theta)]])
                return center + np.dot(rotation_matrix, (point - center))
            lb = rotate_point(lb, transformed_center, rotation)
            rb = rotate_point(rb, transformed_center, rotation)
            rt = rotate_point(rt, transformed_center, rotation)
            lt = rotate_point(lt, transformed_center, rotation)

        return lb, rb, rt, lt

    def __render_mask(self, event):
        if self.__texture is None and self.__display is None:
            return

        if self.__texture:
            self.__render_mask_image(event)
        elif self.__display:
            self.__render_mask_recipe(event)

    def __render_mask_image(self, event):
        frame = rvc.frame() # global frame
        src_frame = rve.sourceFrame(frame) # source frame
        clip_id = self.__session_api.get_current_clip()
        if clip_id is None:
            return
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        if playlist_id is None:
            return

        sources = rvc.sourcesAtFrame(frame)
        if len(sources) != 1:
            return
        source = sources[0]
        smi = rvc.sourceMediaInfo(source)
        geometry = rvc.imageGeometry(source)

        img_width = float(smi["width"])
        img_height = float(smi["height"])

        # get translate and scale
        translate_x = self.__session_api.get_attr_value(clip_id, "pan_x")
        translate_x += self.__session_api.get_attr_value_at(clip_id, "dynamic_translate_x", src_frame)
        translate_y = self.__session_api.get_attr_value(clip_id, "pan_y")
        translate_y += self.__session_api.get_attr_value_at(clip_id, "dynamic_translate_y", src_frame)
        scale_x = self.__session_api.get_attr_value(clip_id, "scale_x")
        scale_x *= self.__session_api.get_attr_value_at(clip_id, "dynamic_scale_x", src_frame)
        scale_y = self.__session_api.get_attr_value(clip_id, "scale_y")
        scale_y *= self.__session_api.get_attr_value_at(clip_id, "dynamic_scale_y", src_frame)

        lb, rb, rt, lt = self.__get_mask_rect(
            img_width, img_height, geometry, -translate_x, -translate_y, 1.0/scale_x, 1.0/scale_y)
        x0, y0 = lb
        x1, y1 = rt

        domain = event.domain()

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, domain[0], 0, domain[1], -1000000, +1000000)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.__texture)

        # check for horizontal flip coordinates
        if x0 > x1:
            x0, x1 = x1, x0

        # fit to width
        w = x1 - x0
        h = self.__height * w / self.__width
        p = 0.5 * (y1 - y0 - h)
        X0 = x0
        X1 = x1
        Y0 = y0 + p + h
        Y1 = y0 + p

        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0, 0)
        GL.glVertex2f(X0, Y0)
        GL.glTexCoord2f(1, 0)
        GL.glVertex2f(X1, Y0)
        GL.glTexCoord2f(1, 1)
        GL.glVertex2f(X1, Y1)
        GL.glTexCoord2f(0, 1)
        GL.glVertex2f(X0, Y1)
        GL.glEnd()

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        GL.glDisable(GL.GL_BLEND)
        GL.glDisable(GL.GL_TEXTURE_2D)

    def __render_mask_recipe(self, event):
        domain = event.domain()
        frame = rvc.frame() # global frame
        src_frame = rve.sourceFrame(frame) # source frame
        clip_id = self.__session_api.get_current_clip()
        if clip_id is None:
            return
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        if playlist_id is None:
            return

        sources = rvc.sourcesAtFrame(frame)
        if len(sources) != 1:
            return

        source = sources[0]
        smi = rvc.sourceMediaInfo(source)
        geometry = rvc.imageGeometry(source)

        img_width = float(smi["width"])
        img_height = float(smi["height"])
        img_ratio = img_width / img_height

        # get translate and scale
        translate_x = self.__session_api.get_attr_value(
            clip_id, "pan_x")
        translate_x += self.__session_api.get_attr_value_at(
            clip_id, "dynamic_translate_x", src_frame)
        translate_y = self.__session_api.get_attr_value(
            clip_id, "pan_y")
        translate_y += self.__session_api.get_attr_value_at(
            clip_id, "dynamic_translate_y", src_frame)
        scale_x = self.__session_api.get_attr_value(
            clip_id, "scale_x")
        scale_x *= self.__session_api.get_attr_value_at(
            clip_id, "dynamic_scale_x", src_frame)
        scale_y = self.__session_api.get_attr_value(
            clip_id, "scale_y")
        scale_y *= self.__session_api.get_attr_value_at(
            clip_id, "dynamic_scale_y", src_frame)

        lb, rb, rt, lt = self.__get_mask_rect(
            img_width, img_height, geometry, -translate_x, -translate_y, 1.0/scale_x, 1.0/scale_y)
        lbx, lby = lb
        rbx, rby = rb
        rtx, rty = rt
        ltx, lty = lt

        GL.glNewList(self.__display, GL.GL_COMPILE)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        GL.glBegin(GL.GL_QUADS)
        for mask_ratio, opacity in self.__recipes:
            # TOP & BOTTOM
            if img_ratio <= mask_ratio:
                mask_height = ((rty - rby) - ((rtx - ltx) / mask_ratio)) / 2
                GL.glColor4f(0.0, 0.0, 0.0, opacity)
                # BOTTOM
                GL.glVertex2f(lbx, lby)
                GL.glVertex2f(rbx, rby)
                GL.glVertex2f(rbx, rby + mask_height)
                GL.glVertex2f(lbx, lby + mask_height)
                # TOP
                GL.glVertex2f(ltx, lty - mask_height)
                GL.glVertex2f(rtx, rty - mask_height)
                GL.glVertex2f(rtx, rty)
                GL.glVertex2f(ltx, lty)
            # LEFT & RIGHT
            elif img_ratio > mask_ratio:
                mask_width = ((rtx - ltx) - ((rty - rby) * mask_ratio)) / 2
                GL.glColor4f(0.0, 0.0, 0.0, opacity)
                # LEFT
                GL.glVertex2f(lbx, lby)
                GL.glVertex2f(lbx + mask_width, lby)
                GL.glVertex2f(ltx + mask_width, lty)
                GL.glVertex2f(ltx, lty)
                # RIGHT
                GL.glVertex2f(rbx - mask_width, rby)
                GL.glVertex2f(rbx, rby)
                GL.glVertex2f(rtx, rty)
                GL.glVertex2f(rtx - mask_width, rty)
        GL.glEnd()

        GL.glDisable(GL.GL_BLEND)

        GL.glEndList()

        GL.glCallList(self.__display)

    # TODO Transforms Indicator
    # def __render_transform_indicators(self, event):
        # if not self.__transform and not self.__dynamic_transform:
        #     return

        # sources = rvc.sourcesAtFrame(rvc.frame())
        # if len(sources) != 1:
        #     return
        # source = sources[0]

        # geometry = rvc.imageGeometry(source)
        # x0, y0 = geometry[0]
        # x1, y1 = geometry[2]

        # domain = event.domain()

        # GL.glMatrixMode(GL.GL_PROJECTION)
        # GL.glLoadIdentity()
        # GL.glOrtho(0, domain[0], 0, domain[1], -1000000, +1000000)
        # GL.glMatrixMode(GL.GL_MODELVIEW)
        # GL.glLoadIdentity()

        # X0 = x0
        # X1 = x1
        # Y0 = y0
        # Y1 = y1

        # GL.glLineWidth(1)
        # GL.glColor3f(0.5, 0.5, 0.5)
        # GL.glEnable(GL.GL_LINE_SMOOTH)
        # GL.glEnable(GL.GL_BLEND)
        # GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # # stipple line indicator
        # GL.glLineStipple(4, 0xAAAA)
        # GL.glEnable(GL.GL_LINE_STIPPLE)
        # GL.glBegin(GL.GL_LINE_LOOP)
        # GL.glVertex2f(X0, Y0)
        # GL.glVertex2f(X1, Y0)
        # GL.glVertex2f(X1, Y1)
        # GL.glVertex2f(X0, Y1)
        # GL.glEnd()
        # GL.glDisable(GL.GL_LINE_STIPPLE)

        # # solid loop line indicator
        # GL.glBegin(GL.GL_LINE_LOOP)
        # GL.glVertex2f(X0, Y0)
        # GL.glVertex2f(X1, Y0)
        # GL.glVertex2f(X1, Y1)
        # GL.glVertex2f(X0, Y1)
        # GL.glEnd()

        # # solid cross line indicator
        # GL.glBegin(GL.GL_LINES)
        # GL.glVertex2f(X0, Y0)
        # GL.glVertex2f(X1, Y1)
        # GL.glEnd()
        # GL.glBegin(GL.GL_LINES)
        # GL.glVertex2f(X1, Y0)
        # GL.glVertex2f(X0, Y1)
        # GL.glEnd()

        # GL.glDisable(GL.GL_BLEND)
        # GL.glDisable(GL.GL_LINE_SMOOTH)

    def pre_render(self, event):
        geometry = self.get_current_clip_geometry()
        if geometry != self.__last_geometry:
            self.__last_geometry = geometry
            if not geometry:
                geometry = None
            self.__session.viewport.set_current_clip_geometry(geometry)
            self.SIG_CURRENT_CLIP_GEOMETRY_CHANGED.emit(geometry)

        frame = rvc.frame() # global frame
        src_frame = rve.sourceFrame(frame) # source frame
        sources = rvc.sourcesAtFrame(frame)

        if len(sources) != 1:
            return

        if self.__frame == frame:
            return

        source = sources[0]
        source_group = rvc.nodeGroup(source)
        source_tf_node = f"{source_group}_transform2D"
        stack_tf_node = f"{source_group}_stack_t_{source_group}"
        h = rvc.sourceMediaInfo(f"{source}").get("uncropHeight")

        clip_id = self.__session_api.get_current_clip()
        playlist_id = self.__session_api.get_playlist_of_clip(clip_id)
        if playlist_id is None: return

        rotation = self.__session_api.get_attr_value_at(
            clip_id, "dynamic_rotation", src_frame)
        translate_x = self.__session_api.get_attr_value_at(
            clip_id, "dynamic_translate_x", src_frame)
        translate_y = self.__session_api.get_attr_value_at(
            clip_id, "dynamic_translate_y", src_frame)
        scale_x = self.__session_api.get_attr_value_at(
            clip_id, "dynamic_scale_x", src_frame)
        scale_y = self.__session_api.get_attr_value_at(
            clip_id, "dynamic_scale_y", src_frame)

        if rotation is not None and rotation != "":
            rvc.setFloatProperty(
                f"{stack_tf_node}.transform.rotate", [float(rotation)])

        if translate_x is not None and translate_x != "":
            translate_x = prop_util.convert_translate_itview_to_rv(translate_x, h)
            t_y = rvc.getFloatProperty(f"{stack_tf_node}.transform.translate")[1]
            rvc.setFloatProperty(
                f"{stack_tf_node}.transform.translate", [float(translate_x), t_y])

        if translate_y is not None and translate_y != "":
            translate_y = prop_util.convert_translate_itview_to_rv(translate_y, h)
            t_x = rvc.getFloatProperty(f"{stack_tf_node}.transform.translate")[0]
            rvc.setFloatProperty(
                f"{stack_tf_node}.transform.translate", [t_x, float(translate_y)])

        if scale_x is not None and scale_x != "":
            s_y = rvc.getFloatProperty(f"{stack_tf_node}.transform.scale")[1]
            rvc.setFloatProperty(
                f"{stack_tf_node}.transform.scale", [float(scale_x), s_y])

        if scale_y is not None and scale_y != "":
            s_x = rvc.getFloatProperty(f"{stack_tf_node}.transform.scale")[0]
            rvc.setFloatProperty(
                f"{stack_tf_node}.transform.scale", [s_x, float(scale_y)])

        self.__frame = frame

    def render(self, event):
        # Masks
        self.__render_mask(event)

        # Transforms
        # self.__render_transform_indicators(event)

        # Draw Line to indicate text position
        domain = event.domain()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, domain[0], 0, domain[1], -1000000, +1000000)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        text_cursor = self.__session.viewport.text_cursor
        if text_cursor.position and text_cursor.size:
            GL.glEnable(GL.GL_BLEND)
            GL.glLineWidth(float(3))
            GL.glColor(1.0, 1.0, 1.0, 1.0)
            GL.glBegin(GL.GL_LINES)
            GL.glVertex(text_cursor.position.x, text_cursor.position.y)
            GL.glVertex(
                text_cursor.position.x,
                text_cursor.position.y + (5 * text_cursor.size))
            GL.glEnd()

        cross_hair_cursor = self.__session.viewport.cross_hair_cursor
        if cross_hair_cursor:
            GL.glColor3f(0.8, 0.8, 0.8)
            GL.glBegin(GL.GL_LINE_STRIP)
            GL.glVertex2f(cross_hair_cursor.x - 5.0, cross_hair_cursor.y)
            GL.glVertex2f(cross_hair_cursor.x + 5.0, cross_hair_cursor.y)
            GL.glEnd()
            GL.glBegin(GL.GL_LINE_STRIP)
            GL.glVertex2f(cross_hair_cursor.x, cross_hair_cursor.y - 5.0)
            GL.glVertex2f(cross_hair_cursor.x, cross_hair_cursor.y + 5.0)
            GL.glEnd()

        # Overlays
        self.__render_html_overlays()

    def __render_html_overlays(self):
        if self.__viewport_widget is None: return
        html_overlays = self.__session.viewport.get_html_overlays()
        if not html_overlays: return

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        for html_overlay in html_overlays:
            if not html_overlay.is_visible: continue
            w, h = html_overlay.width, html_overlay.height
            x = html_overlay.x * self.__viewport_widget.width()
            y = html_overlay.y * self.__viewport_widget.height()
            bg_opacity = html_overlay.bg_opacity
            texture_id = html_overlay.get_custom_attr("gl_texture_id")
            half_w = w/2
            half_h = h/2

            lower_left = (x - half_w, y - half_h)
            lower_right = (x + half_w, y - half_h)
            upper_right = (x + half_w, y + half_h)
            upper_left = (x - half_w, y + half_h)

            # Background
            GL.glBegin(GL.GL_QUADS)
            GL.glColor4f(0.0, 0.0, 0.0, bg_opacity)
            GL.glVertex2f(*lower_left)
            GL.glVertex2f(*lower_right)
            GL.glVertex2f(*upper_right)
            GL.glVertex2f(*upper_left)
            GL.glEnd()

            # Outline
            GL.glLineWidth(1.0)
            GL.glColor4f(0.5, 0.5, 0.5, bg_opacity)
            GL.glBegin(GL.GL_LINE_LOOP)
            GL.glVertex2f(*lower_left)
            GL.glVertex2f(*lower_right)
            GL.glVertex2f(*upper_right)
            GL.glVertex2f(*upper_left)
            GL.glEnd()

            # Draw HTML Overlay Texture
            GL.glColor4f(1.0, 1.0, 1.0, 1.0)
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
            GL.glBegin(GL.GL_QUADS)
            GL.glTexCoord2f(0.0, 0.0)
            GL.glVertex2f(*lower_left)
            GL.glTexCoord2f(1.0, 0.0)
            GL.glVertex2f(*lower_right)
            GL.glTexCoord2f(1.0, 1.0)
            GL.glVertex2f(*upper_right)
            GL.glTexCoord2f(0.0, 1.0)
            GL.glVertex2f(*upper_left)
            GL.glEnd()
            GL.glDisable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

        GL.glDisable(GL.GL_BLEND)

    def is_feedback_visible(self, category:int)-> bool:
        if category == 1:
            return self.__session.viewport.feedback.is_visible
        elif category == 2:
            return self.__session.viewport.feedback.are_strokes_visible
        elif category == 3:
            return self.__session.viewport.feedback.are_texts_visible
        elif category == 4:
            return self.__session.viewport.feedback.are_clip_ccs_visible
        elif category == 5:
            return self.__session.viewport.feedback.are_frame_ccs_visible
        elif category == 6:
            return self.__session.viewport.feedback.are_region_ccs_visible

    def set_feedback_visibility(self, category:int, value:bool)-> None:
        if category == 1:
            self.__session.viewport.feedback.is_visible = value
            self.__annotation_api._update_visibility()
            return True
        if category == 2:
            self.__session.viewport.feedback.are_strokes_visible = value
            self.__annotation_api._redraw_ro_annotations(self.__session_api.get_current_clip())
            return True
        if category == 3:
            self.__session.viewport.feedback.are_texts_visible = value
            self.__annotation_api._redraw_ro_annotations(self.__session_api.get_current_clip())
            return True
        if category == 4:
            self.__session.viewport.feedback.are_clip_ccs_visible = value
            self.__color_api._refresh(self.__session_api.get_current_clip())
            return True
        if category == 5:
            self.__session.viewport.feedback.are_frame_ccs_visible = value
            self.__color_api._refresh(self.__session_api.get_current_clip())
            return True
        if category == 6:
            self.__session.viewport.feedback.are_region_ccs_visible = value
            self.__color_api._refresh(self.__session_api.get_current_clip())
            return True
        return False

    def _set_viewport_widget(self, viewport_widget):
        self.__viewport_widget = viewport_widget
        self.__viewport_widget.installEventFilter(self)
        self.__viewport_widget.setMouseTracking(True)

    def eventFilter(self, object, event):
        if object is self.__viewport_widget:
            get_pos = lambda: (event.pos().x(), event.pos().y())
            if event.type() == QtCore.QEvent.MouseButtonPress and \
            event.buttons() == QtCore.Qt.LeftButton:
                x, y = get_pos()
                self.__last_mouse_pos[0] = x
                self.__last_mouse_pos[1] = y

            if event.type() == QtCore.QEvent.MouseMove:
                x, y = get_pos()
                if event.buttons() == QtCore.Qt.NoButton:
                    self.__html_overlay_hover_check(x, y)
                elif event.buttons() == QtCore.Qt.LeftButton:
                    if self.__active_html_overlay:
                        dx = (x - self.__last_mouse_pos[0])/self.__viewport_widget.width()
                        dy = (y - self.__last_mouse_pos[1])/self.__viewport_widget.height()
                        self.__active_html_overlay.x += dx
                        self.__active_html_overlay.y -= dy
                    self.__last_mouse_pos = [x, y]
                rvc.redraw()
        return False

    def __html_overlay_hover_check(self, mouse_x, mouse_y):
        self.__active_html_overlay = None
        for html_overlay in reversed(
            self.__session.viewport.get_html_overlays()):

            x = html_overlay.x * self.__viewport_widget.width()
            y = self.__viewport_widget.height() - (html_overlay.y * self.__viewport_widget.height())
            half_w = html_overlay.width/2
            half_h = html_overlay.height/2

            left = x - half_w
            right = x + half_w
            bottom = y + half_h
            top = y - half_h

            if left <= mouse_x <= right and top <= mouse_y <= bottom:
                self.__active_html_overlay = html_overlay
                break

        for html_overlay in self.__session.viewport.get_html_overlays():
            if html_overlay is self.__active_html_overlay:
                html_overlay.bg_opacity = 0.6
            else:
                html_overlay.bg_opacity = 0.0

        if self.__active_html_overlay is None:
            runtime.eval(
                "require rv_state_mngr;"
                "rv_state_mngr.disable_frame_change_mouse_events();",[])
        else:
            runtime.eval(
                "require rv_state_mngr;"
                "rv_state_mngr.disable_frame_change_mouse_events();",[])
