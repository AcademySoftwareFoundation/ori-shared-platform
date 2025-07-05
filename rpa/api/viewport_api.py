"""
Viewport API
============

Manage viewport transforms and overlays.
"""

try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore
from typing import List, Optional, Tuple, Dict
from rpa.delegate_mngr import DelegateMngr
from rpa.session_state.utils import Point


class ViewportApi(QtCore.QObject):
    SIG_CURRENT_CLIP_GEOMETRY_CHANGED = QtCore.Signal(object) # geometry

    def __init__(self, logger):
        super().__init__()
        self.__delegate_mngr = DelegateMngr(logger)

    @property
    def delegate_mngr(self):
        return self.__delegate_mngr

    def create_html_overlay(self, html_overlay:Dict)->str:
        """
        Create a floating HTML based overlay on the viewport.
        The data required to create the HTML overlay needs to be passed in
        as a dictionary. Following is an example dict with all the key-value
        pairs that are expected.

        .. code-block:: python

            html_overaly = {
                "html": "<span style='color: white; font-size:42px'>Hello RPA!</span>",
                "x": 0.5,
                "y": 0.5,
                "width": 500,
                "height": 200,
                "is_visible": True
            }

        "html" value need to be the string value that needs to be overlayed on
        the viewport.

        "x" and "y" values need to passed as normalized 0.0 to 1.0 values.
        With (0.0, 0.0) at the lower-left and (1.0, 1.0) at the upper-right.

        "width" and "height" need to be pixel values.

        "is_visible" acccepts a boolean based on which the visibility of the HTML
        overlay can be controller.

        Args:
            html_overaly (Dict): Data required to create HTML overlay.

        Returns:
            (str): Unique id of the created HTML overlay.
        """
        return self.__delegate_mngr.call(
            self.create_html_overlay, [html_overlay])

    def set_html_overlay(self, id:str, html_overlay:Dict):
        """
        Set the properties of existing HTML overlays. The properties can be
        set by passing a dict with the key-value pairs of the properties that
        need to be chagned.

        The passed in the dict should have one or more of the following example
        dictionary,

        .. code-block:: python

            html_overaly = {
                "html": "<span style='color: white; font-size:42px'>Hello RPA!</span>",
                "x": 0.5,
                "y": 0.5,
                "width": 500,
                "height": 200,
                "is_visible": True
            }

        "html" value needs to be the string value that needs to be overlayed on
        the viewport.

        "x" and "y" values need to passed as normalized 0.0 to 1.0 values.
        With (0.0, 0.0) at the lower-left and (1.0, 1.0) at the upper-right.

        "width" and "height" need to be pixel values.

        "is_visible" acccepts a boolean based on which the visibility of the HTML
        overlay can be controller.

        Args:
            id (str):
                Unique id of the HTML overaly whose properties need to be set

            html_overlay (dict):
                Data containing HTML overlay properties to set.

        Returns:
            (bool): True if success else False
        """
        return self.__delegate_mngr.call(
            self.set_html_overlay, [id, html_overlay])

    def get_html_overlay_ids(self)->List[str]:
        """
        Returns unique ids of all the HTML overlays currently present in the
        session.

        Returns:
            (List[str]): List of HTML overlay ids
        """
        return self.__delegate_mngr.call(self.get_html_overlay_ids)

    def get_html_overlay(self, id:str)->Dict:
        """
        Returns the data of the HTML overlay whose id has been provided.
        Following is an example of how the returned dict will look like,

        .. code-block:: python

            {
                "html": "<span style='color: white; font-size:42px'>Hello RPA!</span>",
                "x": 0.5,
                "y": 0.5,
                "width": 500,
                "height": 200,
                "is_visible": True
            }

        Args:
            id (str): Unique id of a HTML overlay

        Returns:
            (Dict): Data of the HTML overlay.
        """
        return self.__delegate_mngr.call(self.get_html_overlay, [id])

    def delete_html_overlays(self, ids:List[str]):
        """
        Delets the HTML overlays whose ids have been provided.

        Args:
            ids (List[str]): Ids of HTML overlays.


        Returns:
            (bool): True if success False otherwise.
        """
        return self.__delegate_mngr.call(self.delete_html_overlays, [ids])

    def set_mask(self, mask:Optional[str])->bool:
        """
        Set a layer of mask on top of the current view

        Args:
            mask (Optional[str]):
                A mask can either be an image path or a recipe to render.
                A mask with image path will be rendered with its respective
                image coordinates matching the viewing media width and height.
                A mask recipe is defined with a desired aspect ratio and opacity.
                The recipe format is as follows: "$aspect_ratio@$opacity"
                There can be multiple recipes for a particular mask.
                In these instances, "&" can be used to denote the recipe list.
                Examples:
                    "/some/path/to/mask/images/mask_example.tif"
                    "2.35@0.5"
                    "1.755@1.0&1.655@0.7"
                The mask will be rendered on top of the current view.
                When None, any existing rendered mask will be removed.
        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_mask, [mask])

    def start_drag(self, pointer:Tuple[float, float])->bool:
        """
        Sets the starting reference pointer position for translation by
        drag operation. After this method, use drag method to drag and
        use finally end_drag to complete the drag operation.

        Args:
            pointer (Tuple[float, float]):
                Screen space (x,y) coordinate defining the start position
                of drag operation for translation.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.start_drag, [pointer])

    def drag(self, pointer:Tuple[float, float])->bool:
        """
        Performs translation based on the given pointer position while
        in drag operation. start_drag method needs to be called before calling
        this method. And end_drag method needs to be called after the drag
        operation is completed.

        Args:
            pointer (Tuple[float, float]):
                Screen space (x,y) coordinate defining the current position
                while in drag operation for translation.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.drag, [pointer])

    def end_drag(self)->bool:
        """
        Ends translation by drag operation, and resets the reference
        pointer position.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.end_drag)

    def scale_on_point(
        self, scale_point:Tuple[float, float], delta:float, speed:float,
        vertical_lock:bool, horizontal_lock:bool)->bool:
        """
        Allow scale in/out at a specific point. Possible to lock the view from
        scaling vertically or horizontally.

        Args:
            scale_point(Tuple[float, float]):
                Screen space (x,y) coordinate position to scale in/out
            delta (float):
                1.0 for scale in operation, and -1.0 for scale out operation
            speed (float):
                Speed at which scale operation occurs, value set by
                some user input
            vertical_lock (bool):
                View locked from scaling vertically when True
            horizontal_lock (bool):
                View locked from scaling horizontally when True
        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.scale_on_point,
            [scale_point, delta, speed, vertical_lock, horizontal_lock])

    def set_scale(
        self, horizontal:float, vertical:Optional[float]=None)->bool:
        """
        Set the horizontal and/or vertical factor to scale in/out of viewport

        Args:
            horizontal (float): Horizontal scale factor
            vertical (float):
                Vertical scale factor. When None, it will
                be the same value as Horizontal scale factor.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.set_scale, [horizontal, vertical])

    def get_scale(self)-> List[float]:
        """
        Get the horizontal and vertical scale values of viewport.

        Returns:
            List[float, float]]: Horizontal and Version scale values
        """
        return self.__delegate_mngr.call(self.get_scale)

    def set_translation(
        self, horizontal:float, vertical:float)->bool:
        """
        Set the horizontal and/or vertical factor to translation in/out of viewport

        Args:
            horizontal (float): Horizontal translation factor
            vertical (float): Vertical translation factor.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.set_translation, [horizontal, vertical])

    def get_translation(self)-> List[float]:
        """
        Get the horizontal and vertical translation values of viewport.

        Returns:
            List[float, float]]: Horizontal and Version translation values
        """
        return self.__delegate_mngr.call(self.get_translation)

    def flip_x(self, state:bool)->bool:
        """
        Flip the current view horizontally or default to original view,
        given the state.

        Args:
            state (bool): flip display view horizontally when True

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.flip_x, [state])

    def flip_y(self, state:bool)->bool:
        """
        Flip the current view vertically or default to original view,
        given the state.

        Args:
            state (bool): flip display view vertically when True

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.flip_y, [state])

    def fit_to_window(self, state:bool)->bool:
        """
        Fit the current media to the width and height of viewing window space

        Args:
            state (bool): Enable fitting to window when True

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.fit_to_window, [state])

    def fit_to_width(self, state:bool)->bool:
        """
        Fit the current media to the width of viewing window space

        Args:
            state (bool): Enable fit to width when True

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.fit_to_width, [state])

    def fit_to_height(self, state:bool)->bool:
        """
        Fit the current media to the height of viewing window space

        Args:
            state (bool): Enable fit to height when True

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.fit_to_height, [state])

    def display_msg(self, message:str, duration:float=2.0)->bool:
        """
        Display the given message on the viewport for the given duration.
        The messages may indicate current status, or other user actions.
        The displayed message will disappear after the given duration has passed.
        The duration is in the unit of seconds.

        Args:
            message (str): The message to be displayed on the viewport
            duration (float): The amount of time to display the message in seconds.
                              When not given, it defaults to 2.0 seconds.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.display_msg, [message, duration])

    def get_current_clip_geometry(self)-> Optional[List[Tuple[float, float]]]:
        """
        Returns a list of (x,y) image corners for the current clip
        in the viewport.

        Returns:
            Optional[List[Tuple[float, float]]]:
                None if there is no current clip otherwise returns a list of
                the image corners of the current clip.
        """
        return self.__delegate_mngr.call(self.get_current_clip_geometry)

    def is_feedback_visible(self, category:int)-> bool:
        """
        This method checks whether annotations and ccs(given the category) in the current session across
        all clips and their corresponding frames are allowed
        to be visible or not.
        Category is defined as follows
        1 - All
        2 - Strokes
        3 - Texts
        4 - Clip CCs
        5 - Frame CCs
        6 - Region CCs

        Args:
            category(int): Integer that represents the category.
        Returns:
            bool : True if annotations and ccs are visible, else False.
        """
        return self.__delegate_mngr.call(self.is_feedback_visible, [category])

    def set_feedback_visibility(self, category:int, value:bool)-> bool:
        """
        Enable users to set visibility of all annotations and ccs in the current session.
        Category is as follows.
        1 - All
        2 - Strokes
        3 - Texts
        4 - Clip CCs
        5 - Frame CCs
        6 - Region CCs
        Args:
            category (int) : Integer that represents the category that needs to be set.
            value (bool) : Flag to set visibility of all annotaions and ccs.

        Returns:
            (bool) : True if success False otherwise
        """
        self.__delegate_mngr.call(self.set_feedback_visibility, [category, value])

    def set_text_cursor(self, position:Point, size:int)-> bool:
        """
        Draw a text-cursor line on the viewport.

        Args:
            position (RPA Point): Position of the cursor
            size(int): Size of the cursor

        Returns:
            (bool): True if success else False
        """
        return self.__delegate_mngr.call(
            self.set_text_cursor, [position, size])

    def is_text_cursor_set(self)-> bool:
        """
        Check if text-cursor is set on viewport.

        Returns:
            (bool): Returns True if text-cursor is set on viewport.
        """
        return self.__delegate_mngr.call(self.is_text_cursor_set)

    def unset_text_cursor(self)-> bool:
        """
        Remove text cursor from viewport.

        Args:
            position (RPA Point): Position of the cursor
            size(int): Size of the cursor

        Returns:
            (bool): True if success else False
        """
        return self.__delegate_mngr.call(self.unset_text_cursor)

    def set_cross_hair_cursor(self, position:Point)-> bool:
        """
        Draw a cross_hair-cursor line on the viewport.

        Args:
            position (RPA Point): Position of the cursor

        Returns:
            (bool): True if success else False
        """
        return self.__delegate_mngr.call(
            self.set_cross_hair_cursor, [position])
