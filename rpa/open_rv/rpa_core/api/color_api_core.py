from OpenGL.GL.ARB import framebuffer_object
from OpenGL.GL import shaders as glShaders
from OpenGL import GL
from rv import commands as rvc
from rv import extra_commands as rve
try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore
from rpa.open_rv.rpa_core.api.utils import itview_to_rv
from rpa.session_state.color_corrections import ColorTimer, Grade
import struct


BLUR_SHADER = """
#version 130

uniform sampler2D mask;
uniform float falloff;
uniform bool horiz;

void main()
{
    vec2 size = textureSize(mask, 0);
    float diameter = falloff * size.x; // in pixels
    int radius = min(max(int(0.5 * diameter), 2), 256);
    vec2 direction = horiz
        ? vec2(diameter / (2.0 * radius * size.x), 0)
        : vec2(0, diameter / (2.0 * radius * size.y));
    float sum = 0;
    for (int i = -radius; i <= +radius; ++i)
    {
        float c = smoothstep(0, 1, 1 - abs(i / float(radius)));
        sum += c * texture(mask, gl_TexCoord[0].st + i * direction).x;
    }
    gl_FragColor.x = sum / radius;
}
"""

def get_property(prop):
    """
    Helper function for retrieving RV's property. It automatically detects the type and dimension
    of the property values.

    Args:
        prop (str): Name of the property.

    Returns:
        Value of the requested property.
    """
    if not rvc.propertyExists(prop):
        return []
    info = rvc.propertyInfo(prop)
    prop_type = info["type"]
    dimension = info["dimensions"][0]
    def _():
        if prop_type == rvc.IntType:
            return rvc.getIntProperty(prop)
        if prop_type == rvc.FloatType:
            return rvc.getFloatProperty(prop)
        if prop_type == rvc.StringType:
            return rvc.getStringProperty(prop)
        raise TypeError("Unsupported property type")
    values = _()
    if dimension <= 1:
        return values
    return [values[i * dimension:(i + 1) * dimension]
        for i in range((len(values) + dimension - 1) // dimension)]

def get_first_value(prop):
    """
    Helper function for retrieving the first value of the RV's property.

    Args:
        prop (str): Name of the property.

    Returns:
        The first alue of the requested property.
    """
    values = get_property(prop)
    if not values:
        return None
    return values[0]

def set_property(prop, values):
    """
    Helper function for setting RV's property. It automatically detects the type and dimension
    of the property values.

    Args:
        prop (str): Name of the property.
        values (list): List of values to be set.
    """
    def _(prop_type, width, setter):
        if not rvc.propertyExists(prop):
            rvc.newProperty(prop, prop_type, width)
        return setter(prop, values, True)
    value = values[0]
    width = 1
    if isinstance(value, list):
        width = len(value)
        values = sum(values, [])
        value = value[0]
    if isinstance(value, int):
        return _(rvc.IntType, width, rvc.setIntProperty)
    if isinstance(value, float):
        return _(rvc.FloatType, width, rvc.setFloatProperty)
    if isinstance(value, str):
        return _(rvc.StringType, width, rvc.setStringProperty)
    raise TypeError("Unsupported property type")

def append_property(prop, values):
    """
    Helper function for appending to RV's property. It automatically detects the type and dimension
    of the property values.

    Args:
        prop (str): Name of the property.
        values (list): List of values to be appended.
    """
    old_values = get_property(prop)
    set_property(prop, old_values + values)

def delete_property(prop):
    """
    Helper function for deleteing RV's property. It does not raise exception in case the property
    does not exist.

    Args:
        prop (str): Name of the property.
    """
    try:
        rvc.deleteProperty(prop)
    except:
        pass

def delete_all_properties(node, prefix):
    """
    Helper function for deleteing RV's properties. It deletes all properties which start with
    the specified prefix from the specified node.

    Args:
        node (str): Name of the RV's node.
        prefix (str): Prefix of the node's properties.
    """
    for prop in rvc.properties(node):
        if prop.startswith(prefix):
            delete_property(prop)


class ColorApiCore(QtCore.QObject):
    """
    A class that provides an interface for color correction operations.
    It also implements the rendering of the color correction on RV side.
    """
    SIG_CCS_MODIFIED = QtCore.Signal(str, object) # clip_id, frame
    SIG_CC_MODIFIED = QtCore.Signal(str, str) # clip_id, cc_id
    SIG_CC_NODE_MODIFIED = QtCore.Signal(str, str, int) # clip_id, cc_id, node_index


    def __init__(self, session):
        """
        Initializes the ColorApi instance.
        """
        super().__init__()
        self.__session = session

        self.__ssbo = None
        self.__textures = []

        blur_shader = glShaders.compileShader(
            BLUR_SHADER, GL.GL_FRAGMENT_SHADER)
        self.__blur_shader_program = glShaders.compileProgram(
            blur_shader)

        self.__uniform_falloff = GL.glGetUniformLocation(
            self.__blur_shader_program, "falloff")
        self.__uniform_horiz = GL.glGetUniformLocation(
            self.__blur_shader_program, "horiz")

    def set_ocio_colorspace(self, clip_id, colorspace):
        clip = self.__session.get_clip(clip_id)
        source_node = clip.get_custom_attr("rv_source_group")
        if not source_node: return False
        color_node = rvc.closestNodesOfType("OCIOFile", source_node)
        if not color_node: return False
        rvc.setStringProperty(color_node[0] + ".ocio.inColorSpace", [colorspace])
        return True

    def get_ocio_colorspace(self, clip_id):
        colorspace = "None"
        clip = self.__session.get_clip(clip_id)
        source_node = clip.get_custom_attr("rv_source_group")
        if not source_node: return
        color_node = rvc.closestNodesOfType("OCIOFile", source_node)
        if not color_node: return
        try:
            colorspace = rvc.getStringProperty(color_node[0] + ".ocio.inColorSpace")[0]
        except Exception as e:
            print("Cannot get colorspace", e)
        return colorspace

    def set_ocio_display(self, display):
        ocio_display_nodes = rvc.nodesOfType("OCIODisplay")
        if not ocio_display_nodes: False
        for node in ocio_display_nodes:
            rvc.setStringProperty(node + ".ocio_display.display", [display])
        return True

    def get_ocio_display(self):
        display = "None"
        try:
            for node in rvc.nodesOfType("OCIODisplay"):
                display = rvc.getStringProperty(node + ".ocio_display.display")[0]
        except Exception as e:
            print("Cannot get colorspace", e)
        return display

    def set_ocio_view(self, view):
        ocio_display_nodes = rvc.nodesOfType("OCIODisplay")
        if not ocio_display_nodes: False
        for node in ocio_display_nodes:
            rvc.setStringProperty(node + ".ocio_display.view", [view])
        return True

    def get_ocio_view(self):
        view = "None"
        try:
            for node in rvc.nodesOfType("OCIODisplay"):
                view = rvc.getStringProperty(node + ".ocio_display.view")[0]
        except Exception as e:
            view = "None"
            print("Cannot get view", e)
        return view

    def set_channel(self, channel:int):
        self.__session.viewport.color_channel = channel
        self.__set_color_channel_mode(channel)
        rvc.redraw()
        return True

    def get_channel(self):
        return self.__session.viewport.color_channel

    def set_fstop(self, value:float):
        self.__session.viewport.fstop = value
        groups = rvc.nodesOfType("RVViewPipelineGroup")
        if not len(groups): return False
        for group in groups:
            nodes = rvc.getStringProperty(group + ".pipeline.nodes")
            if not ("RVColor" in nodes):
                nodes += ["RVColor"]
                rvc.setStringProperty(group + ".pipeline.nodes", nodes, True)
            nodes = rvc.closestNodesOfType("RVColor", group)
            for node in nodes:
                rvc.setFloatProperty(node + ".color.exposure", [value, value, value], True)
        return True

    def get_fstop(self):
        return self.__session.viewport.fstop

    def set_gamma(self, value:float):
        self.__session.viewport.gamma = value
        groups = rvc.nodesOfType("RVViewPipelineGroup")
        if not len(groups): return False
        for group in groups:
            nodes = rvc.getStringProperty(group + ".pipeline.nodes")
            if not ("RVColor" in nodes):
                nodes += ["RVColor"]
                rvc.setStringProperty(group + ".pipeline.nodes", nodes, True)
            nodes = rvc.closestNodesOfType("RVColor", group)
            for node in nodes:
                rvc.setFloatProperty(node + ".color.gamma", [value, value, value], True)
        return True

    def get_gamma(self):
        return self.__session.viewport.gamma

    def get_cc_ids(self, clip_id, frame=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.color_corrections.get_cc_ids(frame=frame)

    def move_cc(self, clip_id, from_index, to_index, frame=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.move_cc(from_index, to_index, frame=frame)
        self.SIG_CCS_MODIFIED.emit(clip_id, frame)
        self._refresh(clip_id)
        return True

    def append_ccs(self, clip_id, names, frame=None, cc_ids=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        ids = clip.color_corrections.append_ccs(names, frame=frame, cc_ids=cc_ids)
        self.SIG_CCS_MODIFIED.emit(clip_id, frame)
        return ids

    def delete_ccs(self, clip_id, cc_ids, frame=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.delete_ccs(cc_ids, frame)
        self.SIG_CCS_MODIFIED.emit(clip_id, frame)
        self._refresh(clip_id)
        return True

    def get_frame_of_cc(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return None
        return clip.color_corrections.get_frame_of_cc(cc_id)

    def get_nodes(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.color_corrections.get_nodes(cc_id)

    def get_node_count(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_node_count(cc_id)

    def get_node(self, clip_id, cc_id, node_index):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_node(cc_id, node_index)

    def append_nodes(self, clip_id, cc_id, nodes):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.append_nodes(cc_id, nodes)
        self.SIG_CC_MODIFIED.emit(clip_id, cc_id)
        self._refresh(clip_id)
        return True

    def clear_nodes(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.clear_nodes(cc_id)
        self.SIG_CC_MODIFIED.emit(clip_id, cc_id)
        self._refresh(clip_id)
        return True

    def delete_node(self, clip_id, cc_id, node_index):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.delete_node(cc_id, node_index)
        self.SIG_CC_MODIFIED.emit(clip_id, cc_id)
        self._refresh(clip_id)
        return True

    def set_node_properties(
        self, clip_id, cc_id, node_index, properties):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.set_node_properties(cc_id, node_index, properties)
        self.SIG_CC_NODE_MODIFIED.emit(clip_id, cc_id, node_index)
        self._refresh(clip_id)
        return True

    def get_node_properties(self, clip_id, cc_id, node_index, property_names):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_node_properties(cc_id, node_index, property_names)

    def is_modified(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        return clip.color_corrections.is_modified(cc_id)

    def set_name(self, clip_id, cc_id, name):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.set_name(cc_id, name)
        self.SIG_CC_MODIFIED.emit(clip_id, cc_id)
        return True

    def get_name(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_name(cc_id)

    def create_region(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.create_region(cc_id)
        self.SIG_CC_MODIFIED.emit(clip_id, cc_id)
        self._refresh(clip_id)
        return True

    def has_region(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        return clip.color_corrections.has_region(cc_id)

    def append_shape_to_region(self, clip_id, cc_id, points):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.append_shape_to_region(cc_id, points)
        self._refresh(clip_id)
        return True

    def delete_region(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.delete_region(cc_id)
        self.SIG_CC_MODIFIED.emit(clip_id, cc_id)
        self._refresh(clip_id)
        return True

    def set_region_falloff(self, clip_id, cc_id, falloff):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.set_region_falloff(cc_id, falloff)
        self.SIG_CC_MODIFIED.emit(clip_id, cc_id)
        self._refresh(clip_id)
        return True

    def get_region_falloff(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_region_falloff(cc_id)

    def mute(self, clip_id, cc_id, value):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.set_mute(cc_id, value)
        self.SIG_CC_MODIFIED.emit(clip_id, cc_id)
        self._refresh(clip_id)
        return True

    def is_mute(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        return clip.color_corrections.is_mute(cc_id)

    def mute_all(self, clip_id, value):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.mute_all(value)
        self.SIG_CCS_MODIFIED.emit(clip_id, None)
        self._refresh(clip_id)
        return True

    def is_mute_all(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        return clip.color_corrections.is_mute_all()

    def set_read_only(self, clip_id, cc_id, value):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        clip.color_corrections.set_read_only(cc_id, value)
        self.SIG_CC_MODIFIED.emit(clip_id, cc_id)
        return True

    def is_read_only(self, clip_id, cc_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return False
        return clip.color_corrections.is_read_only(cc_id)

    def get_rw_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.color_corrections.get_rw_frames()

    def get_ro_frames(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        if not clip: return []
        return clip.color_corrections.get_ro_frames()

    def set_ro_ccs(self, ro_ccs):
        for clip_id, ccs in ro_ccs.items():
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            clip.color_corrections.set_ro_ccs(ccs)
        current_clip = self.__session.viewport.current_clip
        for clip in ro_ccs.keys():
            self._refresh(clip)
            if current_clip == clip:
                self.SIG_CCS_MODIFIED.emit(current_clip, None)
        return True

    def set_rw_ccs(self, rw_ccs):
        for clip_id, ccs in rw_ccs.items():
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            clip.color_corrections.set_rw_ccs(ccs)
        current_clip = self.__session.viewport.current_clip
        for clip in rw_ccs.keys():
            self._refresh(clip)
            if current_clip == clip:                
                self.SIG_CCS_MODIFIED.emit(current_clip, None)
        return True

    def get_ro_ccs(self, clip_id:str, frame=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_ro_ccs(frame)

    def get_rw_ccs(self, clip_id:str, frame=None):
        clip = self.__session.get_clip(clip_id)
        if not clip: return
        return clip.color_corrections.get_rw_ccs(frame)

    def delete_ro_ccs(self, clips):
        for clip_id in clips:
            clip = self.__session.get_clip(clip_id)
            if not clip: continue
            clip.color_corrections.delete_ro_ccs()
        current_clip = self.__session.viewport.current_clip
        for clip in clips:
            self._refresh(clip)
            if current_clip == clip:
                self.SIG_CCS_MODIFIED.emit(current_clip, None)
        return True

    def __get_current_source_node_f(self, frame):
        sources = rvc.sourcesAtFrame(frame)
        if len(sources) != 1:
            return None
        source = sources[0]
        return source

    def __create_fbo_and_textures(self, width, height):
        fbo = GL.glGenFramebuffers(1)
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, fbo)

        stencil_texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, stencil_texture)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_DEPTH24_STENCIL8,
            width,
            height,
            0,
            GL.GL_DEPTH_STENCIL,
            GL.GL_UNSIGNED_INT_24_8,
            None)
        GL.glFramebufferTexture2D(
            GL.GL_FRAMEBUFFER,
            GL.GL_STENCIL_ATTACHMENT,
            GL.GL_TEXTURE_2D,
            stencil_texture,
            0)

        blur_texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, blur_texture)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            width,
            height,
            0,
            GL.GL_RGBA,
            GL.GL_FLOAT,
            None)

        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, width, 0, height, -1000000, +1000000)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glColor(1.0, 1.0, 1.0)

        return fbo, stencil_texture, blur_texture

    def __render_polygon(self, width, height, points):
        GL.glBegin(GL.GL_POLYGON)
        for point in points:
            x = height * point[0] + 0.5 * width
            y = height * point[1] + 0.5 * height
            GL.glVertex2f(x, y)
        GL.glEnd()

    def __render_polygon_with_stencil_test(self, width, height, points):
        GL.glClear(GL.GL_STENCIL_BUFFER_BIT)
        GL.glEnable(GL.GL_STENCIL_TEST)

        # set stencil buffer to invert value on draw, 0 to 1 and 1 to 0
        GL.glStencilFunc(GL.GL_ALWAYS, 0, 1)
        GL.glStencilOp(GL.GL_INVERT, GL.GL_INVERT, GL.GL_INVERT)

        # disable writing to color buffer
        GL.glColorMask(GL.GL_FALSE, GL.GL_FALSE, GL.GL_FALSE, GL.GL_FALSE)

        # draw polygon into stencil buffer
        self.__render_polygon(width, height, points)

        # set stencil buffer to only keep pixels when value in buffer is 1
        GL.glStencilFunc(GL.GL_EQUAL, 1, 1)
        GL.glStencilOp(GL.GL_KEEP, GL.GL_KEEP, GL.GL_KEEP)

        # enable color again
        GL.glColorMask(GL.GL_TRUE, GL.GL_TRUE, GL.GL_TRUE, GL.GL_TRUE)

        # draw polygon into color buffer
        GL.glBegin(GL.GL_POLYGON)
        GL.glVertex2f(0, 0)
        GL.glVertex2f(width, 0)
        GL.glVertex2f(width, height)
        GL.glVertex2f(0, height)
        GL.glEnd()

        GL.glDisable(GL.GL_STENCIL_TEST)

    def __render_texture(self, width, height, texture):
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_MIRRORED_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_MIRRORED_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0, 0)
        GL.glVertex2f(0, 0)
        GL.glTexCoord2f(1, 0)
        GL.glVertex2f(width, 0)
        GL.glTexCoord2f(1, 1)
        GL.glVertex2f(width, height)
        GL.glTexCoord2f(0, 1)
        GL.glVertex2f(0, height)
        GL.glEnd()
        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def __apply_blur(self, width, height, texture, blur_texture, falloff):
        GL.glUseProgram(self.__blur_shader_program)
        GL.glUniform1f(self.__uniform_falloff, falloff / width)

        # the first pass of blur in vertical direction
        GL.glFramebufferTexture2D(
            GL.GL_FRAMEBUFFER,
            GL.GL_COLOR_ATTACHMENT0,
            GL.GL_TEXTURE_2D,
            blur_texture,
            0)
        GL.glUniform1f(self.__uniform_horiz, False)
        self.__render_texture(width, height, texture)

        # the second pass of blur in horizontal direction
        GL.glFramebufferTexture2D(
            GL.GL_FRAMEBUFFER,
            GL.GL_COLOR_ATTACHMENT0,
            GL.GL_TEXTURE_2D,
            texture,
            0)
        GL.glUniform1f(self.__uniform_horiz, True)
        self.__render_texture(width, height, blur_texture)

    def __set_texture_unit(self, texture, texture_unit):
        GL.glActiveTexture(texture_unit)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_MIRRORED_REPEAT)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_MIRRORED_REPEAT)
        GL.glActiveTexture(GL.GL_TEXTURE0)

    def __upload_ssbo_data(self, ccs):
        data = bytearray()
        data.extend(struct.pack("i", len(ccs)))
        for cc in ccs:
            if cc.mute: continue
            is_region = 1.0 if cc.region else 0.0
            data.extend(struct.pack("f", is_region))
            data.extend(struct.pack("f", float(len(cc.nodes))))
            for node in cc.nodes:
                if isinstance(node, ColorTimer):
                    mute = 0.0 if node.mute else 1.0
                    data.extend(struct.pack(
                        "f3f3f3fff", # Format : 1 float for type, 3 for slope, 3 for offset, 3 for power, 1 for sat, 1 for mute (11 floats in total)
                        0.0, # Type identifier for ColorTimer
                        *node.slope,
                        *node.offset,
                        *node.power,
                        node.saturation,
                        mute))
                if isinstance(node, Grade):
                    mute = 0.0 if node.mute else 1.0
                    data.extend(struct.pack(
                        "f3f3f3f3f3f3ff",
                        1.0, # Type identifier for Grade : 1 float for type, 19 floats for Grade
                        *node.blackpoint,
                        *node.whitepoint,
                        *node.lift,
                        *node.gain,
                        *node.multiply,
                        *node.gamma,
                        mute))
        self.__ssbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.__ssbo)
        GL.glBufferData(GL.GL_SHADER_STORAGE_BUFFER, len(data), bytes(data), GL.GL_STATIC_DRAW)
        GL.glBindBufferBase(GL.GL_SHADER_STORAGE_BUFFER, 16, self.__ssbo)

    def __get_source_resolution(self, source):
        smi = rvc.sourceMediaInfo(source)
        return smi["width"], smi["height"]

    def pre_render(self, event):
        """
        This function is triggered by the "pre-render" RV's event. It uploads the neccessary data
        for the color corrector shader. It also generates mask textures
        for each region color correction.
        """
        if not self.__session.viewport.feedback.is_visible:
            return
        frame = rve.sourceFrame(rvc.frame())
        source = self.__get_current_source_node_f(frame)
        if source is None:
            return
        clip_id = self.__session.viewport.current_clip
        if not clip_id: return
        clip = self.__session.get_clip(clip_id)
        clip_ccs = []
        if self.__session.viewport.feedback.are_clip_ccs_visible:
            clip_ccs = clip.color_corrections.clip_ccs
        frame_ccs = []
        if self.__session.viewport.feedback.are_frame_ccs_visible:
            frame_ccs = clip.color_corrections.frame_ccs.get(frame, [])
        ccs =  clip_ccs + frame_ccs
        if not ccs: return
        ccs = [clip.color_corrections.id_to_cc[cc_id] for cc_id in ccs]
        if not self.__session.viewport.feedback.are_region_ccs_visible:
            ccs_without_region = []
            for cc in ccs:
                if cc.region: continue
                ccs_without_region.append(cc)
            ccs = ccs_without_region
        if not ccs: return
        try:
            width, height = self.__get_source_resolution(source)
            fbo, stencil_texture, blur_texture = None, None, None
            fbo, stencil_texture, blur_texture = self.__create_fbo_and_textures(width, height)
            for index, cc in enumerate(ccs):
                if not cc.region: continue
                GL.glUseProgram(0)
                texture = GL.glGenTextures(1)
                self.__textures.append(texture)
                GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
                GL.glTexImage2D(
                    GL.GL_TEXTURE_2D,
                    0,
                    GL.GL_RGBA,
                    width,
                    height,
                    0,
                    GL.GL_RGBA,
                    GL.GL_FLOAT,
                    None)
                GL.glFramebufferTexture2D(
                    GL.GL_FRAMEBUFFER,
                    GL.GL_COLOR_ATTACHMENT0,
                    GL.GL_TEXTURE_2D,
                    texture,
                    0)

                GL.glClearColor(0.0, 0.0, 0.0, 0.0)
                GL.glClear(GL.GL_COLOR_BUFFER_BIT)

                for shape in cc.region.shapes:
                    points = [point.__getstate__() for point in shape.points]
                    points = [itview_to_rv(width, height, *point) for point in points]
                    if not points:
                        continue

                    # draw polygon with stencil test
                    self.__render_polygon_with_stencil_test(width, height, points)

                if not cc.region.shapes:
                    points = [
                        itview_to_rv(width, height, -10.0, -10.0),
                        itview_to_rv(width, height, +10.0, -10.0),
                        itview_to_rv(width, height, +10.0, +10.0),
                        itview_to_rv(width, height, -10.0, +10.0)]
                    self.__render_polygon_with_stencil_test(width, height, points)

                # apply blur
                self.__apply_blur(width, height, texture, blur_texture, cc.region.falloff)

                # assign texture to a texture unit
                self.__set_texture_unit(texture, GL.GL_TEXTURE0 + 16 + index)
            # upload ssbo data to GPU
            self.__upload_ssbo_data(ccs)

        finally:
            GL.glUseProgram(0)
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
            if fbo is not None:
                GL.glDeleteFramebuffers(1, [fbo])
                fbo = None
            if stencil_texture is not None:
                GL.glDeleteTextures([stencil_texture])
                stencil_texture = None
            if blur_texture is not None:
                GL.glDeleteTextures([blur_texture])
                blur_texture = None

            # reset viewport and projections
            domain = event.domain()
            GL.glViewport(0, 0, int(domain[0]), int(domain[1]))
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            GL.glOrtho(0, domain[0], 0, domain[1], -1000000, +1000000)
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()

    def render(self, event):
        """
        This function is triggered by the "render" RV's event. It renders the mask textures
        (for debugging purposes).
        """
        if len(self.__textures) == 0:
            return

        sources = rvc.sourcesAtFrame(rvc.frame())
        if len(sources) != 1:
            return

        width, height = self.__get_source_resolution(sources[0])

        GL.glColor(1.0, 1.0, 1.0)
        GL.glLineWidth(1.0)

        for i, texture in enumerate(self.__textures):
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            GL.glOrtho(0, width, 0, height, -1000000, +1000000)

            GL.glBegin(GL.GL_QUADS)
            GL.glTexCoord2f(0, 0)
            GL.glVertex2f(100*i + 5, 100)
            GL.glTexCoord2f(1, 0)
            GL.glVertex2f(100*(i+1), 100)
            GL.glTexCoord2f(1, 1)
            GL.glVertex2f(100*(i+1), 200)
            GL.glTexCoord2f(0, 1)
            GL.glVertex2f(100*i + 5, 200)
            GL.glEnd()

            GL.glDisable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

            GL.glBegin(GL.GL_LINE_LOOP)
            GL.glVertex2f(100*i + 5, 100)
            GL.glVertex2f(100*(i+1), 100)
            GL.glVertex2f(100*(i+1), 200)
            GL.glVertex2f(100*i + 5, 200)
            GL.glEnd()

    def post_render(self, event):
        """
        This function is triggered by the "post-render" RV's event. It cleans up the resources.
        """
        if self.__ssbo is not None:
            GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, 0)
            GL.glDeleteBuffers(1, [self.__ssbo])
            self.__ssbo = None
        if self.__textures:
            GL.glDeleteTextures(self.__textures)
            self.__textures = []

    def __set_color_channel_mode(self, mode):
        groups = rvc.nodesOfType("RVViewPipelineGroup")
        for group in groups:
            nodes = rvc.getStringProperty(group + ".pipeline.nodes")

            if not ("ChannelSelect" in nodes):
                nodes += ["ChannelSelect"]
                rvc.setStringProperty(group + ".pipeline.nodes", nodes, True)

            nodes = rvc.nodesOfType("ChannelSelect")
            for node in nodes:
                rvc.setIntProperty(node + ".parameters.channel", [mode], True)

    def _refresh(self, clip_id):
        cc_node = self.__get_color_correct_node(clip_id)
        if not cc_node: return
        prop = f"{cc_node}.parameters.refresh"
        try:
            counter = get_property(prop)[0]
        except:
            counter = 0
        set_property(prop, [counter + 1])

    def __del__(self):
        """
        Destructor to clean up resources.
        """
        if self.__blur_shader_program is not None:
            GL.glDeleteProgram(self.__blur_shader_program)
            self.__blur_shader_program = None

    def __get_color_correct_node(self, clip_id):
        clip = self.__session.get_clip(clip_id)
        source_group = clip.get_custom_attr("rv_source_group")
        if not source_group: return
        source_node = f"{source_group}_source"
        cc_node = rve.associatedNode("ColorCorrector", source_node)
        if not cc_node:
            nodes = get_property(f"{source_group}_colorPipeline.pipeline.nodes")
            nodes = ["ColorCorrector"] + nodes
            set_property(f"{source_group}_colorPipeline.pipeline.nodes", nodes)
            cc_node = rve.associatedNode("ColorCorrector", f"{source_node}")
        return cc_node
