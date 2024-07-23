"""Color corrector module."""

import json
import struct
from uuid import uuid4
from OpenGL import GL
from OpenGL.GL import shaders as glShaders
from OpenGL.GL.ARB import framebuffer_object
from rv import commands as rvc
from rv import extra_commands as rve
from rv import runtime
from exceptions import SingletonInstantiatedException

BLUR_SHADER = """
#version 130

uniform sampler2D mask;
uniform float falloff;
uniform bool horiz;

void main()
{
    vec2 size = textureSize(mask, 0);
    float diameter = falloff * size.y; // in pixels
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


class ColorCorrection:
    """
    A class representing color correction parameters.
    """

    def __init__(self,
                 slope=(1, 1, 1),
                 offset=(0, 0, 0),
                 power=(1, 1, 1),
                 saturation=1,
                 blackpoint=(0, 0, 0),
                 whitepoint=(1, 1, 1),
                 lift=(0, 0, 0),
                 gain=(1, 1, 1),
                 multiply=(1, 1, 1),
                 gamma=(1, 1, 1)):
        """
        Initializes a ColorCorrection instance with default or provided values.

        Args:
            slope (tuple): Slope for each color channel. Default is (1, 1, 1).
            offset (tuple): Offset for each color channel. Default is (0, 0, 0).
            power (tuple): Power for each color channel. Default is (1, 1, 1).
            saturation (float): Saturation value. Default is 1.
            blackpoint (tuple): Blackpoint for each color channel. Default is (0, 0, 0).
            whitepoint (tuple): Whitepoint for each color channel. Default is (1, 1, 1).
            lift (tuple): Lift for each color channel. Default is (0, 0, 0).
            gain (tuple): Gain for each color channel. Default is (1, 1, 1).
            multiply (tuple): Multiply for each color channel. Default is (1, 1, 1).
            gamma (tuple): Gamma for each color channel. Default is (1, 1, 1).
        """

        # Color Timer
        self.slope = list(map(float, slope))
        self.offset = list(map(float, offset))
        self.power = list(map(float, power))
        self.saturation = float(saturation)

        # Grade
        self.blackpoint = list(map(float, blackpoint))
        self.whitepoint = list(map(float, whitepoint))
        self.lift = list(map(float, lift))
        self.gain = list(map(float, gain))
        self.multiply = list(map(float, multiply))
        self.gamma = list(map(float, gamma))

    def update(self,
               slope=None,
               offset=None,
               power=None,
               saturation=None,
               blackpoint=None,
               whitepoint=None,
               lift=None,
               gain=None,
               multiply=None,
               gamma=None):
        """
        Updates the color correction values if new values are provided.

        Args:
            slope (tuple): New slope values for each color channel.
            offset (tuple): New offset values for each color channel.
            power (tuple): New power values for each color channel.
            saturation (float): New saturation value.
            blackpoint (tuple): New blackpoint values for each color channel.
            whitepoint (tuple): New whitepoint values for each color channel.
            lift (tuple): New lift values for each color channel.
            gain (tuple): New gain values for each color channel.
            multiply (tuple): New multiply values for each color channel.
            gamma (tuple): New gamma values for each color channel.
        """
        if slope is not None:
            self.slope = list(map(float, slope))
        if offset is not None:
            self.offset = list(map(float, offset))
        if power is not None:
            self.power = list(map(float, power))
        if saturation is not None:
            self.saturation = float(saturation)
        if blackpoint is not None:
            self.blackpoint = list(map(float, blackpoint))
        if whitepoint is not None:
            self.whitepoint = list(map(float, whitepoint))
        if lift is not None:
            self.lift = list(map(float, lift))
        if gain is not None:
            self.gain = list(map(float, gain))
        if multiply is not None:
            self.multiply = list(map(float, multiply))
        if gamma is not None:
            self.gamma = list(map(float, gamma))

    def load(self, node):
        """
        Loads color correction values from a specified node.

        Args:
            node (str): Node identifier for property retrieval.
        """
        ColorCorrection.update(self,
            get_first_value(f"{node}.slope"),
            get_first_value(f"{node}.offset"),
            get_first_value(f"{node}.power"),
            get_first_value(f"{node}.saturation"),
            get_first_value(f"{node}.blackpoint"),
            get_first_value(f"{node}.whitepoint"),
            get_first_value(f"{node}.lift"),
            get_first_value(f"{node}.gain"),
            get_first_value(f"{node}.multiply"),
            get_first_value(f"{node}.gamma"))

    def store(self, node):
        """
        Stores color correction values into a specified node.

        Args:
            node (str): Node identifier for property setting.
        """
        set_property(f"{node}.slope", [self.slope])
        set_property(f"{node}.offset", [self.offset])
        set_property(f"{node}.power", [self.power])
        set_property(f"{node}.saturation", [self.saturation])
        set_property(f"{node}.blackpoint", [self.blackpoint])
        set_property(f"{node}.whitepoint", [self.whitepoint])
        set_property(f"{node}.lift", [self.lift])
        set_property(f"{node}.gain", [self.gain])
        set_property(f"{node}.multiply", [self.multiply])
        set_property(f"{node}.gamma", [self.gamma])

    def to_bytes(self):
        """
        Converts color correction values to a bytes object.

        Returns:
            Bytes object representing the color correction values.
        """
        return struct.pack("f" * 28,
            self.slope[0], self.slope[1], self.slope[2],
            self.offset[0], self.offset[1], self.offset[2],
            self.power[0], self.power[1], self.power[2],
            self.saturation,
            self.blackpoint[0], self.blackpoint[1], self.blackpoint[2],
            self.whitepoint[0], self.whitepoint[1], self.whitepoint[2],
            self.lift[0], self.lift[1], self.lift[2],
            self.gain[0], self.gain[1], self.gain[2],
            self.multiply[0], self.multiply[1], self.multiply[2],
            self.gamma[0], self.gamma[1], self.gamma[2])


class RegionColorCorrection(ColorCorrection):
    """
    A class representing region color correction parameters.
    """

    def __init__(self,
                 slope=(1, 1, 1),
                 offset=(0, 0, 0),
                 power=(1, 1, 1),
                 saturation=1,
                 blackpoint=(0, 0, 0),
                 whitepoint=(1, 1, 1),
                 lift=(0, 0, 0),
                 gain=(1, 1, 1),
                 multiply=(1, 1, 1),
                 gamma=(1, 1, 1),
                 falloff=0,
                 guid=None):
        """
        Initializes a RegionColorCorrection instance with default or provided values.

        Args:
            slope (tuple): Slope for each color channel. Default is (1, 1, 1).
            offset (tuple): Offset for each color channel. Default is (0, 0, 0).
            power (tuple): Power for each color channel. Default is (1, 1, 1).
            saturation (float): Saturation value. Default is 1.
            blackpoint (tuple): Blackpoint for each color channel. Default is (0, 0, 0).
            whitepoint (tuple): Whitepoint for each color channel. Default is (1, 1, 1).
            lift (tuple): Lift for each color channel. Default is (0, 0, 0).
            gain (tuple): Gain for each color channel. Default is (1, 1, 1).
            multiply (tuple): Multiply for each color channel. Default is (1, 1, 1).
            gamma (tuple): Gamma for each color channel. Default is (1, 1, 1).
            falloff (float): Falloff value. Default is 0.
            guid (str): GUID value. Default is None.
        """
        self.guid = guid
        self.falloff = float(falloff)
        super().__init__(slope, offset, power, saturation,
            blackpoint, whitepoint, lift, gain, multiply, gamma)

    def update(self,
               slope=None,
               offset=None,
               power=None,
               saturation=None,
               blackpoint=None,
               whitepoint=None,
               lift=None,
               gain=None,
               multiply=None,
               gamma=None,
               falloff=None,
               guid=None):
        """
        Updates the region color correction values if new values are provided.

        Args:
            slope (tuple): New slope values for each color channel.
            offset (tuple): New offset values for each color channel.
            power (tuple): New power values for each color channel.
            saturation (float): New saturation value.
            blackpoint (tuple): New blackpoint values for each color channel.
            whitepoint (tuple): New whitepoint values for each color channel.
            lift (tuple): New lift values for each color channel.
            gain (tuple): New gain values for each color channel.
            multiply (tuple): New multiply values for each color channel.
            gamma (tuple): New gamma values for each color channel.
            falloff (float): New falloff value.
            guid (str): New GUID value.
        """
        if guid is not None:
            self.guid = guid
        if falloff is not None:
            self.falloff = float(falloff)
        super().update(slope, offset, power, saturation,
            blackpoint, whitepoint, lift, gain, multiply, gamma)

    def load(self, node):
        """
        Loads region color correction values from a specified node.

        Args:
            node (str): Node identifier for property retrieval.
        """
        RegionColorCorrection.update(self,
            falloff=get_first_value(f"{node}.falloff"))
        super().load(node)

    def store(self, node):
        """
        Stores region color correction values into a specified node.

        Args:
            node (str): Node identifier for property setting.
        """
        set_property(f"{node}.falloff", [self.falloff])
        super().store(node)

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
        return None
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
    if values is None:
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
    old_values = get_property(prop) if rvc.propertyExists(prop) else []
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


class ColorCorrectorApi:
    """
    A class that provides an interface for color correction operations.
    It also implements the rendering of the color correction on RV side.
    """
    __instance = None

    @classmethod
    def get_instance(cls):
        """Returns the sigleton instance of ActionsHeader"""
        if cls.__instance is None:
            cls.__instance = ColorCorrectorApi()
        return cls.__instance

    def __init__(self):
        """
        Initializes the ColorCorrectorApi instance.
        """
        if ColorCorrectorApi.__instance is not None:
            raise SingletonInstantiatedException()
        super().__init__()
        ColorCorrectorApi.__instance = self

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

    def __del__(self):
        """
        Destructor to clean up resources.
        """
        if self.__blur_shader_program is not None:
            GL.glDeleteProgram(self.__blur_shader_program)
            self.__blur_shader_program = None

    def __get_source_and_node(self, frame, create=False):
        # check the image source
        sources = rvc.sourcesAtFrame(frame)
        if len(sources) != 1:
            return None, None
        source = sources[0]

        # create the color corrector node if specified
        if create:
            nodes = rve.nodesInEvalPath(frame, "ColorCorrector")
            if not nodes:
                pgs = rve.nodesInEvalPath(rvc.frame(), "RVColorPipelineGroup")
                for pg in pgs:
                    nodes = get_property(pg + ".pipeline.nodes")
                    nodes = ["ColorCorrector"] + nodes
                    set_property(pg + ".pipeline.nodes", nodes)

        # check the color corrector node
        nodes = rve.nodesInEvalPath(frame, "ColorCorrector")
        if len(nodes) != 1:
            return source, None
        node = nodes[0]

        return source, node

    def __get_clip_cc(self, frame):
        source, node = self.__get_source_and_node(frame)
        if None in (source, node):
            return ColorCorrection()

        cc = ColorCorrection()
        cc.load(f"{node}.clip")
        return cc

    def __get_frame_cc(self, frame):
        source, node = self.__get_source_and_node(frame)
        if None in (source, node):
            return ColorCorrection()
        source_frame = rve.sourceFrame(frame)

        cc = ColorCorrection()
        cc.load(f"{node}.frame:{source_frame}")
        return cc

    def __get_region_ccs(self, frame):
        source, node = self.__get_source_and_node(frame)
        if None in (source, node):
            return []

        # check if some color correction regions exist
        source_frame = rve.sourceFrame(frame)
        guids = get_property(f"{node}.frame:{source_frame}.regions")
        if not guids:
            return []

        ccs = []
        for guid in guids:
            cc = RegionColorCorrection(guid=guid)
            cc.load(f"{node}.region:{guid}")
            ccs.append(cc)
        return ccs

    def __refresh(self, node):
        prop = f"{node}.parameters.refresh"
        try:
            counter = get_property(prop)[0]
        except:
            counter = 0
        set_property(prop, [counter + 1])

    def get_clip_cc(self, frame):
        """
        Retrieve clip color correction at a specific frame.

        Args:
            frame: The frame for which a clip color correction is retrieved.

        Returns:
            Clip color correction dictionary, for example:
            {
                'slope': [1.0, 1.0, 1.0],
                'offset': [0.0, 0.0, 0.0],
                'power': [1.0, 1.0, 1.0],
                'saturation': 1.0,
                'blackpoint': [0.0, 0.0, 0.0],
                'whitepoint': [1.0, 1.0, 1.0],
                'lift': [0.0, 0.0, 0.0],
                'gain': [1.0, 1.0, 1.0],
                'multiply': [1.0, 1.0, 1.0],
                'gamma': [1.0, 1.0, 1.0]
            }
        """
        try:
            cc = self.__get_clip_cc(frame)
            return vars(cc)
        except Exception as e:
            return {"exception": str(e)}

    def set_clip_cc(self, frame, cc):
        """
        Set clip color correction at a specific frame.

        Args:
            frame: The frame for which a clip color correction is set.
            cc: Clip color correction dictionary to be set, for example:
                {
                    'slope': [1.0, 1.0, 1.0],
                    'offset': [0.0, 0.0, 0.0],
                    'power': [1.0, 1.0, 1.0],
                    'saturation': 1.0,
                    'blackpoint': [0.0, 0.0, 0.0],
                    'whitepoint': [1.0, 1.0, 1.0],
                    'lift': [0.0, 0.0, 0.0],
                    'gain': [1.0, 1.0, 1.0],
                    'multiply': [1.0, 1.0, 1.0],
                    'gamma': [1.0, 1.0, 1.0]
                }
                Partial clip color correction updates are also possible, for example:
                {
                    'saturation': 2.0
                }
        """
        try:
            source, node = self.__get_source_and_node(frame, create=True)
            if None in (source, node):
                raise RuntimeError(f"No source at frame {frame}")

            prop = f"{node}.clip"
            stored_cc = ColorCorrection()
            stored_cc.load(prop)
            stored_cc.update(**cc)
            stored_cc.store(prop)

            self.__refresh(node)
            return None
        except Exception as e:
            return {"exception": str(e)}

    def get_frame_cc(self, frame):
        """
        Retrieve frame color correction for a specific frame.

        Args:
            frame: The frame for which a frame color correction is retrieved.

        Returns:
            Frame color correctiondictionary, for example:
            {
                'slope': [1.0, 1.0, 1.0],
                'offset': [0.0, 0.0, 0.0],
                'power': [1.0, 1.0, 1.0],
                'saturation': 1.0,
                'blackpoint': [0.0, 0.0, 0.0],
                'whitepoint': [1.0, 1.0, 1.0],
                'lift': [0.0, 0.0, 0.0],
                'gain': [1.0, 1.0, 1.0],
                'multiply': [1.0, 1.0, 1.0],
                'gamma': [1.0, 1.0, 1.0]
            }
        """
        try:
            cc = self.__get_frame_cc(frame)
            return vars(cc)
        except Exception as e:
            return {"exception": str(e)}

    def set_frame_cc(self, frame, cc):
        """
        Set frame color correction for a specific frame.

        Args:
            frame: The frame for which a frame color correction is set.
            cc: Frame color correction dictionary to be set, for example:
                {
                    'slope': [1.0, 1.0, 1.0],
                    'offset': [0.0, 0.0, 0.0],
                    'power': [1.0, 1.0, 1.0],
                    'saturation': 1.0,
                    'blackpoint': [0.0, 0.0, 0.0],
                    'whitepoint': [1.0, 1.0, 1.0],
                    'lift': [0.0, 0.0, 0.0],
                    'gain': [1.0, 1.0, 1.0],
                    'multiply': [1.0, 1.0, 1.0],
                    'gamma': [1.0, 1.0, 1.0]
                }
                Partial frame color correction updates are also possible, for example:
                {
                    'saturation': 2.0
                }
        """
        try:
            source, node = self.__get_source_and_node(frame, create=True)
            if None in (source, node):
                raise RuntimeError(f"No source at frame {frame}")
            source_frame = rve.sourceFrame(frame)

            prop = f"{node}.frame:{source_frame}"
            stored_cc = ColorCorrection()
            stored_cc.load(prop)
            stored_cc.update(**cc)
            stored_cc.store(prop)

            self.__refresh(node)
            return None
        except Exception as e:
            return {"exception": str(e)}

    def create_region_cc(self, frame):
        """
        Create a new region color correction for a specific frame.

        Args:
            frame: The frame for which a region color correction is created.

        Returns:
            GUID of the newly created region color correction.
        """
        try:
            source, node = self.__get_source_and_node(frame, create=True)
            if None in (source, node):
                raise RuntimeError(f"No source at frame {frame}")
            source_frame = rve.sourceFrame(frame)

            cc = RegionColorCorrection(guid=uuid4().hex)
            append_property(f"{node}.frame:{source_frame}.regions", [cc.guid])
            cc.store(f"{node}.region:{cc.guid}")

            return vars(cc)
        except Exception as e:
            return {"exception": str(e)}

    def delete_region_cc(self, frame, cc_guid):
        """
        Delete a region color correction from a specific frame using its GUID.

        Args:
            frame: The frame for which the region color correction is deleted.
            cc_guid: GUID of the region color correction to be deleted.
        """
        try:
            source, node = self.__get_source_and_node(frame)
            if None in (source, node):
                raise RuntimeError(f"No source at frame {frame}")
            source_frame = rve.sourceFrame(frame)

            regions_property = f"{node}.frame:{source_frame}.regions"
            guids = get_property(regions_property)
            if cc_guid not in guids:
                return None

            guids.remove(cc_guid)
            if guids:
                set_property(regions_property, guids)
            else:
                delete_property(regions_property)

            delete_property(f"{node}.region:{cc_guid}.falloff")
            delete_property(f"{node}.region:{cc_guid}.slope")
            delete_property(f"{node}.region:{cc_guid}.offset")
            delete_property(f"{node}.region:{cc_guid}.power")
            delete_property(f"{node}.region:{cc_guid}.saturation")
            delete_property(f"{node}.region:{cc_guid}.blackpoint")
            delete_property(f"{node}.region:{cc_guid}.whitepoint")
            delete_property(f"{node}.region:{cc_guid}.lift")
            delete_property(f"{node}.region:{cc_guid}.gain")
            delete_property(f"{node}.region:{cc_guid}.multiply")
            delete_property(f"{node}.region:{cc_guid}.gamma")

            shapes_property = f"{node}.region:{cc_guid}.shapes"
            guids = get_property(shapes_property)
            if guids is None:
                return None

            delete_property(shapes_property)
            for guid in guids:
                delete_property(f"{node}.shape:{guid}.points")

            self.__refresh(node)
            return None
        except Exception as e:
            return {"exception": str(e)}

    def get_region_cc(self, frame, cc_guid):
        """
        Retrieve region color correction for a specific frame and GUID.

        Args:
            frame: The frame for which region color correction is retrieved.
            cc_guid: GUID of the region color correction.

        Returns:
            Region color correction dictionary, for example:
            {
                'guid': 'b22a2099bd4647efa9d9c0eef80ea058',
                'falloff': 0.0,
                'slope': [1.0, 1.0, 1.0],
                'offset': [0.0, 0.0, 0.0],
                'power': [1.0, 1.0, 1.0],
                'saturation': 1.0,
                'blackpoint': [0.0, 0.0, 0.0],
                'whitepoint': [1.0, 1.0, 1.0],
                'lift': [0.0, 0.0, 0.0],
                'gain': [1.0, 1.0, 1.0],
                'multiply': [1.0, 1.0, 1.0],
                'gamma': [1.0, 1.0, 1.0]
            }
        """
        try:
            source, node = self.__get_source_and_node(frame)
            if None in (source, node):
                raise RuntimeError(f"No source at frame {frame}")
            source_frame = rve.sourceFrame(frame)

            guids = get_property(f"{node}.frame:{source_frame}.regions")
            if cc_guid not in guids:
                raise RuntimeError(f"No region CC with guid {cc_guid} found at frame {frame}")

            stored_cc = RegionColorCorrection(guid=cc_guid)
            stored_cc.load(f"{node}.region:{cc_guid}")

            return vars(stored_cc)
        except Exception as e:
            return {"exception": str(e)}

    def set_region_cc(self, frame, cc_guid, cc):
        """
        Set region color correction for a specific frame and GUID.

        Args:
            frame: The frame for which a region color correction is set.
            cc_guid: GUID of the region color correction.
            cc: Region color correction dictionary to be set, for example:
                {
                    'guid': 'b22a2099bd4647efa9d9c0eef80ea058',
                    'falloff': 0.0,
                    'slope': [1.0, 1.0, 1.0],
                    'offset': [0.0, 0.0, 0.0],
                    'power': [1.0, 1.0, 1.0],
                    'saturation': 1.0,
                    'blackpoint': [0.0, 0.0, 0.0],
                    'whitepoint': [1.0, 1.0, 1.0],
                    'lift': [0.0, 0.0, 0.0],
                    'gain': [1.0, 1.0, 1.0],
                    'multiply': [1.0, 1.0, 1.0],
                    'gamma': [1.0, 1.0, 1.0]
                }
                Partial region color correction updates are also possible, for example:
                {
                    'falloff': 0.1
                }
        """
        try:
            source, node = self.__get_source_and_node(frame)
            if None in (source, node):
                raise RuntimeError(f"No source at frame {frame}")
            source_frame = rve.sourceFrame(frame)

            guids = get_property(f"{node}.frame:{source_frame}.regions")
            if cc_guid not in guids:
                raise RuntimeError(f"No region CC with guid {cc_guid} found at frame {frame}")

            prop = f"{node}.region:{cc_guid}"
            stored_cc = RegionColorCorrection(guid=cc_guid)
            stored_cc.load(prop)
            stored_cc.update(**cc)
            stored_cc.store(prop)

            self.__refresh(node)
            return None
        except Exception as e:
            return {"exception": str(e)}

    def get_region_ccs(self, frame):
        """
        Retrieve all region color corrections for a specific frame.

        Args:
            frame: The frame for which region color corrections are retrieved.

        Returns:
            List of region color correction in the specified frame, for example:
            [
                {
                    'guid': '0b810853b99f48c28dcf3a5be4582bb5',
                    'falloff': 0.1,
                    'slope': [1.0, 2.0, 1.0],
                    'offset': [0.0, 0.0, 0.0],
                    'power': [1.0, 1.0, 1.0],
                    'saturation': 1.0,
                    'blackpoint': [0.0, 0.0, 0.0],
                    'whitepoint': [1.0, 1.0, 1.0],
                    'lift': [0.0, 0.0, 0.0],
                    'gain': [1.0, 1.0, 1.0],
                    'multiply': [1.0, 1.0, 1.0],
                    'gamma': [1.0, 1.0, 1.0]
                },
                {
                    'guid': 'b22a2099bd4647efa9d9c0eef80ea058',
                    'falloff': 0.0,
                    'slope': [2.0, 1.0, 1.0],
                    'offset': [0.0, 0.0, 0.0],
                    'power': [1.0, 1.0, 1.0],
                    'saturation': 1.0,
                    'blackpoint': [0.0, 0.0, 0.0],
                    'whitepoint': [1.0, 1.0, 1.0],
                    'lift': [0.0, 0.0, 0.0],
                    'gain': [1.0, 1.0, 1.0],
                    'multiply': [1.0, 1.0, 1.0],
                    'gamma': [1.0, 1.0, 1.0]
                }
            ]
        """
        try:
            ccs = self.__get_region_ccs(frame)
            return [vars(cc) for cc in ccs]
        except Exception as e:
            return {"exception": str(e)}

    def reorder_region_ccs(self, frame, cc_guids):
        """
        Reorder region color corrections at a specific frame based on the provided GUIDs.

        Args:
            frame: The frame in which region color corrections are reordered.
            cc_guids: List of region color correction GUIDs specifying the new order.
        """
        try:
            source, node = self.__get_source_and_node(frame)
            if None in (source, node):
                raise RuntimeError(f"No source at frame {frame}")
            source_frame = rve.sourceFrame(frame)

            guids = get_property(f"{node}.frame:{source_frame}.regions")
            if sorted(guids) != sorted(cc_guids):
                raise RuntimeError("Missing or superfluous region CC guids")

            set_property(f"{node}.frame:{source_frame}.regions", cc_guids)

            self.__refresh(node)
            return None
        except Exception as e:
            return {"exception": str(e)}

    def create_shape(self, frame, cc_guid):
        """
        Create a shape for a region color correction at a specific frame.

        Args:
            frame: The frame for which the shape is created.
            cc_guid: GUID of the region color correction.

        Returns:
            GUID of the newly created shape.
        """

        try:
            source, node = self.__get_source_and_node(frame)
            if None in (source, node):
                raise RuntimeError(f"No source at frame {frame}")
            source_frame = rve.sourceFrame(frame)

            guids = get_property(f"{node}.frame:{source_frame}.regions")
            if cc_guid not in guids:
                raise RuntimeError(f"No region CC with guid {cc_guid} found at frame {frame}")

            shape_guid = uuid4().hex
            append_property(f"{node}.region:{cc_guid}.shapes", [shape_guid])

            return shape_guid
        except Exception as e:
            return {"exception": str(e)}

    def set_drawing_in_progress(self, value):
        if value:
            runtime.eval(
            "require rv_state_mngr;"
            "rv_state_mngr.disable_frame_change_mouse_events();" ,[])
        else:
            runtime.eval(
            "require rv_state_mngr;"
            "rv_state_mngr.enable_frame_change_mouse_events();" ,[])

    def append_point_to_shape(self, frame, cc_guid, shape_guid, x, y):
        """
        Append a point to a specific shape for a region color correction.

        Args:
            frame: The frame containing the region color correction.
            cc_guid: GUID of the region color correction.
            shape_guid: GUID of the shape to which the point is appended.
            x: X-coordinate of the point (in the screen space)
            y: Y-coordinate of the point (in the screen space)
        """
        try:
            source, node = self.__get_source_and_node(frame)
            if None in (source, node):
                raise RuntimeError(f"No source at frame {frame}")

            guids = get_property(f"{node}.region:{cc_guid}.shapes")
            if shape_guid not in guids:
                raise RuntimeError(f"No shape with guid {shape_guid} found at region CC {cc_guid}")

            point = (float(x), float(y))
            point_info = rvc.imagesAtPixel(point, None, True)[0]
            x, y = rvc.eventToImageSpace(point_info["name"], point, True)

            append_property(f"{node}.shape:{shape_guid}.points", [[x, y]])

            self.__refresh(node)
            return None
        except Exception as e:
            return {"exception": str(e)}

    def append_points_to_shape(self, frame, cc_guid, shape_guid, points):
        """
        Append a list of points to a specific shape for a region color correction.

        Args:
            frame: The frame containing the region color correction.
            cc_guid: GUID of the region color correction.
            shape_guid: GUID of the shape to which the point is appended.
            points: list of XY-coordinates of the point (in the screen space)
        """
        try:
            source, node = self.__get_source_and_node(frame)
            if None in (source, node):
                raise RuntimeError(f"No source at frame {frame}")

            guids = get_property(f"{node}.region:{cc_guid}.shapes")
            if shape_guid not in guids:
                raise RuntimeError(f"No shape with guid {shape_guid} found at region CC {cc_guid}")

            coords = []
            for x, y in points:
                point = (float(x), float(y))
                point_info = rvc.imagesAtPixel(point, None, True)[0]
                x, y = rvc.eventToImageSpace(point_info["name"], point, True)
                coords.append([x, y])

            append_property(f"{node}.shape:{shape_guid}.points", coords)

            self.__refresh(node)
            return None
        except Exception as e:
            return {"exception": str(e)}

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
        GL.glUniform1f(self.__uniform_falloff, falloff)

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

    def __upload_ssbo_data(self, frame, region_ccs):
        clip_cc = self.__get_clip_cc(frame)
        frame_cc = self.__get_frame_cc(frame)

        data = bytearray()
        data.extend(clip_cc.to_bytes())
        data.extend(frame_cc.to_bytes())
        data.extend(struct.pack("i", len(region_ccs)))
        for region_cc in region_ccs:
            data.extend(region_cc.to_bytes())

        self.__ssbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.__ssbo)
        GL.glBufferData(GL.GL_SHADER_STORAGE_BUFFER, len(data), bytes(data), GL.GL_STATIC_DRAW)
        GL.glBindBufferBase(GL.GL_SHADER_STORAGE_BUFFER, 16, self.__ssbo)

    def __get_source_resolution(self, source):
        smi = rvc.sourceMediaInfo(source)
        return smi["width"], smi["height"]

    def pre_render(self):
        """
        This function is triggered by the "pre-render" RV's event. It uploads the neccessary data
        for the color corrector shader. It also generates mask textures
        for each region color correction.
        """
        frame = rvc.frame()
        source, node = self.__get_source_and_node(frame)
        if None in (source, node):
            return

        try:
            width, height = self.__get_source_resolution(source)

            fbo, stencil_texture, blur_texture = None, None, None
            fbo, stencil_texture, blur_texture = self.__create_fbo_and_textures(width, height)

            i = -1
            region_ccs = []
            for region_cc in self.__get_region_ccs(frame):

                GL.glUseProgram(0)

                shapes = get_property(f"{node}.region:{region_cc.guid}.shapes")
                if shapes is None:
                    continue

                i += 1
                region_ccs.append(region_cc)

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

                for shape in shapes:

                    points = get_property(f"{node}.shape:{shape}.points")
                    if not points:
                        continue

                    # draw polygon with stencil test
                    self.__render_polygon_with_stencil_test(width, height, points)

                # apply blur
                self.__apply_blur(width, height, texture, blur_texture, region_cc.falloff)

                # assign texture to a texture unit
                self.__set_texture_unit(texture, GL.GL_TEXTURE0 + 16 + i)

            # upload ssbo data to GPU
            self.__upload_ssbo_data(frame, region_ccs)

        finally:
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

    def render(self):
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

    def post_render(self):
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
