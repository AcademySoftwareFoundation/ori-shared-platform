from dataclasses import dataclass


@dataclass
class PlayingState:
    is_playing: bool = False
    is_forward: bool = True


@dataclass
class AudioState:
    is_mute:bool = False
    is_audio_scrubbing_enabled:bool = False
    volume:int = 0


class Timeline:

    def __init__(self, session):
        self.__session = session
        self.__playing_state = PlayingState(False, True)
        self.__audio_state = AudioState(False, False, 100)
        self.__current_frame = 0
        self.__seq_to_clip = {}
        self.__clip_to_seq = {}
        self.__playback_mode = 0

    def set_playing_state(self, is_playing, is_forward):
        self.__playing_state.is_playing = is_playing
        self.__playing_state.is_forward = is_forward

    def get_playing_state(self):
        return \
            self.__playing_state.is_playing, self.__playing_state.is_forward

    def get_frame_range(self):
        return self.__get_start_frame(), self.__get_end_frame()

    def get_current_frame(self):
        playlist = self.__session.get_playlist(self.__session.viewport.fg)
        if not playlist.clip_ids:
            self.__current_frame = 0
        return self.__current_frame

    def set_current_frame(self, frame):
        if not frame:
            return
        self.__current_frame = \
            max(self.__get_start_frame(), min(frame, self.__get_end_frame()))
        return self.__current_frame

    def __get_start_frame(self):
        if not self.__seq_to_clip:
            return 0
        else:
            frame, _ = next(iter(self.__seq_to_clip.items()))
            return frame

    def __get_end_frame(self):
        if not self.__seq_to_clip:
            return 0
        else:
            frame, _ = next(iter(reversed(self.__seq_to_clip.items())))
            return frame

    def get_seq_frames(self, clip_id, frames=None):
        seq_frames = self.__clip_to_seq.get(clip_id)
        if not seq_frames: return []

        if frames is None:
            return list(seq_frames.values())
        else:
            out = []
            for frame in frames:
                out.append(seq_frames.get(frame))
        return out

    def get_clip_frames(self, seq_frames=None):
        if not self.__seq_to_clip:
            return [0]

        if seq_frames is None:
            return list(self.__seq_to_clip.values())
        else:
            out = []
            for seq_frame in seq_frames:
                out.append(self.__seq_to_clip.get(seq_frame))
        return out

    def update(self):
        self.__seq_to_clip.clear()
        self.__clip_to_seq.clear()
        playlist = self.__session.get_playlist(self.__session.viewport.fg)
        clips = []
        active_clip_ids = playlist.active_clip_ids
        for clip_id in active_clip_ids:
            clips.append(self.__session.get_clip(clip_id))

        seq_frame = 1
        for clip in clips:
            key_in = clip.get_attr_value("key_in")
            key_out = clip.get_attr_value("key_out")
            key_in = 0 if key_in is None else key_in
            key_out = 0 if key_out is None else key_out
            for clip_frame in range(key_in, key_out + 1):
                self.__seq_to_clip[seq_frame] = (clip.id, clip_frame)
                self.__clip_to_seq.setdefault(clip.id, {})[clip_frame] = seq_frame
                seq_frame += 1

        self.__current_frame = max(
            self.__get_start_frame(),
            min(self.__current_frame, self.__get_end_frame()))

    def set_volume(self, volume):
        self.__audio_state.volume = volume
        return True

    def get_volume(self):
        return self.__audio_state.volume

    def set_mute(self, state):
        self.__audio_state.is_mute = state

    def is_mute(self):
        return self.__audio_state.is_mute

    def enable_audio_scrubbing(self, state):
        self.__audio_state.is_audio_scrubbing_enabled = state

    def is_audio_scrubbing_enabled(self):
        return self.__audio_state.is_audio_scrubbing_enabled

    def set_playback_mode(self, mode):
        self.__playback_mode = mode

    def get_playback_mode(self):
        return self.__playback_mode
