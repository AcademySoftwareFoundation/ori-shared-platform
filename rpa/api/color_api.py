"""
Color API
=========

Manage viewport color-space and clip color-corrections.

Color-Corrections can be set either be set on the entire clip or on a particular Frame.

Multiple Clip-level color-corrections can be set on a particular clip and multiple
frame-level color-corrections can be set on a particular frame of a clip.

A color-correction can either be read-only or read-write.
"""

from rpa.delegate_mngr import DelegateMngr
from rpa.session_state.color_corrections import \
    ColorTimer, Grade, ColorCorrection
from PySide2 import QtCore
from typing import List, Union, Optional, Dict, Tuple


class ColorApi(QtCore.QObject):
    """
    A class that provides an interface for color operations.
    """
    SIG_CCS_MODIFIED = QtCore.Signal(str, object) # clip_id, frame
    # Gets emitted whenever any color-corrections associated with a
    # particular clip is either removed, added or moved.
    # If frame number emitted with signal is None, then it indicates that
    # clip level color-corrections list has been modified otherwise it
    # indicates frame level color-corrections.
    SIG_CC_MODIFIED = QtCore.Signal(str, str) # clip_id, cc_id
    # Gets emitted whenever any particular color-correction associated with a
    # particular clip is modified. This includes adding/removing
    # color-correction nodes, adding/removing regions, chaning
    # color-correction's name, mute/un-mute. The color-correction id could be
    # if of a color-correction in the clip-level or frame-level.
    SIG_CC_NODE_MODIFIED = QtCore.Signal(str, str, int) # clip_id, cc_id, node_index
    # Gets emitted whenever any particular color-correction node's attributes
    # are modified. Here again color-correction id could be of a
    # color-correction in the clip-level or frame-level.

    def __init__(self, logger):
        """
        Initialize ColorApi with a core API instance.
        """
        super().__init__()
        self.__delegate_mngr = DelegateMngr(logger)

    @property
    def delegate_mngr(self):
        return self.__delegate_mngr

    def set_ocio_colorspace(self, clip_id:str, colorspace:str) -> bool:
        """
        Set OCIO colorspace for given clip.

        Args:
            clip_id (str): Id of the clip
            colorspace (str): Name of the colorspace

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.set_ocio_colorspace, [clip_id, colorspace])

    def get_ocio_colorspace(self, clip_id:str) -> str:
        """
        Get OCIO colorspace for given clip.

        Args:
            clip_id (str): Id of the clip

        Returns:
            str : Name of of OCIO colorspace
        """
        return self.__delegate_mngr.call(
            self.get_ocio_colorspace, [clip_id])

    def set_ocio_display(self, display: str) -> bool:
        """
        Set current OCIO display.

        Args:
            display (str): Name of the display

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_ocio_display, [display])

    def get_ocio_display(self) -> str:
        """
        Get the current OCIO display.

        Returns:
            str : Name of the display
        """
        return self.__delegate_mngr.call(self.get_ocio_display)

    def set_ocio_view(self, view:str) -> bool:
        """
        Set current OCIO view.

        Args:
            view (str): Name of the view.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.set_ocio_view, [view])

    def get_ocio_view(self) -> str:
        """
        Get the current OCIO view.

        Returns:
            str : Name of the view
        """
        return self.__delegate_mngr.call(self.get_ocio_view)

    def set_channel(self, channel:int) -> bool:
        """
        Set the current color channel(s) to be shown. Following are the
        options available and the integer to be used to set them respectively,
        RED = 0
        GREEN = 1
        BLUE = 2
        ALPHA = 3
        RGB = 4
        LUMINANCE = 5

        Args:
            channel (int): Number to identify the channel(s) to set

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_channel, [channel])

    def get_channel(self) -> int:
        """
        Get the current color channel(s) to be shown. An integer denotining each of the
        respective color channel(s) will be returned. Following are the
        integers used to denote respective color channel(s).
        RED = 0
        GREEN = 1
        BLUE = 2
        ALPHA = 3
        RGB = 4
        LUMINANCE = 5

        Returns:
            int : Integeter denoting the current color channel.
        """
        return self.__delegate_mngr.call(self.get_channel)

    def set_fstop(self, value) -> bool:
        """
        Sets the global fstop color value.

        Args:
            value (float): fstop value

        Returns:
            (bool) : True if success False otherwise
        """
        self.__delegate_mngr.call(self.set_fstop, [value])

    def get_fstop(self) -> float:
        """
        Get the global fstop color value.

        Returns:
            float : the current fstop value set
        """
        return self.__delegate_mngr.call(self.get_fstop)

    def set_gamma(self, value) -> bool:
        """
        Sets the global gamma color value.

        Args:
            value (float): gamma value

        Returns:
            (bool) : True if success False otherwise
        """
        self.__delegate_mngr.call(self.set_gamma, [value])

    def get_gamma(self) -> float:
        """
        Get the global gamma color value.

        Returns:
            float : the current gamma value set
        """
        return self.__delegate_mngr.call(self.get_gamma)

    def get_cc_ids(self, clip_id:str, frame:Optional[int]=None) -> List[str]:
        """
        Returns the list of color correction ids for a specific clip or frame.

        Args:
            clip_id (str): Id of the clip whose ccs is needed.
            frame(int, optional):
                If frame number is given, retrieve the color correction ids in
                that particular frame, or return for the entire clip.

        Returns:
            list (str) : Ids of color corrections in that particular clip/frame.
        """
        return self.__delegate_mngr.call(self.get_cc_ids, [clip_id, frame])

    def move_cc(
        self, clip_id:str, from_index:int, to_index:int,
        frame:Optional[int]=None) -> bool:
        """
        Moves a color correction setting within the list
        by changing its position from one index to another.
        Args:
            clip_id (str): id of the clip.
            from_index (int) : Current index of the color correction.
            to_index (int): Target index to move the color correction.
            frame(int, optional): if frame move frame ccs, else move clip ccs.
        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.move_cc, [clip_id, from_index, to_index, frame])

    def append_ccs(
        self, clip_id:str, names:List[str], frame:Optional[int]=None,
        cc_ids:Optional[List[str]]=None) -> List[str]:
        """
        Creates color correction objects with the give names and optional ids.

        Args:
            clip_id (str): id of the clip.
            names (list): list of names of each color correction.
            frame (int, optional):
                Specific frame at which to apply the color corrections.
                If not provided, the ccs are applied to the entire clip.
            cc_ids (list(str), optional): list of color correction unique ids

        Returns:
            cc_ids (str): list of color correction ids appended.
        """
        return self.__delegate_mngr.call(
            self.append_ccs, [clip_id, names, frame, cc_ids])

    def delete_ccs(
        self, clip_id:str, cc_ids:List[str],
        frame:Optional[int]=None) -> bool:
        """
        Delete color corrections associated with the particular ids
        in the specified clip or frame.

        Args:
            clip_id (str): Id of a clip
            cc_ids(list) : List of color corrections to delete.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.delete_ccs, [clip_id, cc_ids, frame])

    def get_frame_of_cc(self, clip_id:str, cc_id:str) -> Optional[int]:
        """
        Get the frame of the given color correction.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.

        Returns:
            int : Frame of the given color-correction
        """
        return self.__delegate_mngr.call(self.get_frame_of_cc, [clip_id, cc_id])

    def get_nodes(
        self, clip_id:str, cc_id:str) \
        -> List[Union[ColorTimer, Grade]]:
        """
        Retrieves all nodes(colortimers and grade nodes) for the specified clip
        and color correction id.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.

        Returns:
            List[Union[ColorTimer, Grade]] :
                List of nodes in that particular cc id.
        """
        return self.__delegate_mngr.call(self.get_nodes, [clip_id, cc_id])

    def get_node_count(self, clip_id:str, cc_id:str):
        """
        Get the current number of nodes in the color-correction of the
        given id in the clip of the given id.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.

        Returns:
            int : Number of ndodes in the given color-correction
        """
        return self.__delegate_mngr.call(
            self.get_node_count, [clip_id, cc_id])

    def get_node(
        self, clip_id:str, cc_id:str, node_index:int) \
        -> Union[ColorTimer, Grade]:
        """
        Retrieve the node(colortimer or grade node) for the specified clip
        and color correction id and from the particular index.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.
            node_index (int): index of the node to retrieve.

        Returns:
            object : Colortimer or grade node object.
        """
        return self.__delegate_mngr.call(
            self.get_node, [clip_id, cc_id, node_index])

    def append_nodes(
        self, clip_id:str, cc_id:str,
        nodes:List[Union[ColorTimer, Grade]]) -> bool:
        """
        Appends multiple nodes(either a colortimer or grade node object) to the
        CC created for the specified clip and cc id.

        Args:
            clip_id (str): Id of the clip.
            cc_id (str):
                Id of color correction to which the node(s) are to be added.
            nodes (List[Union[ColorTimer, Grade]]):
                List of ColorTimer or Grade nodes to append.
        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.append_nodes, [clip_id, cc_id, nodes])

    def clear_nodes(self, clip_id:str, cc_id:str) -> bool:
        """
        Deletes all the nodes(Colortimer, Grade) in the color correction
        for the give clip and color correction ID.

        Args:
            clip_id (str): Id of a clip
            cc_id(str) : Id of Color-Correction

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.clear_nodes, [clip_id, cc_id])

    def delete_node(self, clip_id:str, cc_id:str, node_index:int) -> bool:
        """
        Delete the specific node in the given index in the color correction
        settings for the give clip and color correction ID.

        Args:
            clip_id (str): Id of a clip
            cc_id(str) : Id of Color-Correction
            node_index (int): Index of node to delete

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.delete_node, [clip_id, cc_id, node_index])

    def set_node_properties(
        self, clip_id:str, cc_id:str,
        node_index:int, properties:Dict) -> bool:
        """
        Sets the given node-properties of the node in the color
        correction for the give clip, color-correction and node-index.

        Args:
            clip_id (str): Id of the clip.
            cc_id (str): Unique id for the color correction.
            node_index (int) : Index of the node to update
            properties (dict):
                Key value pairs of the properties that need to be set.
                Example : {'offset' : [0.5, 0.3, 0.4], 'mute':True}

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.set_node_properties,
            [clip_id, cc_id, node_index, properties])

    def get_node_properties(
        self, clip_id:str, cc_id:str,
        node_index:int, property_names:List[str]) -> List:
        """
        For the provided node property name(s), gets the values of the
        node in the color correction for the give clip, color-correction
        and node-index.

        Args:
            clip_id (str): Id of the clip.
            cc_id (str): Unique id for the color correction.
            node_index (int) : Index of the node to update
            property_names (list):
                Name of the properties whose values need to be fetched.
                Example : ["offset", "gain"]

        Returns:
            List :
                Values of the given property names in the same order as
                how the property names were given.
        """
        return self.__delegate_mngr.call(
            self.get_node_properties,
            [clip_id, cc_id, node_index, property_names])

    def is_modified(self, clip_id:str, cc_id:str) -> bool:
        """
        Checks if color correction values of that particular id in the
        specified clip has been modified.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.

        Returns:
            bool : True if modified, False otherwise.
        """
        return self.__delegate_mngr.call(self.is_modified, [clip_id, cc_id])

    def set_name(self, clip_id:str, cc_id:str, name:str) -> bool:
        """
        Update the name of the color correction setting.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.
            name (str): name to update to.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_name, [clip_id, cc_id, name])

    def get_name(self, clip_id:str, cc_id:str) -> str:
        """
        Retrieves the name of the color correction in the
        specified clip and cc id.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.

        Returns:
            str: name of the color correction.
        """
        return self.__delegate_mngr.call(self.get_name, [clip_id, cc_id])

    def create_region(self, clip_id:str, cc_id:str) -> bool:
        """
        Create a mask/region to the specified clip and color correction.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.
        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.create_region, [clip_id, cc_id])

    def has_region(self, clip_id:str, cc_id:str) -> bool:
        """
        Check if a particular region exists within the specified clip
        and color correction(id).

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.

        Returns:
            bool: True if region exists, False otherwise.
        """
        return self.__delegate_mngr.call(self.has_region, [clip_id, cc_id])

    def append_shape_to_region(
        self, clip_id:str, cc_id:str, points:List[Tuple[float]]) -> bool:
        """
        Appends a shape to the region in the specified clip
        and color correction ID.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.
            points (list) : list of (x, y) points representing any shape.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.append_shape_to_region, [clip_id, cc_id, points])

    def delete_region(self, clip_id:str, cc_id:str) -> bool:
        """
        Delete a mask/region in the specified clip and color correction.

        Args:
            clip_id (str): Id of the clip.
            cc_id (str): Unique id for the color correction.
        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.delete_region, [clip_id, cc_id])

    def set_region_falloff(self, clip_id:str, cc_id:str, falloff:float)->bool:
        """
        Sets the falloff value associated with the region in a
        particular clip and color correction.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.
            falloff (float): falloff value

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_region_falloff, [clip_id, cc_id, falloff])

    def get_region_falloff(self, clip_id:str, cc_id:str) -> float:
        """
        Retrieves the falloff value associated with the region in a
        particular clip and color correction.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.

        Returns:
            float : falloff value
        """
        return self.__delegate_mngr.call(self.get_region_falloff, [clip_id, cc_id])

    def mute(self, clip_id:str, cc_id:str, value:bool) -> bool:
        """
        Sets mute value all color correction values in the specified
        clip associated with the specified color correction ID.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.
            value (bool): True to mute the color correction, False otherwise.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.mute, [clip_id, cc_id, value])

    def is_mute(self, clip_id:str, cc_id:str) -> bool:
        """
        Checks if color correction values of that particular id in the
        specified clip has been muted.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.

        Returns:
            bool : True if muted, False otherwise.
        """
        return self.__delegate_mngr.call(self.is_mute, [clip_id, cc_id])

    def mute_all(self, clip_id:str, value:bool) -> bool:
        """
        Sets mute value all color correction values in the specified
        clip associated with the specified color correction ID.

        Args:
            clip_id (str): id of the clip.
            value (bool): True to mute all the color corrections,
                          False otherwise.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.mute_all, [clip_id, value])

    def is_mute_all(self, clip_id:str) -> bool:
        """
        Checks if all color correction values in the specified
        clip has been muted.

        Args:
            clip_id (str): id of the clip.

        Returns:
            bool : True if muted, False otherwise.
        """
        return self.__delegate_mngr.call(self.is_mute_all, [clip_id])

    def set_read_only(self, clip_id:str, cc_id:str, value:bool) -> bool:
        """
        Set if the color correction values of that particular id should be
        read-only or read-write.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.
            value (bool) : True if success False otherwise

        Returns:
            bool : True if set, False otherwise.
        """
        return self.__delegate_mngr.call(self.set_read_only, [clip_id, cc_id, value])

    def is_read_only(self, clip_id:str, cc_id:str) -> bool:
        """
        Checks if color correction values of that particular id in
        the specified clip is read_only.

        Args:
            clip_id (str): id of the clip.
            cc_id (str): Unique id for the color correction.

        Returns:
            bool : True if read only, False otherwise.
        """
        return self.__delegate_mngr.call(self.is_read_only, [clip_id, cc_id])

    def get_rw_frames(self, clip_id:str) -> List[int]:
        """
        Retrieves the frames that contain read-write color corrections within
        a specified clip.

        Args:
            clip_id (str): id of the clip.

        Returns:
            List[int]: list of frame numbers
        """
        return self.__delegate_mngr.call(self.get_rw_frames, [clip_id])

    def get_ro_frames(self, clip_id:str) -> List[int]:
        """
        Retrieves the frames that contain read-only color corrections within
        a specified clip.

        Args:
            clip_id (str): id of the clip.

        Returns:
            List[int]: list of frame numbers
        """
        return self.__delegate_mngr.call(self.get_ro_frames, [clip_id])

    def set_ro_ccs(self, ccs:dict) -> bool:
        """
        Removes all existing read only color corrections in the given clips and
        replaces them with the given ccs. If Frame number is None, then the
        color-correction will be added as a clip-level color-correction.

        Here is an example of how the ccs dict should look like,

        .. code-block:: python

            {
                clip_id_1 : [
                    (None, color_correction),
                    (frame_1, color_correction),
                    (None, color_correction),
                    (frame_5, color_correction),
                    (frame_10, color_correction)
                ]
            }

        Args:
            ccs (dict):
                Color correction that need to be set for the given clips and
                their respective frames.

        Returns:
            bool : True if sucess, False otherwise.
        """
        return self.__delegate_mngr.call(self.set_ro_ccs, [ccs])

    def get_ro_ccs(
        self, clip_id:str, frame:Optional[int]=None)->List[ColorCorrection]:
        """
        Get the list of read-only color-corrctions that are present in the
        given clips on the given frames. If frame number is not given, then\
        then the clip-level color-corrections are returned.

        Args:
            clip_id(str): Id of the clip
            frame(Optional[int]):
                Frame of the clip. If None is give, clip level
                cc will be returned.

        Returns:
            List[RPA ColorCorrection]: RPA Color Correction Object.
        """
        return self.__delegate_mngr.call(self.get_ro_ccs, [clip_id, frame])

    def set_rw_ccs(self, ccs:dict) -> bool:
        """
        Removes all existing read write color corrections in the given clips
        and replaces them with the given ccs. If Frame number is None, then
        the color-correction will be added as a clip-level color-correction.

        Here is an example of how the ccs dict should look like,

        .. code-block:: python

            {
                clip_id_1 : [
                    (None, color_correction),
                    (frame_1, color_correction),
                    (None, color_correction),
                    (frame_5, color_correction),
                    (frame_10, color_correction)
                ]
            }

        Args:
            ccs (dict):
                Color correction that need to be set for the given clips and
                their respective frames.

        Returns:
            bool : True if sucess, False otherwise.
        """
        return self.__delegate_mngr.call(self.set_rw_ccs, [ccs])

    def get_rw_ccs(
        self, clip_id:str, frame:Optional[int]=None)->List[ColorCorrection]:
        """
        Get the list of read-only color-corrctions that are present in the
        given clips on the given frames. If frame number is not given, then\
        then the clip-level color-corrections are returned.

        Args:
            clip_id(str): Id of the clip
            frame(Optional[int]):
                Frame of the clip. If None is give, clip level
                cc will be returned.

        Returns:
            List[RPA ColorCorrection]: RPA Color Correction Object.
        """
        return self.__delegate_mngr.call(self.get_rw_ccs, [clip_id, frame])

    def delete_ro_ccs(self, clips) -> bool:
        """
        Deletes all existing read only color corrections in the given clips.

        Args:
            clips (list): List of clip ids to delete ro_ccs from.

        Returns:
            bool : True if sucess, False otherwise.
        """
        return self.__delegate_mngr.call(self.delete_ro_ccs, [clips])
