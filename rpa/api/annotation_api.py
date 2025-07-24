"""
Annotation API
==============

Manage clip annotations which include Strokes and Texts.

Annotations can only be set on the particular Frame of a Clip.

Annotations can either be read-write or read-only.

A Frame of a clip can have multiple Read-Write Annotations and it can
have only 1 Read-Only Annotation.
"""

try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore
from rpa.delegate_mngr import DelegateMngr
from rpa.session_state.annotations import \
    StrokePoint, Stroke, Text, Annotation
from rpa.session_state.utils import Color, Point
from typing import List, Dict


class AnnotationApi(QtCore.QObject):
    SIG_MODIFIED = QtCore.Signal()
    # Gets emitted whenever annotations(strokes/texts) are added or removed.

    def __init__(self, logger):
        super().__init__()
        self.__delegate_mngr = DelegateMngr(logger)

    @property
    def delegate_mngr(self)-> DelegateMngr:
        return self.__delegate_mngr

    def append_transient_point(
        self, clip_id:str, frame:int,
        token:str, stroke_point:StrokePoint, is_line:bool=False)->bool:
        """
        This methods adds a transient point(temporary point for drawing)
        to a specified frame in a clip. These points are used to build or
        update a stroke during the drawing process. If the token already
        exists, the point is appended to the stroke
        associated with that token.

        Args:
            clip_id (str):
                Id of a clip where the transient point will be added.
            frame (int): frame number where the point should be added.
            token (str):
                A unique identifier that associates the transient point
                with a specified drawing stroke.
            stroke_point (StrokePoint):
                RPA StrokePoint that needs to be appended to the transient
                stroke that is created by means of appending transient points.
            is_line (bool):
                If the is_line flag is True, the trasient stroke is a line,
                only 2 points at most will be kept.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call( self.append_transient_point,
            [clip_id, frame, token, stroke_point, is_line])

    def get_transient_stroke(self, clip_id:str, frame:int, token:str):
        """
        Retrieves all transient points associated with a specific stroke in
        a given clip and frame.

        Args:
            clip_id (str): Id of a clip where the transient stroke exists.
            frame (int): Frame number where the stroke is located.
            token (str):
                A unique identifier associated with the stroke
                that needs to be retrieved.

        Returns:
            Stroke :
                The RPA Stroke that is created by means of appending
                transient stroke-points.
        """
        return self.__delegate_mngr.call(self.get_transient_stroke,
            [clip_id, frame, token])

    def delete_transient_points(self, clip_id:str, frame:int, token:str)->bool:
        """
        Removes all transient points associated with a specific RPA Stroke in
        a given clip and frame.

        Args:
            clip_id (str):
                Id of a clip where the transient points should be deleted.
            frame (int): Frame number where the points should be deleted.
            token (str):
                The unique identifier associated with the stroke
                whose points are to be deleted.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.delete_transient_points, [clip_id, frame, token])

    def append_strokes(
        self, clip_id:str, frame:int, strokes:List[Stroke])-> bool:
        """
        This method adds new strokes to a specified clip and frame.

        Args:
            clip_id (str): Id of a clip.
            frame (int): Frame number.
            strokes (list[Stroke]) :
                List of RPA Stroke objects to add to the frame.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.append_strokes,
            [clip_id, frame, strokes])

    def set_text(
        self, clip_id:str, frame:int, text:Text)->bool:
        """
        Based on the text properties defined in the text object
        set the text as an annotation.

        If a text-annotation already exists at the same position as the
        position in given text object, then that existing text annotation's
        text and properties will be updated with the text and properties of
        the the given text-object.

        Args:
            clip_id (str): Id of a clip.
            frame (int): Frame number.
            text (Text) : RPA Text object

        Returns:
            (bool): True if success else False
        """
        return self.__delegate_mngr.call(self.set_text, [clip_id, frame, text])

    def append_texts(self, clip_id:str, frame:int, texts:List[Text])->bool:
        """
        This method adds new text annotations to the specified clip and frame.

        Args:
            clip_id (str): Id of a clip.
            frame (int): Frame number.
            texts (list[Text]) : List of RPA Text objects to add to the frame.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.append_texts, [clip_id, frame, texts])


    def set_ro_annotations(self, annotations:Dict)-> bool:
        """
        Set the list of read-only annotaitons that need to be set for the
        clips and their respective frames as mentioned in the given dict.

        Following is an example of how the annotations dict should look like,

        .. code-block:: python

            annotations = {
                "clip_id_1": {
                    frame_1: [Annotation(), Annotation(), Annotation()]
                    frame_2: [Annotation(), Annotation(), Annotation()]
                    frame_3: [Annotation(), Annotation()]
                },
                "clip_id_2": {
                    frame_1: [Annotation(), Annotation(), Annotation()]
                    frame_2: [Annotation(), Annotation(), Annotation()]
                    frame_3: [Annotation(), Annotation()]
                }
            }

        Args:
            annotations (Dict): Dictionary of annotations

        Returns: (bool) : True if success False otherwise.
        """
        return self.__delegate_mngr.call(self.set_ro_annotations, [annotations])

    def get_ro_annotations(self, clip_id:str, frame:int)-> List[Annotation]:
        """
        Retrieves the list of read-only annotations for the
        specified clip and frame.

        Args:
            clip_id (str): Id of a clip.
            frame (int): Clip frame number

        Returns:
            (list) : Read-only Annotations(strokes and texts) objects.
        """
        return self.__delegate_mngr.call(self.get_ro_annotations, [clip_id, frame])

    def delete_ro_annotations(self, clips:list)->bool:
        """
        This method deletes the read-only annotations from given clips.

        Args:
            clips (list):list of clip ids.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.delete_ro_annotations, [clips])

    def get_ro_frames(self, clip_id:str)->List[int]:
        """
        Retrieves the frames that contain read-only annotations within
        a specified clip. These are frames where annotations cannot be modified
        or erased and are used for viewing only.

        Args:
            clip_id (str): Id of a clip.

        Returns:
            list[int] :
                A list of frame numbers that contain read-only annotations.
        """
        return self.__delegate_mngr.call(self.get_ro_frames, [clip_id])

    def set_rw_annotations(self, annotations:Dict)-> bool:
        """
        Sets the read-write annotations for the clips and their respective frames as
        given in the dictionary.

        Here is an example of how the annotations dict should look like,

        .. code-block:: python

            {
                "clip_id_1": {
                    frame_1: Annotation()
                    frame_2: Annotation()
                    frame_3: Annotation()
                },
                "clip_id_2": {
                    frame_1: Annotation()
                    frame_2: Annotation()
                    frame_3: Annotation()
                }
            }

        Args:
            annotatoins(Dict) : Annotaions that need to be set on clips and
            their respective frames.

        Returns:
            (bool): True is success else False
        """
        return self.__delegate_mngr.call(self.set_rw_annotations, [annotations])

    def get_rw_annotation(self, clip_id:str, frame:int)-> Annotation:
        """
        Retrieves the read-write annotations for a specified clip and frame.

        Args:
            clip_id (str): Id of a clip.
            frame (int): frame number.

        Returns:
            Annotation(RPA Annotation):
                RPA Annotation(strokes and texts) object.
        """
        return self.__delegate_mngr.call(self.get_rw_annotation, [clip_id, frame])

    def delete_rw_annotation(self, clip_id:str, frame:int)->bool:
        """
        This method deletes the read-write annotation from a specified clip and frame.
        Unlike clear, delete doesn't bring back the annotation on undo.

        Args:
            clip_id (str): Id of a clip.
            frame (int): Frame number.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.delete_rw_annotation, [clip_id, frame])

    def get_rw_frames(self, clip_id:str)->List[int]:
        """
        Retrieves the frames that contain read-write annotations within
        a specified clip. There are frames where annotations can be modified
        or erased.

        Args:
            clip_id (str): Id of a clip.

        Returns:
            list : A list of frame numbers that contain read-write annotations.
        """
        return self.__delegate_mngr.call(self.get_rw_frames, [clip_id])

    def clear_frame(self, clip_id:str, frame:int)-> bool:
        """
        This method clears all annotations in a specified clip and frame.
        This differs from delete, when you do undo/redo, this still brings
        back the cleared annotations, but delete will not.

        Args:
            clip_id (str): Id of a clip.
            frame (int): Frame number where annotations should be cleared.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.clear_frame, [clip_id, frame])

    def undo(self, clip_id:str, frame:int)-> bool:
        """
        Reverts the most recent annotation change in the specified
        clip and frame.

        Args:
            clip_id (str): Id of a clip.
            frame (int): Frame number.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.undo, [clip_id, frame])

    def redo(self, clip_id:str, frame:int)-> bool:
        """
        This method reapplies the most recent undone annotation change
        in the specified clip and frame.

        Args:
            clip_id (str): Id of a clip.
            frame (int): Frame number.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.redo, [clip_id, frame])

    def set_laser_pointer(self, id:str, point:Point, color:Color)-> bool:
        """
        This method sets a laser pointer on the specified clip and frame.

        Args:
            id (str): Id of the laser pointer.
            point (Point):
                RPA Point object holding the normalized (0.0 to 1.0) position
                where the laser pointer should be placed.
            color (Color):
                The RPA Color objectfor the laset pointer.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_laser_pointer, [id, point, color])

    def set_pointer(self, stroke_point:StrokePoint)-> bool:
        """
        This method sets a pen pointer on the specified clip and frame.

        Args:
            stroke_point (StrokePoint) :
                The RPA StrokePoint that needs to be used to draw the pointer.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_pointer, [stroke_point])
