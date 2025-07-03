from PySide2 import QtCore
from rv import runtime
from rv import extra_commands as rve
from rv import commands as rvc


class TimelineApiCore(QtCore.QObject):
    SIG_MODIFIED = QtCore.Signal()
    SIG_FRAME_CHANGED = QtCore.Signal(int) # frame
    SIG_PLAY_STATUS_CHANGED = QtCore.Signal(bool, bool) # playing, forward

    def __init__(self, session, session_api):
        super().__init__()
        self.__session = session
        self.__session_api = session_api

        self.__session_api.SIG_PLAYLIST_MODIFIED.connect(
            self.__playlist_seq_modified)
        self.__session_api.SIG_ACTIVE_CLIPS_CHANGED.connect(
            self.__playlist_seq_modified)
        self.__session_api.SIG_ATTR_VALUES_CHANGED.connect(
            self.__attr_values_changed)

    def set_playing_state(self, playing, forward):
        self.__session.timeline.set_playing_state(playing, forward)
        is_playing, is_forward = self.__session.timeline.get_playing_state()
        if is_playing: rvc.play()
        else: rvc.stop()
        rvc.setInc(1 if is_forward else -1)
        return True

    def get_playing_state(self):
        return self.__session.timeline.get_playing_state()

    def goto_frame(self, frame):
        self.__set_current_frame(frame)
        rvc.stop()
        runtime.eval(
            "require audio_api;"
            "audio_api.check_for_scrubbing();", [])
        rvc.setFrame(frame)

    def get_current_frame(self):
        return self.__session.timeline.get_current_frame()

    def get_frame_range(self):
        return self.__session.timeline.get_frame_range()

    def get_seq_frames(self, clip_id, frames=None):
        return self.__session.timeline.get_seq_frames(clip_id, frames)

    def get_clip_frames(self, frames=None):
        return self.__session.timeline.get_clip_frames(frames)

    def get_volume(self):
        return self.__session.timeline.get_volume()

    def set_volume(self, volume):
        volume = volume / 100.0
        self.__session.timeline.set_volume(volume)
        rvc.setFloatProperty("#RVSoundTrack.audio.volume", [volume])
        return True

    def set_mute(self, state):
        self.__session.timeline.set_mute(state)
        rvc.setIntProperty(
            "#RVSoundTrack.audio.mute", [1 if state else 0])
        return True

    def is_mute(self):
        return self.__session.timeline.is_mute()

    def enable_audio_scrubbing(self, state):
        self.__session.timeline.enable_audio_scrubbing(state)
        rvc.stop()
        mode = "true" if state is True else "false"
        runtime.eval(
            "require audio_api;"
            f"audio_api.toggle_scrubbing_mode({mode});", [])
        return True

    def is_audio_scrubbing_enabled(self):
        return self.__session.timeline.is_audio_scrubbing_enabled()

    def set_playback_mode(self, mode):
        self.__session.timeline.set_playback_mode(mode)
        rvc.setPlayMode(mode)
        rvc.redraw()
        return True

    def get_playback_mode(self):
        return self.__session.timeline.get_playback_mode()

    def emit_frame_changed(self):
        frame = rvc.frame()
        self.__set_current_frame(frame)
        self.SIG_FRAME_CHANGED.emit(frame)

    def emit_play_status_changed(self):
        is_playing, is_forward = rvc.isPlaying(), rvc.inc() > 0
        self.__session.timeline.set_playing_state(is_playing, is_forward)
        self.SIG_PLAY_STATUS_CHANGED.emit(is_playing, is_forward)

    def __playlist_seq_modified(self, playlist_id):
        if self.__session.viewport.fg == playlist_id:
            self.__session.timeline.update()
            self.SIG_MODIFIED.emit()

    def __attr_values_changed(self, attr_values):
        for attr_value in attr_values:
            playlist_id, clip_id, attr_id, value = attr_value
            if all([
                self.__session.viewport.fg == playlist_id,
                any([
                    attr_id == "key_in",
                    attr_id == "key_out"
                ])
            ]):
                self.__session.timeline.update()
                self.SIG_MODIFIED.emit()

    def __set_current_frame(self, frame):
        out = self.__session.timeline.set_current_frame(frame)
        return out
