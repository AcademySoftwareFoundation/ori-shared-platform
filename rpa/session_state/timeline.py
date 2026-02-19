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
        if frame <= 0:
            return
        self.__current_frame = \
            max(self.__get_start_frame(), min(frame, self.__get_end_frame()))
        return self.__current_frame

    def __get_start_frame(self):
        frame = 0
        if self.__seq_to_clip:
            frame, _ = next(iter(self.__seq_to_clip.items()))
        return frame

    def __get_end_frame(self):
        frame = 0
        if self.__seq_to_clip:
            frame, _ = next(iter(reversed(self.__seq_to_clip.items())))
        return frame

    def get_seq_frames(self, clip_id, frames=None):
        seq_frames = self.__clip_to_seq.get(clip_id)
        if not seq_frames: return []

        if frames is None:
            return [(clip_frame, seqs) for clip_frame, seqs in seq_frames.items()]
        else:
            return [(clip_frame, seqs) for clip_frame, seqs in seq_frames.items() if clip_frame in frames]

    def get_clip_frames(self, seq_frames=None):
        if not self.__seq_to_clip:
            return []

        if seq_frames is None:
            return list(self.__seq_to_clip.values())
        else:
            return [self.__seq_to_clip.get(seq_frame) for seq_frame in seq_frames]

    def update(self):
        self.__seq_to_clip.clear()
        self.__clip_to_seq.clear()
        playlist = self.__session.get_playlist(self.__session.viewport.fg)
        clips = []
        active_clip_ids = playlist.active_clip_ids
        for clip_id in active_clip_ids:
            clips.append(self.__session.get_clip(clip_id))

        seq_frame = 1
        last_clip_index = len(clips) - 1
        for i, clip in enumerate(clips):
            if len(clips) > 1 and i != last_clip_index:
                src_frames = clip.get_timeline_frames()
            else:
                src_frames = clip.get_source_frames()
            for local_frame, clip_frame in enumerate(src_frames, 1):
                self.__seq_to_clip[seq_frame] = (clip.id, clip_frame, local_frame)
                clip_to_seq = self.__clip_to_seq.setdefault(clip.id, {})
                clip_to_seq.setdefault(clip_frame, []).append(seq_frame)
                seq_frame += 1

        self.__current_frame = max(
            self.__get_start_frame(),
            min(self.__current_frame, self.__get_end_frame()))


        return True

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
