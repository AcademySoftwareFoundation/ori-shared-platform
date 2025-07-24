"""
Timeline API
============

Manage timeline's Play State and Volume controls.

Also convert current frame of a clip to its frame number relative to the
current timeline sequence and vice versa.
"""

from typing import List, Optional, Tuple
try:
    from PySide2 import QtCore
except ImportError:
    from PySide6 import QtCore
from rpa.delegate_mngr import DelegateMngr


class TimelineApi(QtCore.QObject):
    SIG_MODIFIED = QtCore.Signal()
    # Gets emitted whenever the timeline is modified. This includes,
    # current-frame changed and frame-range changed.
    SIG_FRAME_CHANGED = QtCore.Signal(int) # frame
    # Gets emitted whenever the frame is changed in the timeline.
    SIG_PLAY_STATUS_CHANGED = QtCore.Signal(bool, bool) # playing, is_forward
    # Gets emitted whenever the play status changes. Play status includes
    # whether timeline is playing and the direction in which it is playing.

    def __init__(self, logger):
        super().__init__()
        self.__delegate_mngr = DelegateMngr(logger)

    @property
    def delegate_mngr(self):
        return self.__delegate_mngr

    ###########################################################################
    # Frame Controls                                                          #
    ###########################################################################

    def set_playing_state(self, playing, forward=True)->bool:
        """
        Sets the playing state for the media

        Args:
            playing (bool): play if True, else stop
            forward (bool): plays forward if True, else reversed

        Returns:
            (bool) : True if set False otherwise
        """
        return self.__delegate_mngr.call(
            self.set_playing_state, [playing, forward])

    def get_playing_state(self):
        """
        Returns the current playing state

        Returns:
            Two bools representing is-playing and is-forward states
        """
        return self.__delegate_mngr.call(self.get_playing_state)

    def goto_frame(self, frame:int)->bool:
        """
        Go to the specified frame.

        Note that the given frame number must be relative to the timeline
        sequence and not relative to individual clips.

        Args:
            frame (int): Frame in timeline sequence

        Returns:
            (bool) : True if set False otherwise
        """
        return self.__delegate_mngr.call(self.goto_frame, [frame])

    def get_current_frame(self)->int:
        """
        Get the current frame of the timeline.
        If no current clip is present then 0 is returned.

        Note that the frame number returned is relative to the timeline
        sequence and not relative to individual clips.

        Returns:
            (int) : Current frame
        """
        return self.__delegate_mngr.call(self.get_current_frame)

    def get_frame_range(self)->Tuple[int, int]:
        """
        Get the current frame of the timeline.
        If no current clip is present then 0 is returned.

        Note that the frame numbers returned are relative to the timeline
        sequence and not relative to individual clips.

        Returns:
            (Tuple[int, int]) : Start and end frames of the timeline.
        """
        return self.__delegate_mngr.call(self.get_frame_range)

    def get_seq_frames(
        self, clip_id: str, frames: Optional[List[int]]=None)->List[int]:
        """
        Get the frames relative to the current timeline sequence that
        corresponds to the given clip frames. If frames are not given, then
        all the frames in the current timeline sequence will be returned.

        Args:
            clip_id (str):
                Id of clip in timeline whose frames need to be converted
                into timeline sequence frames.

        Kwargs:
            frames(List[int]): Frames relative to the given clip.

        Returns:
            List[int]:
                Frames relative to the timeline sequence.
        """
        return self.__delegate_mngr.call(
            self.get_seq_frames, [clip_id, frames])

    def get_clip_frames(self, frames: Optional[List[int]]=None)->List[Tuple[str, int]]:
        """
        Get the frames relative to the clips in the timeline corresponding
        to the given timeline sequence frames. If frames are not given, then
        all the ids of the clips with their respective clip frames will be returned.

        Kwargs:
            frames(List[int]): List of timeline sequence frames

        Returns:
            List[str, int]:
                Clip-ids and Frames relative to the clips in the timeline.

        Example of how the returned list will look like,

        .. code-block:: python

            [
                ("clip_id_1", 1001), ("clip_id_1", 1002),
                ("clip_id_2", 1005), ("clip_id_2", 1006), ("clip_id_2", 1007),
                ("clip_id_3", 1001), ("clip_id_3", 1002)
            ]
        """
        return self.__delegate_mngr.call(self.get_clip_frames, [frames])

    ###########################################################################
    # Audio Controls                                                          #
    ###########################################################################

    def get_volume(self):
        """
        Get current volume

        Returns:
            int value in [0,100] range
        """
        return self.__delegate_mngr.call(
            self.get_volume)

    def set_volume(self, volume: int)->bool:
        """
        Sets current volume

        Args:
            volume (int): desired volume

        Returns:
            (bool): True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_volume, [volume])

    def set_mute(self, state: bool):
        """
        Set/unset audio to mute

        Args:
            state (bool): desired state of mute

        Returns:
            (bool): True if success False otherwise
        """
        return self.__delegate_mngr.call(self.set_mute, [state])

    def is_mute(self):
        """
        Get current state of mute on audio

        Returns:
            bool - if True audio is muted, else not muted
        """
        return self.__delegate_mngr.call(self.is_mute)

    def enable_audio_scrubbing(self, state)->bool:
        """
        Set on/off to audio scrubbing mode

        Args:
            state (bool): on/off flag

        Returns:
            (bool) : True if set False otherwise
        """
        return self.__delegate_mngr.call(self.enable_audio_scrubbing, [state])

    def is_audio_scrubbing_enabled(self):
        """
        Get current audio scrubbing state

        Returns:
            bool representing on or off scrubbing state
        """
        return self.__delegate_mngr.call(self.is_audio_scrubbing_enabled)

    ###########################################################################
    # Playback Controls                                                       #
    ###########################################################################

    def set_playback_mode(self, mode:int):
        """
        Set the playback mode of the current session
        0 - Playback Repeat (Loop)
        1 - Playback Once
        2 - Playback Swing (PingPong)

        Args:
            mode (int):
                An integer that represents the playback mode being set

        Returns:
            (bool): True if set, otherwise False
        """
        return self.__delegate_mngr.call(self.set_playback_mode, [mode])

    def get_playback_mode(self)->int:
        """
        Get the current playback mode
        The default playback mode is set to: 0 - Playback Repeat
        The returned playback mode is one of the following:
        0 - Playback Repeat (Loop)
        1 - Playback Once
        2 - Playback Swing (PingPong)

        Returns:
           An integer representing the current playback mode
        """
        return self.__delegate_mngr.call(self.get_playback_mode)
