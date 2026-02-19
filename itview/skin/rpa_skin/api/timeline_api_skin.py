from PySide2 import QtCore
from itview.skin.rpa_skin.attr_utils import make_callables, connect_signals


class TimelineApiSkin(QtCore.QObject):
    SIG_MODIFIED = QtCore.Signal()
    SIG_FRAME_CHANGED = QtCore.Signal(int) # frame
    SIG_PLAY_STATUS_CHANGED = QtCore.Signal(bool, bool) # playing, forward

    def __init__(self, rpa_tx, session_api, session):
        super().__init__()
        self.__rpa_tx = rpa_tx
        self.__session = session
        self.__session_api = session_api
        make_callables(self.__rpa_tx, self)
        connect_signals(self.__rpa_tx, self)

        self.SIG_FRAME_CHANGED.connect(
            self.__set_current_frame)
        self.SIG_PLAY_STATUS_CHANGED.connect(
            self.__session.timeline.set_playing_state)

        self.__session_api.SIG_FG_PLAYLIST_CHANGED.connect(
            self._playlist_seq_modified)
        self.__session_api.SIG_PLAYLIST_MODIFIED.connect(
            self._playlist_seq_modified)
        self.__session_api.SIG_ATTR_VALUES_CHANGED.connect(
            self.__attr_values_changed)

    def set_playing_state(self, playing, forward):
        self.__session.timeline.set_playing_state(playing, forward)
        self.__rpa_tx.set_playing_state(playing, forward)

    def get_playing_state(self):
        return self.__session.timeline.get_playing_state()

    def goto_frame(self, frame:int)->bool:
        frame = self.__set_current_frame(frame)
        return self.__rpa_tx.goto_frame(frame)

    def get_current_frame(self, wait=False):
        if wait:
            return self.__rpa_tx.get_current_frame(wait)
        else:
            return self.__session.timeline.get_current_frame()

    def get_frame_range(self):
        return self.__session.timeline.get_frame_range()

    def get_seq_frames(self, clip_id, frames=None):
        return self.__session.timeline.get_seq_frames(clip_id, frames)

    def get_clip_frames(self, frames=None):
        return self.__session.timeline.get_clip_frames(frames)

    def get_volume(self):
        return self.__session.timeline.get_volume()

    def set_volume(self, volume: int)->bool:
        self.__session.timeline.set_volume(volume)
        return self.__rpa_tx.set_volume(volume)

    def set_mute(self, state):
        self.__session.timeline.set_mute(state)
        return self.__rpa_tx.set_mute(state)

    def is_mute(self):
        return self.__session.timeline.is_mute()

    def enable_audio_scrubbing(self, state):
        self.__session.timeline.enable_audio_scrubbing(state)
        self.__rpa_tx.enable_audio_scrubbing(state)

    def is_audio_scrubbing_enabled(self):
        return self.__session.timeline.is_audio_scrubbing_enabled()

    def set_playback_mode(self, mode):
        self.__session.timeline.set_playback_mode(mode)
        return self.__rpa_tx.set_playback_mode(mode)

    def get_playback_mode(self):
        return self.__session.timeline.get_playback_mode()

    def _playlist_seq_modified(self, playlist_id):
        if self.__session.viewport.fg != playlist_id: return
        self.__session.timeline.update()
        self.SIG_MODIFIED.emit()

    def __attr_values_changed(self, attr_values):
        if any(attr_value[0] == self.__session.viewport.fg and \
            attr_value[2] in ("key_in", "key_out") for attr_value in attr_values):
            self.__session.timeline.update()
            self.SIG_MODIFIED.emit()

    def __set_current_frame(self, frame):
        out = self.__session.timeline.set_current_frame(frame)
        return out
