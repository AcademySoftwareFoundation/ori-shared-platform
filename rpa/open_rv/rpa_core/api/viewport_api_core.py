import asyncio
import math
import os
import re
import threading
from dataclasses import dataclass
import imageio.v3 as iio
import numpy as np
from OpenGL import GL
try:
    from PySide2 import QtGui, QtCore, QtWebEngineWidgets
except:
    from PySide6 import QtGui, QtCore, QtWebEngineWidgets
from rv import commands as rvc
from rv import extra_commands as rve
from rv import runtime
from rpa.open_rv.rpa_core.api import prop_util
from rpa.session_state.utils import Point, itview_to_screen
from playwright.async_api import async_playwright


def render_html_to_image(width, height, html):
    doc = QtGui.QTextDocument()
    doc.setHtml(html)
    doc.setTextWidth(width)
    doc.setDocumentMargin(0)

    image = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)
    image.fill(QtCore.Qt.transparent)

    painter = QtGui.QPainter(image)
    doc.drawContents(painter)
    painter.end()

    return image

def qimage_to_gl_texture(image):
    ptr = image.bits()
    ptr = ptr[: image.sizeInBytes()]
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


def hex_to_glColor3f(hex_color):
    """Convert hex color string to RGB float for glColor3f

    Args:
        hex_color (str): hex color string in the form of #FFFFFF

    Returns:
        tuple: (r, g, b) as floats in [0.0, 1.0]
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b)

@dataclass(frozen=True)
class FlipMode:
    NONE: str = "None"
    BOTH: str = "Both"
    HORIZ: str = "Horizontally"
    VERT: str = "Vertically"


class PlaywrightRenderer(QtCore.QObject):
    SIG_RENDER_FINISHED = QtCore.Signal(object) # image

    def __init__(self, async_loop, callback):
        super().__init__()
        self.__async_loop = async_loop
        self.__last_future = self.__async_loop.create_future()
        self.__callback = callback
        self.__empty_image = None
        self.__playwright = None
        self.__browser = None
        self.__page = None
        self.SIG_RENDER_FINISHED.connect(self.render_finished)

    def __del__(self):
        asyncio.run_coroutine_threadsafe(self.cleanup(), self.__async_loop)

    async def cleanup(self):
        if self.__page:
            await self.__page.close()
        if self.__browser:
            await self.__browser.close()
        if self.__playwright:
            await self.__playwright.stop()

    def render(self, html_overlay):
        self.__last_future.cancel()
        self.render_empty(html_overlay)
        if html_overlay.html:
            self.__last_future = asyncio.run_coroutine_threadsafe(self.render_async(html_overlay), self.__async_loop)

    def render_empty(self, html_overlay):
        try:
            overlay_width, overlay_height = html_overlay.get_custom_attr("content_size")
        except:
            overlay_width, overlay_height = 100, 100

        if self.__empty_image is None \
        or overlay_width != self.__empty_image.width() \
        or overlay_height != self.__empty_image.height():
            self.__empty_image = QtGui.QImage(overlay_width, overlay_height, QtGui.QImage.Format_ARGB32)
            self.__empty_image.fill(QtCore.Qt.transparent)
        self.__callback(self.__empty_image)

    async def render_async(self, html_overlay):
        if self.__playwright is None:
            self.__playwright = await async_playwright().start()
        if self.__browser is None:
            self.__browser = await self.__playwright.chromium.launch(headless=True)
        if self.__page is None:
            self.__page = await self.__browser.new_page()

        await self.__page.set_viewport_size({
            "width": html_overlay.width,
            "height": html_overlay.height})
        await self.__page.set_content(html_overlay.html, wait_until="networkidle")
        element = await self.__page.query_selector("#content")  # or any locator
        if not element:
            element = self.__page
        png_bytes = await element.screenshot(type="png", omit_background=True)
        image = QtGui.QImage()
        image.loadFromData(QtCore.QByteArray(png_bytes), "PNG")
        self.SIG_RENDER_FINISHED.emit(image)

    def render_finished(self, image):
        self.__callback(image)


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

        self.__renderers = {}

        self.__async_loop = asyncio.new_event_loop()
        def background_loop():
            asyncio.set_event_loop(self.__async_loop)
            self.__async_loop.run_forever()
        self.__async_thread = threading.Thread(target=background_loop, daemon=True)
        self.__async_thread.start()

    def create_html_overlay(self, html_overlay):
        id = self.__session.viewport.create_html_overlay(html_overlay)
        html_overlay = self.__session.viewport.get_html_overlay(id)
        self.__set_html_overlay_texture(id, html_overlay)
        return id

    def set_html_overlay(self, id:str, html_overlay):
        is_success = \
            self.__session.viewport.set_html_overlay(id, html_overlay)
        if is_success:
            html_overlay = self.__session.viewport.get_html_overlay(id)
            self.__set_html_overlay_texture(id, html_overlay)
        return is_success

    def __set_html_overlay_texture(self, id, html_overlay):
        def update_texture(image):
            if not image: return
            old_texture_id = html_overlay.get_custom_attr("gl_texture_id")
            if old_texture_id is not None:
                GL.glDeleteTextures([old_texture_id])
            new_texture_id = qimage_to_gl_texture(image)
            html_overlay.set_custom_attr("gl_texture_id", new_texture_id)
            html_overlay.set_custom_attr("content_size", [image.width(), image.height()])
            rvc.redraw()
        if html_overlay.use_web_engine:
            renderer = self.__renderers.get(id)
            if renderer is None:
                renderer = PlaywrightRenderer(self.__async_loop, update_texture)
                self.__renderers[id] = renderer
            renderer.render(html_overlay)
        else:
            image = render_html_to_image(
                html_overlay.width, html_overlay.height, html_overlay.html)
            update_texture(image)

    def get_html_overlay(self, id:str):
        return self.__session.viewport.get_html_overlay_data(id)

    def get_html_overlay_ids(self):
        return self.__session.viewport.get_html_overlay_ids()

    def delete_html_overlays(self, ids):
        is_success = self.__session.viewport.delete_html_overlays(ids)
        for id in ids:
            self.__renderers.pop(id, None)
        rvc.redraw()
        return is_success

    def create_opengl_overlay(self, recipe):
        id = self.__session.viewport.create_opengl_overlay(recipe)
        rvc.redraw()
        return id

    def set_opengl_overlay(self, id, recipe):
        is_success = self.__session.viewport.set_opengl_overlay(id, recipe)
        if is_success:
            rvc.redraw()
        return is_success

    def get_opengl_overlay_ids(self):
        return self.__session.viewport.get_opengl_overlay_ids()

    def delete_opengl_overlays(self, ids):
        is_success = self.__session.viewport.delete_opengl_overlays(ids)
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

    def is_flipped_x(self):
        return self.__session.viewport.transforms.flip_x

    def flip_x(self, state):
        scale = \
            rvc.getFloatProperty("#RVDispTransform2D.transform.scale")
        h_scale = scale[0]
        v_scale = scale[1]

        translation = \
            rvc.getFloatProperty("#RVDispTransform2D.transform.translate")
        dx = translation[0]
        dy = translation[1]

        if state != (h_scale < 0):
            self.set_translation(0.0, 0.0)
            self.set_scale(h_scale * -1, v_scale)
            self.set_translation(dx * -1, dy)

        self.__session.viewport.transforms.flip_x = state

        if self.__session.viewport.transforms.flip_x and self.__session.viewport.transforms.flip_y:
            mode = FlipMode.BOTH
        elif self.__session.viewport.transforms.flip_x:
            mode = FlipMode.HORIZ
        elif self.__session.viewport.transforms.flip_y:
            mode = FlipMode.VERT
        else:
            mode = FlipMode.NONE

        self.display_msg(f"Flipped: {mode}")
        return True

    def is_flipped_y(self):
        return self.__session.viewport.transforms.flip_y

    def flip_y(self, state):
        scale = \
            rvc.getFloatProperty("#RVDispTransform2D.transform.scale")
        h_scale = scale[0]
        v_scale = scale[1]

        translation = \
            rvc.getFloatProperty("#RVDispTransform2D.transform.translate")
        dx = translation[0]
        dy = translation[1]

        if state != (v_scale < 0):
            self.set_translation(0.0, 0.0)
            self.set_scale(h_scale, v_scale * -1)
            self.set_translation(dx, dy * -1)

        self.__session.viewport.transforms.flip_y = state

        if self.__session.viewport.transforms.flip_x and self.__session.viewport.transforms.flip_y:
            mode = FlipMode.BOTH
        elif self.__session.viewport.transforms.flip_x:
            mode = FlipMode.HORIZ
        elif self.__session.viewport.transforms.flip_y:
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

    def get_viewport_dimensions(self):
        return rvc.viewSize()

    def get_translation(self):
        return prop_util.get_property("#RVDispTransform2D.transform.translate")[0]

    def set_rotation(self, angle):
        self.__session.viewport.rotation = angle
        groups = rvc.nodesOfType("RVViewPipelineGroup")
        if not len(groups): return False
        for group in groups:
            nodes = rvc.getStringProperty(group + ".pipeline.nodes")
            if not ("RVTransform2D" in nodes):
                nodes += ["RVTransform2D"]
                rvc.setStringProperty(group + ".pipeline.nodes", nodes, True)
            nodes = rvc.closestNodesOfType("RVTransform2D", group)
            for node in nodes:
                rvc.setFloatProperty(node + ".transform.rotate", [float(angle)], True)
        return True

    def get_rotation(self):
        return self.__session.viewport.rotation

    def get_mask(self):
        return self.__session.viewport.mask

    def set_mask(self, mask):
        self.__session.viewport.mask = mask
        self.__unload_mask()

        # No Mask
        if mask is None:
            rvc.redraw()
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
            rvc.redraw()
            return False

        rvc.redraw()
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

    def __get_image_rect(self, width, height, geometry, translate_x, translate_y, scale_x, scale_y, rotation=None):
        """Return geometry rectangle of the image without image transforms applied

        Args:
            width (float): image width
            height (float): image height
            geometry (list): current image geometry
            translate_x (float): translation in x axis
            translate_y (float): translation in y axis
            scale_x (float): scale in x axis
            scale_y (float): scale in y axis
            rotation (float, optional): rotation of an image. Defaults to None.

        Returns:
            _type_: _description_
        """
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

        lb, rb, rt, lt = self.__get_image_rect(
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
        GL.glColor4f(1.0, 1.0, 1.0, 1.0)
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

        lb, rb, rt, lt = self.__get_image_rect(
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

    def __render_opengl_overlays(self, event):
        frame = rvc.frame()
        sources = rvc.sourcesAtFrame(frame)
        if len(sources) != 1:
            return
        domain = event.domain()
        overlays = self.__session.viewport.get_opengl_overlays()
        for recipe in overlays:
            if not recipe.get("is_visible", False):
                continue
            vertices = recipe.get("vertices", [])
            vertices = list(map(lambda v: np.array([*self.__convert_to_image_space(v), 1]), vertices))
            if recipe.get("apply_image_transforms", False):
                vertices = self.__apply_image_transforms(vertices)
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            GL.glOrtho(0, domain[0], 0, domain[1], -1000000, +1000000)
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()

            GL.glLineWidth(recipe.get("width", 1.0))
            GL.glEnable(GL.GL_BLEND)
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
            GL.glColor4f(*hex_to_glColor3f(recipe.get("color", "#FFFFFF")),
                         recipe.get("opacity", 1.0))
            if recipe.get("dashed", False):
                GL.glLineStipple(4, 0xAAAA)
                GL.glEnable(GL.GL_LINE_STIPPLE)
            GL.glBegin(GL.GL_LINE_LOOP)
            for corner in vertices:
                GL.glVertex(corner)
            GL.glEnd()
            if recipe.get("dashed", False):
                GL.glDisable(GL.GL_LINE_STIPPLE)

    def __convert_to_image_space(self, vert):
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

        translate_x = self.__session_api.get_attr_value(clip_id, "pan_x")
        translate_x += self.__session_api.get_attr_value_at(clip_id, "dynamic_translate_x", src_frame)
        translate_y = self.__session_api.get_attr_value(clip_id, "pan_y")
        translate_y += self.__session_api.get_attr_value_at(clip_id, "dynamic_translate_y", src_frame)
        scale_x = self.__session_api.get_attr_value(clip_id, "scale_x")
        scale_x *= self.__session_api.get_attr_value_at(clip_id, "dynamic_scale_x", src_frame)
        scale_y = self.__session_api.get_attr_value(clip_id, "scale_y")
        scale_y *= self.__session_api.get_attr_value_at(clip_id, "dynamic_scale_y", src_frame)
        rotation = self.get_rotation()
        lb, rb, _, lt = self.__get_image_rect(
            img_width, img_height, geometry, -translate_x, -translate_y, 1.0/scale_x, 1.0/scale_y, rotation=rotation)

        u, v = rb-lb, lt-lb # vectors that define direction of rectangle
        return lb + vert[0]*u + vert[1]*v

    def __apply_image_transforms(self, vertices):
        clip_id = self.__session.viewport.current_clip
        frame = rvc.frame() # global frame
        src_frame = rve.sourceFrame(frame) # source frame

        translate_x = self.__session_api.get_attr_value(clip_id, "pan_x")
        translate_x += self.__session_api.get_attr_value_at(clip_id, "dynamic_translate_x", src_frame)
        translate_y = self.__session_api.get_attr_value(clip_id, "pan_y")
        translate_y += self.__session_api.get_attr_value_at(clip_id, "dynamic_translate_y", src_frame)
        scale_x = self.__session_api.get_attr_value(clip_id, "scale_x")
        scale_x *= self.__session_api.get_attr_value_at(clip_id, "dynamic_scale_x", src_frame)
        scale_y = self.__session_api.get_attr_value(clip_id, "scale_y")
        scale_y *= self.__session_api.get_attr_value_at(clip_id, "dynamic_scale_y", src_frame)
        rotation = self.__session_api.get_attr_value(clip_id, "rotation")
        rotation += self.__session_api.get_attr_value_at(clip_id, "dynamic_rotation", src_frame)
        theta = -math.radians(rotation)
        pixel_size = self.__get_pixel_size(1.0/scale_x, 1.0/scale_y)
        centroid = np.array(vertices).mean(axis=0)

        S = np.array([
            [scale_x, 0, 0],
            [0, scale_y, 0],
            [0, 0, 1]
        ])

        R = np.array([
            [math.cos(theta), -math.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]
        ])

        T1 = np.array([
            [1, 0, -centroid[0]],
            [0, 1, -centroid[1]],
            [0, 0, 1]
        ])

        T2 = np.array([
            [1, 0, centroid[0]],
            [0, 1, centroid[1]],
            [0, 0, 1]
        ])

        Tu = np.array([
            [1, 0, translate_x*pixel_size[0]],
            [0, 1, translate_y*pixel_size[1]],
            [0, 0, 1]
        ])

        M = Tu @ T2 @ R @ S @ T1
        transformed_vertices = []
        for v in vertices:
            transformed_vertices.append(M @ v)
        return transformed_vertices

    def __get_pixel_size(self, scale_x, scale_y):
        frame = rvc.frame() # global frame

        sources = rvc.sourcesAtFrame(frame)
        if len(sources) != 1:
            return
        source = sources[0]
        geometry = rvc.imageGeometry(source)

        g = [np.array(p) for p in geometry]

        size = np.array([
            scale_x * np.linalg.norm(g[1] - g[0]),
            scale_y * np.linalg.norm(g[3] - g[0])])
        width, height = self.__get_current_dimensions()
        pixel_size = size / np.array([width, height])
        return pixel_size

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
        secondary_transform = f"{source_group}_secondary_transform"
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
                f"{secondary_transform}.transform.rotate", [float(rotation)])

        if translate_x is not None and translate_x != "":
            translate_x = prop_util.convert_translate_itview_to_rv(translate_x, h)
            t_y = rvc.getFloatProperty(f"{secondary_transform}.transform.translate")[1]
            rvc.setFloatProperty(
                f"{secondary_transform}.transform.translate", [float(translate_x), t_y])

        if translate_y is not None and translate_y != "":
            translate_y = prop_util.convert_translate_itview_to_rv(translate_y, h)
            t_x = rvc.getFloatProperty(f"{secondary_transform}.transform.translate")[0]
            rvc.setFloatProperty(
                f"{secondary_transform}.transform.translate", [t_x, float(translate_y)])

        if scale_x is not None and scale_x != "":
            s_y = rvc.getFloatProperty(f"{secondary_transform}.transform.scale")[1]
            rvc.setFloatProperty(
                f"{secondary_transform}.transform.scale", [float(scale_x), s_y])

        if scale_y is not None and scale_y != "":
            s_x = rvc.getFloatProperty(f"{secondary_transform}.transform.scale")[0]
            rvc.setFloatProperty(
                f"{secondary_transform}.transform.scale", [s_x, float(scale_y)])

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
        self.__render_html_overlays(event)
        self.__render_opengl_overlays(event)

    def __render_html_overlays(self, event):
        if self.__viewport_widget is None: return
        html_overlays = self.__session.viewport.get_html_overlays()
        if not html_overlays: return

        frame = rvc.frame() # global frame
        src_frame = rve.sourceFrame(frame) # source frame
        clip_id = self.__session_api.get_current_clip()
        if clip_id is None:
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

        lb, rb, rt, lt = self.__get_image_rect(
            img_width, img_height, geometry, -translate_x, -translate_y, 1.0/scale_x, 1.0/scale_y)

        domain = event.domain()

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, domain[0], 0, domain[1], -1000000, +1000000)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        for html_overlay in html_overlays:
            if not html_overlay.is_visible: continue
            bg_opacity = html_overlay.bg_opacity
            texture_id = html_overlay.get_custom_attr("gl_texture_id")
            if not texture_id: continue
            content_size = html_overlay.get_custom_attr("content_size")
            if not content_size: continue
            overlay_width, overlay_height = content_size

            if html_overlay.placement == "frame_inside_overlay":
                ratio = overlay_width / overlay_height
                size = rt - lb
                w = max(size[0], ratio * size[1])
                h = w / ratio
                center = 0.5 * (lb + rt)
                l, r = center[0] - w/2, center[0] + w/2   # left & right
                b, t = center[1] - h/2, center[1] + h/2   # bottom & top
            else:
                w, h = overlay_width, overlay_height
                x = html_overlay.x * self.__viewport_widget.width()
                y = html_overlay.y * self.__viewport_widget.height()
                l, r = x - w/2, x + w/2   # left & right
                b, t = y - h/2, y + h/2   # bottom & top

            # Background
            GL.glBegin(GL.GL_QUADS)
            GL.glColor4f(0.0, 0.0, 0.0, bg_opacity)
            GL.glVertex2f(l, b)
            GL.glVertex2f(r, b)
            GL.glVertex2f(r, t)
            GL.glVertex2f(l, t)
            GL.glEnd()

            # Outline
            GL.glLineWidth(1.0)
            GL.glColor4f(0.5, 0.5, 0.5, bg_opacity)
            GL.glBegin(GL.GL_LINE_LOOP)
            GL.glVertex2f(l, b)
            GL.glVertex2f(r, b)
            GL.glVertex2f(r, t)
            GL.glVertex2f(l, t)
            GL.glEnd()

            # Draw HTML Overlay Texture
            if texture_id is not None:
                GL.glColor4f(1.0, 1.0, 1.0, 1.0)
                GL.glEnable(GL.GL_TEXTURE_2D)
                GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
                GL.glBegin(GL.GL_QUADS)
                GL.glTexCoord2f(0.0, 1.0)
                GL.glVertex2f(l, b)
                GL.glTexCoord2f(1.0, 1.0)
                GL.glVertex2f(r, b)
                GL.glTexCoord2f(1.0, 0.0)
                GL.glVertex2f(r, t)
                GL.glTexCoord2f(0.0, 0.0)
                GL.glVertex2f(l, t)
                GL.glEnd()
                GL.glDisable(GL.GL_TEXTURE_2D)
                GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

            # Draw Border
            if html_overlay.border_width > 0.0:
                GL.glLineWidth(html_overlay.border_width)
                GL.glColor4f(*html_overlay.border_color)
                if html_overlay.border_dashed:
                    GL.glLineStipple(4, 0xAAAA)
                    GL.glEnable(GL.GL_LINE_STIPPLE)
                GL.glBegin(GL.GL_LINE_LOOP)
                GL.glVertex2f(l, b)
                GL.glVertex2f(r, b)
                GL.glVertex2f(r, t)
                GL.glVertex2f(l, t)
                GL.glEnd()
                if html_overlay.border_dashed:
                    GL.glDisable(GL.GL_LINE_STIPPLE)

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

            if html_overlay.placement is not None:
                continue

            try:
                overlay_width, overlay_height = html_overlay.get_custom_attr("content_size")
            except:
                overlay_width, overlay_height = 100, 100

            x = html_overlay.x * self.__viewport_widget.width()
            y = self.__viewport_widget.height() - (html_overlay.y * self.__viewport_widget.height())
            half_w = overlay_width/2
            half_h = overlay_height/2

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

    def toggle_presentation_mode(self):
        is_presenting = rvc.presentationMode()
        rvc.setPresentationMode(not is_presenting)
