"""Color corrector module."""
from review_plugin_api.api._delegate_mngr import DelegateMngr


class ColorCorrectorApi:
    """
    A class that provides an interface for color correction operations.
    """

    def __init__(self):
        """
        Initialize ColorCorrectorApi with a core API instance.
        """
        self.__delegate_mngr = DelegateMngr()

    def get_delegate_mngr(self):
        return self.__delegate_mngr

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
        return self.__delegate_mngr.call(
            self.get_clip_cc, [frame])

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
        return self.__delegate_mngr.call(
            self.set_clip_cc, [frame, cc])

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
        return self.__delegate_mngr.call(
            self.get_frame_cc, [frame])

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
        return self.__delegate_mngr.call(
            self.set_frame_cc, [frame, cc])

    def create_region_cc(self, frame):
        """
        Create a new region color correction for a specific frame.

        Args:
            frame: The frame for which a region color correction is created.

        Returns:
            GUID of the newly created region color correction.
        """
        return self.__delegate_mngr.call(
            self.create_region_cc, [frame])

    def delete_region_cc(self, frame, cc_guid):
        """
        Delete a region color correction from a specific frame using its GUID.

        Args:
            frame: The frame for which the region color correction is deleted.
            cc_guid: GUID of the region color correction to be deleted.
        """
        return self.__delegate_mngr.call(
            self.delete_region_cc, [frame, cc_guid])

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
        return self.__delegate_mngr.call(
            self.get_region_cc, [frame, cc_guid])

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
        return self.__delegate_mngr.call(
            self.set_region_cc, [frame, cc_guid, cc])

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
        return self.__delegate_mngr.call(
            self.get_region_ccs, [frame])

    def reorder_region_ccs(self, frame, cc_guids):
        """
        Reorder region color corrections at a specific frame based on the provided GUIDs.

        Args:
            frame: The frame in which region color corrections are reordered.
            cc_guids: List of region color correction GUIDs specifying the new order.
        """
        return self.__delegate_mngr.call(
            self.reorder_region_ccs, [frame, cc_guids])

    def create_shape(self, frame, cc_guid):
        """
        Create a shape for a region color correction at a specific frame.

        Args:
            frame: The frame for which the shape is created.
            cc_guid: GUID of the region color correction.

        Returns:
            GUID of the newly created shape.
        """
        return self.__delegate_mngr.call(
            self.create_shape, [frame, cc_guid])

    def set_drawing_in_progress(self, value:bool):
        return self.__delegate_mngr.call(
            self.set_drawing_in_progress, [value])

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
        return self.__delegate_mngr.call(
            self.append_point_to_shape, [frame, cc_guid, shape_guid, x, y])

    def append_points_to_shape(self, frame, cc_guid, shape_guid, points):
        """
        Append a list of points to a specific shape for a region color correction.

        Args:
            frame: The frame containing the region color correction.
            cc_guid: GUID of the region color correction.
            shape_guid: GUID of the shape to which the point is appended.
            points: list of XY-coordinates of the point (in the screen space)
        """
        return self.__delegate_mngr.call(
            self.append_points_to_shape, [frame, cc_guid, shape_guid, points])
