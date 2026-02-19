import re
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class VirtualMediaType:
    solid = "solid"
    smptebars = "smptebars"
    colorchart = "colorchart"
    noise = "noise"
    blank = "blank"
    black = "black"
    white = "white"
    grey = "grey"
    gray = "gray"
    hramp = "hramp"
    hbramp = "hbramp"
    hwramp = "hwramp"
    error = "error"


@dataclass(frozen=True)
class VirtualMediaOption:
    start = "start"
    end = "end"
    fps = "fps"
    increment = "inc"
    red = "red"
    green = "green"
    blue = "blue"
    grey = "grey"
    gray = "gray"
    alpha = "alpha"
    width = "width"
    height = "height"
    depth = "depth"
    interval = "interval"
    audio = "audio"
    frequency = "freq"
    amp = "amp"
    rate = "rate"
    hpan = "hpan"
    flash = "flash"
    filename = "filename"


class RVVirtualMediaGenerator:
    """
    A class that handles virtual media generation specific to RV
    The representational string used as a path is in ".movieproc" format
    """

    def __init__(self, session_api):
        self.__session_api = session_api

    def get_virtual_media_path(self, vm_type:str,
            ref_clip_id:Optional[str]=None,
            options:Optional[Dict[str, Any]]=None):
        """
        Create a virtual media path using optionally given clip media info
        and/or options and get a representational string.

        Args:
            vm_type (str):
                Represents the virtual media type to be used for creating the virtual media.
                The types may include black frames, color chart, or color bars.
                When only vm_type is given, virtual media will adopt default attributes.
                Refer to VirtualMediaType class.

        Kwargs:
            ref_clip_id (Optional[str]):
                Optional clip id that can be used as a reference for virtual media generation.
                This clip's media attributes will be applied to the virtual media.
                The virtual media will have the same properties as the clip of interest,
                such as resolution, media fps, media length (key in & key out).

            options (Optional[Dict[str, Any]]):
                Optional dictionary with key (str) as some modifiable virtual media attribute,
                and option's value as the value for the attribute.
                If some option is redundant from ref_clip_id, then
                options' attributes will override the clip's media attributes.
                Refer to VirtualMediaOption class.

        Returns:
            str: A string specifying the virtual media information,
                 which can be used as a path to create a virtual media clip
        """

        vm_format = ""
        vm_attrs = {}

        if ref_clip_id is not None:
            playlist_id = self.__session_api.get_playlist_of_clip(ref_clip_id)

            resolution = self.__session_api.get_attr_value(
                ref_clip_id, "resolution")
            width, height = self.__get_width_and_height(resolution)

            fps = round(self.__session_api.get_attr_value(
                ref_clip_id, "media_fps"), 2)

            key_in = self.__session_api.get_attr_value(
                ref_clip_id, "key_in")
            key_out = self.__session_api.get_attr_value(
                ref_clip_id, "key_out")

            vm_attrs = { VirtualMediaOption.width : width,
                         VirtualMediaOption.height : height,
                         VirtualMediaOption.fps : fps,
                         VirtualMediaOption.start : key_in,
                         VirtualMediaOption.end : key_out}

        if options is not None:
            vm_attrs.update(options)

        vm_format = ",".join(
            f"{key}={val}" for key, val in vm_attrs.items() if val is not None)

        if vm_format:
            vm_format = f",{vm_format}"

        vm_path = f"{vm_type}{vm_format}.movieproc"
        return vm_path

    def is_virtual_media(self, clip_id:str):
        """
        Check whether the given clip is a virtual media.

        Args:
            clip_id (str): Id of the Clip

        Returns:
            bool: True if the clip is a virtual media, otherwise False
        """
        media_path = self.__session_api.get_attr_value(
            clip_id, "media_path")
        return media_path.lower().endswith(".movieproc")

    def __get_width_and_height(self, resolution:str):
        match = re.match(r"(\d+)\s*x\s*(\d+)", resolution)
        if not match:
            return None, None
        return int(match.group(1)), int(match.group(2))
