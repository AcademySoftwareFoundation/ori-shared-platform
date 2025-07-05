"""
Session API
===========

Manage Playlists, Clips and Clip-Attributes.

The Session API works with Ids to manipulate respective Playlists, Clips and
Attrs.
"""

try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore
from typing import List, Optional, Tuple, Union, Any
from rpa.delegate_mngr import DelegateMngr
import uuid


class SessionApi(QtCore.QObject):
    SIG_PLAYLISTS_MODIFIED = QtCore.Signal()
    # Gets emitted whenever the playlist list in the session is modified.
    # This could happend when existing playlists are deleted, permanently
    # deleted, new playlist is created and when any of the existing playlists
    # are moved.
    SIG_PLAYLIST_MODIFIED = QtCore.Signal(str) # playlist_id
    # Gets emitted whenever the clips under a respective playlist is modified.
    # This could happend when existing clips are permantly deleted or when new
    # clips are created and when existing clips are moved.
    SIG_FG_PLAYLIST_CHANGED = QtCore.Signal(str) # playlist_id
    # Gets emitted when the Fore-Ground playlist, which is always the current
    # playlist is changed. This could happen, when the user changes it, or
    # even when the existing FG playlist is deleted and a new FG playlist is
    # automatically assigned.
    SIG_BG_PLAYLIST_CHANGED = QtCore.Signal(object) # playlist_id/None
    # Gets emitted when the BG playlist is changed. This could happen when the
    # user changes the BG playlist, when the BG playlist is removed or
    # deleted.
    SIG_CURRENT_CLIP_CHANGED = QtCore.Signal(object) # clip_id/None
    # Gets emitted when the current clip that is shown in the viewport
    # changes. This could happen when the user changes the current clip or the
    # current clip is deleted and a new current clip is automatically assigned.
    SIG_ATTR_VALUES_CHANGED = QtCore.Signal(list)
    # Gets emitted whenever one or more attr values of a clip are changed.
    # Example of how the attr values will be carried by this signal,
    # [(playlist_id, clip_id, attr_id, value),
    #  (playlist_id, clip_id, attr_id, value)]
    SIG_ACTIVE_CLIPS_CHANGED = QtCore.Signal(str) # playlist_id
    # Gets emitted whenever the list of active clips are changed
    # for a particular playlist.

    def __init__(self, logger):
        super().__init__()
        self.__delegate_mngr = DelegateMngr(logger)

    @property
    def delegate_mngr(self):
        return self.__delegate_mngr

    def clear(self)->bool:
        """
        Clear the session by permanently deleting all the Playlists and their
        corresponding clips in the entire Session tree.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.clear)

    ###########################################################################
    # Playlist Methods                                                        #
    ###########################################################################

    def get_playlists(self)->List[str]:
        """
        Returns ids of all playlist in the session.

        Returns:
            list[str]: Ids of playlists.
        """
        return self.__delegate_mngr.call(self.get_playlists)

    def get_playlist_name(self, id:str)->str:
        """
        Returns name of the playlist whose id is provided.

        Args:
            id (str): Id of Playlist

        Returns:
            str : Name of Playlist
        """
        return self.__delegate_mngr.call(self.get_playlist_name, [id])

    def set_fg_playlist(self, id:str)->bool:
        """
        Set the playlist with the given id to be the Fore-Ground(FG) playlist.

        Args:
            id (str): Id of playlist

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_fg_playlist, [id])

    def get_fg_playlist(self)->str:
        """
        Return the id of the Fore-Ground(FG) playlist. Note that a Session
        will always have a FG playlist.

        Returns:
            str : Id of the playlist to set as Fore-Ground.
        """
        return self.__delegate_mngr.call(self.get_fg_playlist)

    def set_bg_playlist(self, id:str)->bool:
        """
        Set the playlist with given id to be the Back-Ground(BG) playlist.

        Args:
            id (str): Id of Playlist to set as Back-Ground.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_bg_playlist, [id])

    def get_bg_playlist(self)->Optional[str]:
        """
        Returns the id of the Back-Ground(BG) playlist. If there is no BG
        playlist currently, then None is returned.

        Returns:
            Optional[str] : Optional id of Back-Ground playlist.
        """
        return self.__delegate_mngr.call(self.get_bg_playlist)

    def delete_playlists_permanently(self, ids:List[str])->bool:
        """
        Playlists with the given respective ids, will be permanently deleted
        along with the clips they hold. Permanently deleted playlists cannot
        be restored.

        Args:
            Ids (List[str]): Ids of Playlists.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.delete_playlists_permanently, [ids])

    def delete_playlists(self, ids:List[str])->bool:
        """
        Playlists with the given respective ids will be temporarily deleted
        along with the clips they hold. Note that this method will only
        temporarily delete the playlists, these temporarily deleted playlists
        can be restored.

        Args:
            Ids (List[str]): Ids of Playlists.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(self.delete_playlists, [ids])

    def get_deleted_playlists(self)->List[str]:
        """
        Returns ids of all the playlists that have been deleted temporarily.

        Returns:
            List[str]: Ids of all temporarily deleted playlists.
        """
        return self.__delegate_mngr.call(self.get_deleted_playlists)

    def restore_playlists(self, ids, index=None)->bool:
        """
        Restores playlists with the given ids that were previouly deleted
        back into the session. If index is provided the playlists
        will be restored into it otherwise will restore playlists to the end
        of the playlist.

        Args:
            ids (List[str]): Ids of playlists to restore from being deleted.

        Kwargs:
            index (Optional[str]):
                Optioanl position index where the playlists need to be restored to.

        Returns:
            (bool) : True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.restore_playlists, [ids, index])

    def create_playlists(
        self, names:List[str], index:Optional[int]=None,
        ids:Optional[List[str]]=None)->List[str]:
        """
        Creates new playlists with the given names. If index is provided, the
        new playlists will be inserted into it, otherwise they will be
        inserted at the end. If unique ids are provided, they will used to
        identify each of the created playlists otherwise unique ids will be
        auto-generated and returned once the playlists are created.

        Args:
            names (List[str]): Names for the playlists to be created

        Kwargs:
            index (Optional[int]):
                Positional index of where the playlists are to be inserted.

            ids (Optional[List(str)]):
                Ids to be used to indentify playlists once they are created.
                Make sure to provide unique ids for each of the playlists.
                The list must be the same length as that of the names.
                Recommended to use the following to generate these ids,
                import uuid;
                names = ["playlist_1", "playlist_2", "playlist_3"]
                ids = [uuid.uuid4().hex for _ in names]

        Returns:
            List[str]:
                Ids of the playlists created in the same order
                of the names provided.
        """
        if ids is None:
            ids = [uuid.uuid4().hex for _ in  names]
        self.__delegate_mngr.call(
            self.create_playlists, [names, index, ids])
        return ids

    def move_playlists_to_index(self, index:int, ids:List[str])->bool:
        """
        Playlists with the given respective ids will be moved to the given
        index.

        Args:
            index (int):Index to which playlists are moved to in the current session.

            ids (List[str]): Ids of Playlists.

        Returns:
            (bool): True if success False otherwise
        """
        return self.__delegate_mngr.call(
            self.move_playlists_to_index, [index, ids])

    def move_playlists_by_offset(self, offset:int, ids:List[str])->bool:
        """
        Playlists with the given respective ids will be moved up or down based
        on the given offset.A positive offset will move them down and a
        negative offset will move them up. If the offset is greater than the
        total number of playlists in the list, then they will be moved to the
        end of the list and if the offset is less than 0 then the playlists
        will be moved to the very top.

        Args:
            offset (int):
                The number of indexes the selected playlists's respective
                movement must be offsetted by. Note negative is up and
                positive is down.

            Ids (List[str]): Ids of Playlists.

        Returns:
            (bool): True if moved False otherwise
        """
        return self.__delegate_mngr.call(self.move_playlists_by_offset, [offset, ids])

    def set_playlist_name(self, id:str, name:str)->bool:
        """
        Set the name of the playlist with the given id.

        Args:
            id (str): Id of the playlist whose name needs to be set

            name (str): Name that needs to be set to the playlist

        Returns:
            (bool): True if set False otherwise
        """
        return self.__delegate_mngr.call(self.set_playlist_name, [id, name])

    def set_bg_mode(self, mode:int)->bool:
        """
        Set the Background-Mode(BG Mode) to be used in the session.
        The BG Mode is relevant only if a BG playlist is set. The various
        BG Modes can be set using integers to identify them. The following
        are the integers which can be used to set the various available
        BG modes,
        1 - Wipe Mode
        2 - Side by Side Mode
        3 - Top to Bottom Mode
        4 - Picture in Picture Mode

        Args:
            mode (int):
                The integer that represents the BG Mode that needs to be set.

        Returns:
            (bool): True if set False otherwise
        """
        return self.__delegate_mngr.call(self.set_bg_mode, [mode])

    def get_bg_mode(self)->int:
        """
        Get the integer that represents the current Background Mode
        that is set. Note that BG modes are relevant only if a BG playlist
        is currently present in the Session. Based on the current BG Mode,
        one of the following integers will be returned,
        1 - Wipe Mode
        2 - Side by Side Mode
        3 - Top to Bottom Mode
        4 - Picture in Picture Mode

        Returns:
            int : Integer representing the current BG mode.
        """
        return self.__delegate_mngr.call(self.get_bg_mode)

    ###########################################################################
    # Clip Methods                                                            #
    ###########################################################################

    def create_clips(
        self, playlist_id:str, paths:List[Union[str, Tuple[str, str]]],
        index:Optional[int]=None, ids:Optional[List[str]]=None)->List[str]:
        """
        Creates clips with the given paths in the playlist of the given
        playlist id. The paths can also be data-base ids or web-urls as long
        as mechanisms for the core application to find the media file from the
        given paths are in place. The created playlists will be inserted into
        the given index if provided otherwise the clips will be inserted at
        the bottom of the playlist. If ids are provided, they will be used to
        identify the playlists. Make sure the provided ids are uniqiue.
        Recommended to use the following to generate these ids,

        .. code-block:: python

            import uuid;
            paths = ["path/to/clip_1", ("path/to/clip_2", "path/to/audio_clip_2"), "path/to/clip_3"]
            ids = [uuid.uuid4().hex for _ in paths]

        If no ids are provided, unique ids will be autogenerated. Eitherways
        the ids of the created clips will be retured in the same order of the
        given paths. Note that all the attributes (attrs) of the clips will
        also be fetched and available in the session as clips are created.

        Args:
            playlist_id (str):
                Id of the playlist into which the clips needs to be created.

            paths (List[Union[str, Tuple[str, str]]):
                Paths to media for which clips need to be created.
                The path can be of a string, or a tuple of two strings.
                If given as a tuple, first string represents the video media path,
                and second string is the audio media path.

        Kwargs:
            index (Optional[int]):
                Optional positional index where the
                clips need to be inserted.

            ids (Optional[List[str]]):
                Optional unique ids that need to be used for
                each of the created clips.

        Returns:
            list[str]: Ids of the created clips
        """
        if ids is None:
            ids = [uuid.uuid4().hex for _ in  paths]
        return self.__delegate_mngr.call(
            self.create_clips, [playlist_id, paths, index, ids])

    def get_clips(self, id:str)->List[str]:
        """
        Get the ids of the clips in the playlist of the given id.

        Args:
            id (str): Id of the playlist

        Returns:
            list[str]: Ids of the clips
        """
        return self.__delegate_mngr.call(self.get_clips, [id])

    def set_active_clips(self, playlist_id:str, clip_ids:List[str])->None:
        """
        Set the clips whose ids have been provided to be actove in the
        playlist with the given id. Note that each time this method is used
        the previously activated clips are replaced. If an empty list is
        provided all the clips in the playlist are activated.

        Note that only active clips will be considered in the sequence of
        clips constructed for any given playlist.

        Args:
            playlist_id (str): Id of the playlist

            clip_ids (List[str]): Ids of clips.

        Returns:
            None
        """
        return self.__delegate_mngr.call(
            self.set_active_clips, [playlist_id, clip_ids])

    def get_active_clips(self, id:str)->List[str]:
        """
        Get the ids of the clips that have been activated in the playlist
        of the given id.

        Note that only active clips will be considered in the sequence of
        clips constructed for any given playlist.

        If no particular list of clips were activated by the user, then all
        the clips in the playlists will be activated and returned.

        Args:
            id (str): Id of the Playlist

        Return:
            list[str]: Ids of the clips
        """
        return self.__delegate_mngr.call(self.get_active_clips, [id])

    def move_clips_to_index(self, index:int, ids:List[str])->bool:
        """
        Move clips with the given ids in their respective playlist to the
        given index. Note that all clips must be part of the same playlist
        in order to perform this operation.

        Args:
            index (int): Index to which clips are moved to in the current playlist.

            ids (List[str]): Ids of clips.

        Returns:
            (bool): True if success False otherwise
        """
        return self.__delegate_mngr.call(self.move_clips_to_index, [index, ids])

    def move_clips_by_offset(self, offset:int, ids:List[str])->bool:
        """
        Move clips with the given ids in their respective playlists up or down
        based on the offset. Positive offset moves clips down and negative
        offset moves clips up. If offset is greater than total number of
        clips in the playlist, then clips are moved to the bottom. And if
        offset is less than 0 then clips are moved to the top.

        Args:
            offset (int):
                The number of indexes the selected clips's respective
                movement must be offsetted by. Note negative is up and
                positive is down.

            ids (List[str]): Ids of clips that need to be moved.

        Returns:
            (bool): True if moved False otherwise
        """
        return self.__delegate_mngr.call(self.move_clips_by_offset, [offset, ids])

    def delete_clips_permanently(self, ids:List[str])->bool:
        """
        Permanently delete clips with the given ids.

        Args:
            ids (List[str]): Ids of clips that need to be permanently deleted

        Returns:
            (bool): True if deleted permanently False otherwise
        """
        return self.__delegate_mngr.call(self.delete_clips_permanently, [ids])

    def get_current_clip(self)->str:
        """
        Get the id of the current clip of the session.

        Returns:
            str : Id of the current clip
        """
        return self.__delegate_mngr.call(self.get_current_clip)

    def set_current_clip(self, id:str)->bool:
        """
        Set the clip with the given id to be current clip of the Session.

        Args:
            id (str):
                Id of clip to set as current clip.

        Returns:
            (bool): True if set False otherwise
        """
        return self.__delegate_mngr.call(self.set_current_clip, [id])

    def get_playlist_of_clip(self, id:str)->str:
        """
        Get the id of the playlist in which the clip of the given id is
        currently present.

        Args:
            id (str): Id of the clip

        Returns:
            str: Id of the playlist
        """
        return self.__delegate_mngr.call(self.get_playlist_of_clip, [id])

    def set_clip_path(self, id:str, path:object)->bool:
        """
        Set the path of the media for the clip with the given id. The path
        can also be a data-base id or web url as long mechanisms for the core
        application to find the media file from the given path are in place.

        Args:
            id (str): Id of the clip whose path needs to be set.
            path (str): Path to the media

        Returns:
            (bool): True if set False otherwise
        """
        return self.__delegate_mngr.call(self.set_clip_path, [id, path])

    ###########################################################################
    # Custom Attr Methods                                                     #
    ###########################################################################

    def set_custom_session_attr(self, attr_id:str, value:Any)->bool:
        """
        Set custom attributes that will be associated with the RPA session.

        Args:
            attr_id(str): Id of the attribute
            value(Any): Value to be set

        Returns:
            bool: True if successfully set
        """
        self.__delegate_mngr.call(
            self.set_custom_session_attr, [attr_id, value])

    def get_custom_session_attr(self, attr_id)->Any:
        """
        Get custom attributes that are associated with the RPA session.

        Args:
            attr_id(str): Id of the attribute

        Returns:
            Any: Value of the given Id
        """
        return self.__delegate_mngr.call(
            self.get_custom_session_attr, [attr_id])

    def get_custom_session_attr_ids(self)->List[str]:
        """
        Get custom attribute ids that are associated with the RPA session.

        Returns:
            List[str]: Ids of attributes
        """
        return self.__delegate_mngr.call(self.get_custom_session_attr_ids)

    def set_custom_playlist_attr(self, playlist_id, attr_id, value)->bool:
        """
        Set custom attributes that will be associated with the playlist of the
        given playlist Id.

        Args:
            playlist_id(str): Id of the playlist
            attr_id(str): Id of the attribute
            value(Any): Value to be set

        Returns:
            bool: True if successfully set
        """
        return self.__delegate_mngr.call(
            self.set_custom_playlist_attr, [playlist_id, attr_id, value])

    def get_custom_playlist_attr(self, playlist_id, attr_id)->Any:
        """
        Get custom attributes that are associated with the playlist of the
        given playlist Id.

        Args:
            playlist_id(str): Id of the playlist
            attr_id(str): Id of the attribute

        Returns:
            Any: Value of the given Id
        """
        return self.__delegate_mngr.call(
            self.get_custom_playlist_attr, [playlist_id, attr_id])

    def get_custom_playlist_attr_ids(self, playlist_id)->List[str]:
        """
        Get custom attribute ids that are associated with the playlist of the
        given playlist Id.

        Args:
            playlist_id(str): Id of the playlist

        Returns:
            List[str]: Ids of attributes
        """
        return self.__delegate_mngr.call(
            self.get_custom_playlist_attr_ids, [playlist_id])

    def set_custom_clip_attr(self, clip_id, attr_id, value)->bool:
        """
        Set custom attributes that will be associated with the clip of the
        given clip Id.

        Args:
            clip_id(str): Id of the clip
            attr_id(str): Id of the attribute
            value(Any): Value to be set

        Returns:
            bool: True if successfully set
        """
        return self.__delegate_mngr.call(
            self.set_custom_clip_attr, [clip_id, attr_id, value])

    def get_custom_clip_attr(self, clip_id, attr_id)->Any:
        """
        Get custom attributes that are associated with the clip of the
        given clip Id.

        Args:
            clip_id(str): Id of the clip
            attr_id(str): Id of the attribute

        Returns:
            Any: Value of the given Id
        """
        return self.__delegate_mngr.call(
            self.get_custom_clip_attr, [clip_id, attr_id])

    def get_custom_clip_attr_ids(self, clip_id)->List[str]:
        """
        Get custom attribute ids that are associated with the clip of the
        given clip Id.

        Args:
            clip_id(str): Id of the clip

        Returns:
            List[str]: Ids of attributes
        """
        return self.__delegate_mngr.call(
            self.get_custom_clip_attr_ids, [clip_id])

    ###########################################################################
    # Clip Attr Methods                                                       #
    ###########################################################################

    def get_attrs_metadata(self)->dict:
        """
        Get the metadata of all the attributes (attrs) in the current Session.

        Returns:
            dict : Dict of the metadata of all attrs

        Example:
            Here is an example of how the returned dict will look like,

            .. code-block:: python

                {
                    'play_order':
                    {
                        'name': 'Play Order',
                        'data_type': 'int',
                        'is_read_only': True,
                        'is_keyable': False,
                        'default_value': None
                    },
                    'media_path':
                    {
                        'name': 'Media Path',
                        'data_type': 'str',
                        'is_read_only': True,
                        'is_keyable': False,
                        'default_value': '',
                    }
                }
        """
        return self.__delegate_mngr.call(self.get_attrs_metadata)

    def get_attr_value(self, clip_id:str, attr_id:str)->object:
        """
        Get the value of the attribute of the clip of the playlist whose respective
        ids are given.

        Args:
            clip_id (str): Id of the Clip
            attr_id (str): Id of the Attr

        Returns:
            object: Value of the attribute
        """
        return self.__delegate_mngr.call(
            self.get_attr_value, [clip_id, attr_id])

    def get_default_attr_value(self, id:str)->object:
        """
        Get the default value which is metadata of the
        attribute with the given id

        Args:
            id (str): Id of the attribute

        Returns:
            object: Default value of attribute
        """
        return self.__delegate_mngr.call(
            self.get_default_attr_value, [id])

    def get_attrs(self)->List[str]:
        """
        Get ids of all the attrs in the session

        Returns:
            List[str]: Ids of all attrs in the session
        """
        return self.__delegate_mngr.call(self.get_attrs)

    def get_attr_name(self, id:str)->str:
        """
        Get the name of attr with the given id

        Args:
            id (str): Id of the attr

        Returns:
            str: Name of the attr
        """
        return self.__delegate_mngr.call(self.get_attr_name, [id])

    def get_read_write_attrs(self)->List[str]:
        """
        Get the ids of all the attrs that are editable that
        is both readable and writable.

        Returns:
            List[str]: Ids of attrs that are editable
        """
        return self.__delegate_mngr.call(self.get_read_write_attrs)

    def get_read_only_attrs(self)->List[str]:
        """
        Get the ids of all the attrs that are non-editable that is read-only.

        Returns:
            List[str]: Ids of attrs that are non-editable
        """
        return self.__delegate_mngr.call(self.get_read_only_attrs)

    def get_keyable_attrs(self)->List[str]:
        """
        Get the ids of all the attrs that are keyable.

        Returns:
            List[str]: Ids of attrs that are keyable
        """
        return self.__delegate_mngr.call(self.get_keyable_attrs)

    def is_attr_read_only(self, id:str)->bool:
        """
        Returns True if the attr of the given id is non-editable
        that is read-only.

        Args:
            id (str): Id of the attr.

        Returns:
            bool: True if attr of given id is read-only else False.
        """
        return self.__delegate_mngr.call(self.is_attr_read_only, [id])

    def is_attr_keyable(self, id:str)->bool:
        """
        Returns True if the attr of the given id is keyable.

        Args:
            id (str): Id of the attr.

        Returns:
            bool: True if attr of given id is keyable else False.
        """
        return self.__delegate_mngr.call(self.is_attr_keyable, [id])

    def get_attr_data_type(self, id:str)->str:
        """
        Gets the data-type of the attr with the given id. Note that the
        data-type of the various attrs are represented as the following strings,
        "int" - integer
        "float" - float
        "str" - string
        "bool" - boolean
        "path" - file path

        Args:
            id (str): Id of the attr

        Returns:
            str: String name of the data-type as mentioned in description
        """
        return self.__delegate_mngr.call(self.get_attr_data_type, [id])

    def set_attr_values(self, attr_values:List[Tuple])->bool:
        """
        Set the value of the attributes from the given list.
        Example of how attr_values should look like,

        .. code-block:: python

            [
                (playlist_id_1, clip_id_1, attr_id_1, value),
                (playlist_id_1, clip_id_1, attr_id_2, value),
                (playlist_id_1, clip_id_2, attr_id_1, value),
                (playlist_id_2, clip_id_3, attr_id_1, value),
                (playlist_id_2, clip_id_4, attr_id_2, value)
            ]

        Args:
            attr_values (List[Tuple]):
                List of tuples containing playlist id, clip id, attr id and
                value.

        Returns:
            (bool): True if set False otherwise
        """
        return self.__delegate_mngr.call(self.set_attr_values, [attr_values])

    def refresh_attrs(self, ids:List[Tuple[str]])->bool:
        """
        Refresh session cache with the latest values for attrs of clips of
        playlists with the given ids.

        Example of how ids should look like,

        .. code-block:: python

            [
                (playlist_id_1, clip_id_1, attr_id_1),
                (playlist_id_1, clip_id_1, attr_id_2),
                (playlist_id_1, clip_id_2, attr_id_1),
                (playlist_id_2, clip_id_3, attr_id_1),
                (playlist_id_2, clip_id_4, attr_id_2)
            ]

        Args:
            ids (List[Tuple[str]]):
                List of tuples containing playlist id, clip id and attr id.

        Returns:
            (bool): True if refreshed False otherwise
        """
        return self.__delegate_mngr.call(self.refresh_attrs, [ids])

    def get_attr_value_at(self, clip_id:str, attr_id:str, key:int):
        """
        Get the value of the keyable attribute for the clip at the
        given key (frame) with respective ids.

        Args:
            clip_id (str): Id of the Clip
            attr_id (str): Id of the Attr
            key (int): Frame of the Clip

        Returns:
            object: Value of the attribute at given key
        """
        value = self.__delegate_mngr.call(
            self.get_attr_value_at, [clip_id, attr_id, key])
        return value

    def set_attr_values_at(self, attr_values_at:List[Tuple])->bool:
        """
        Set the value of the keyable attributes at the given frame.

        Example of how attr_values_at should look like,

        .. code-block:: python

            [
                (playlist_id_1, clip_id_1, attr_id_1, key, value),
                (playlist_id_1, clip_id_1, attr_id_2, key, value),
                (playlist_id_1, clip_id_2, attr_id_1, key, value),
                (playlist_id_2, clip_id_3, attr_id_1, key, value),
                (playlist_id_2, clip_id_4, attr_id_2, key, value)
            ]

        Args:
            attr_values_at (List[Tuple]):
                List of tuples containing playlist id, clip id, attr id,
                key (frame) and value.

        Returns:
            (bool): True if set False otherwise
        """
        return self.__delegate_mngr.call(self.set_attr_values_at, [attr_values_at])

    def clear_attr_values_at(self, attr_values_at:List[Tuple])->bool:
        """
        Clear the value of the keyable attributes from the list at the given frame.

        Example of how attr_values_at should look like,

        .. code-block:: python

            [
                (playlist_id_1, clip_id_1, attr_id_1, key),
                (playlist_id_1, clip_id_1, attr_id_2, key),
                (playlist_id_1, clip_id_2, attr_id_1, key),
                (playlist_id_2, clip_id_3, attr_id_1, key),
                (playlist_id_2, clip_id_4, attr_id_2, key)
            ]

        Args:
            attr_values_at (List[Tuple]):
                List of tuples containing playlist id, clip id, attr id, and key (frame).

        Returns:
            (bool): True if cleared False otherwise
        """
        return self.__delegate_mngr.call(self.clear_attr_values_at, [attr_values_at])

    def get_attr_keys(self, clip_id:str, attr_id:str)->List[int]:
        """
        Get the list of key frames of the keyable attribute within the clip.
        For non-keyable attributes, the list returned will be empty.

        Args:
            clip_id (str): Id of the Clip
            attr_id (str): Id of the Attr

        Returns:
            List[int]: List of clip key frames
        """
        return self.__delegate_mngr.call(self.get_attr_keys, [clip_id, attr_id])

    def get_session_str(self)->Union[str, Tuple[str]]:
        """
        Get the string representation of the session object. This method might
        return a pair of strings (skin, core) when running in multi-process
        mode.

        Returns:
            str:
                string representation of the session object

            tuple[str]:
                Pair of string representations of the session objects
                (skin, core) when running in multi-process mode
        """
        return self.__delegate_mngr.call(self.get_session_str)

    ###########################################################################
    # MISC                                                                    #
    ###########################################################################


    def set_current_frame_mode(self, mode:int)->bool:
        """
        Set the behavior of the current-frame when changing playlists.

        The following are the available modes,

        **0 \: Same Across Playlists**

        Current frame will be synced across all playlists.
        In the case when a single clip is selected in a playlist,
        current frame defaults to first frame of the clip.

        **1 \: First Frame**

        Current frame will default to first frame of a selected clip
        or sequence of clips within a playlist or among playlists.
        Only in the case when BG playlist exist, current frame will
        be synced across FG and BG playlists.

        **2 \: Remember Last**

        Current frame will be set to last frame it was at for the
        playlist. Only in the case when BG playlist exist, current
        frame will be synced across FG and BG playlists.

        Args:
            mode (int): Mode to set.

        Returns:
            (bool): True of set False otherwise
        """
        return self.__delegate_mngr.call(self.set_current_frame_mode, [mode])

    def get_current_frame_mode(self)->int:
        """
        Get the behavior mode of the current frame when changing playlists.

        The following are the available modes,

        **0 \: Same Across Playlists**

        Current frame will be synced across all playlists.
        In the case when a single clip is selected in a playlist,
        current frame defaults to first frame of the clip.

        **1 \: First Frame**

        Current frame will default to first frame of a selected clip
        or sequence of clips within a playlist or among playlists.
        Only in the case when BG playlist exist, current frame will
        be synced across FG and BG playlists.

        **2 \: Remember Last**

        Current frame will be set to last frame it was at for the
        playlist. Only in the case when BG playlist exist, current
        frame will be synced across FG and BG playlists.

        Returns:
            int: Behavior mode of current frame
        """
        return self.__delegate_mngr.call(self.get_current_frame_mode)
