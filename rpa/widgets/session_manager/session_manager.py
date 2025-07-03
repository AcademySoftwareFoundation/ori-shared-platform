from PySide2 import QtCore, QtWidgets
from rpa.widgets.session_manager.splitter import Splitter
from rpa.widgets.session_manager.toolbars.playlists_toolbar.playlists_toolbar \
    import PlaylistsToolbar
from rpa.widgets.session_manager.toolbars.clips_toolbar.clips_toolbar \
    import ClipsToolbar
from rpa.widgets.session_manager.playlists_controller.playlists_controller \
    import PlaylistsController
from rpa.widgets.session_manager.clips_controller.clips_controller \
    import ClipsController
from enum import Enum
import json
from rpa.session_state.annotations import Annotation
from rpa.session_state.color_corrections import ColorCorrection
import uuid


class PrefKey(Enum):
    PLUGIN = "playlist_manager"
    SPLITTER_STATE = "splitter_state"


class SessionManager:

    def __init__(self, rpa, parent_widget):
        super().__init__()
        self.__playlists_toolbar = PlaylistsToolbar(parent_widget)
        self.__clips_toolbar = ClipsToolbar(parent_widget)
        self.__playlists_controller = PlaylistsController(rpa, parent_widget)
        self.__clips_controller = ClipsController(rpa, parent_widget)

        self.__view = QtWidgets.QMainWindow(parent_widget)
        self.__view.setWindowTitle("Session Manager")
        self.__view.setMaximumHeight(500)
        self.__view.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.__view.addToolBar(QtCore.Qt.LeftToolBarArea, self.__playlists_toolbar)
        self.__view.addToolBar(QtCore.Qt.LeftToolBarArea, self.__clips_toolbar)

        self.__splitter = Splitter(self.__view)
        self.__splitter.setOrientation(QtCore.Qt.Horizontal)
        self.__splitter.addWidget(self.__playlists_controller.view)
        self.__splitter.addWidget(self.__clips_controller.view)

        self.__view.setCentralWidget(self.__splitter)
        self.__rpa = rpa
        self.__config_api = rpa.config_api

        self.__playlists_toolbar.SIG_CREATE.connect(
            self.__playlists_controller.create)
        self.__playlists_toolbar.SIG_DELETE.connect(
            self.__playlists_controller.delete)
        self.__playlists_toolbar.SIG_DELETE_PERMANENTLY.connect(
            self.__playlists_controller.delete_permanently)
        self.__playlists_toolbar.SIG_MOVE_TOP.connect(
            self.__playlists_controller.move_top)
        self.__playlists_toolbar.SIG_MOVE_UP.connect(
            self.__playlists_controller.move_up)
        self.__playlists_toolbar.SIG_MOVE_DOWN.connect(
            self.__playlists_controller.move_down)
        self.__playlists_toolbar.SIG_MOVE_BOTTOM.connect(
            self.__playlists_controller.move_bottom)
        self.__playlists_toolbar.SIG_CLEAR.connect(
            self.__playlists_controller.clear)

        self.__clips_toolbar.SIG_CREATE.connect(
            self.__clips_controller.create)
        self.__clips_toolbar.SIG_DELETE_PERMANENTLY.connect(
            self.__clips_controller.delete_permanently)
        self.__clips_toolbar.SIG_MOVE_TOP.connect(
            self.__clips_controller.move_top)
        self.__clips_toolbar.SIG_MOVE_UP.connect(
            self.__clips_controller.move_up)
        self.__clips_toolbar.SIG_MOVE_DOWN.connect(
            self.__clips_controller.move_down)
        self.__clips_toolbar.SIG_MOVE_BOTTOM.connect(
            self.__clips_controller.move_bottom)

        self.__playlists_controller.SIG_CUT.connect(self.__cut_playlists)
        self.__playlists_controller.SIG_COPY.connect(self.__copy_playlists)
        self.__playlists_controller.SIG_PASTE.connect(self.__paste_playlists)
        self.__playlists_controller.SIG_DUPLICATE.connect(self.__duplicate_playlists)
        self.__playlists_controller.SIG_MOVE.connect(self.__move_playlists)
        self.__playlists_controller.SIG_ADD_CLIPS.connect(self.__add_clips_to_playlist)

        self.__clips_controller.SIG_CUT.connect(self.__cut_clips)
        self.__clips_controller.SIG_COPY.connect(self.__copy_clips)
        self.__clips_controller.SIG_PASTE.connect(self.paste_clips)
        self.__clips_controller.SIG_MOVE.connect(self.__move_clips)

        self.__load_preferences()

        self.__injected_media_path_attr_ids = []
        self.__get_media_path_for_paste = None

    @property
    def view(self):
        return self.__view

    @property
    def playlists_controller(self):
        return self.__playlists_controller

    @property
    def clips_controller(self):
        return self.__clips_controller

    @property
    def playlists_toolbar(self):
        return self.__playlists_toolbar

    @property
    def clips_toolbar(self):
        return self.__clips_toolbar

    def __load_preferences(self):
        self.__config_api.beginGroup(PrefKey.PLUGIN.value)

        splitter_state = \
            self.__config_api.value(PrefKey.SPLITTER_STATE.value, None)
        self.__splitter.set_state(splitter_state)

        self.__config_api.endGroup()

    def save_preferences(self):
        self.__config_api.beginGroup(PrefKey.PLUGIN.value)

        self.__config_api.setValue(
            PrefKey.SPLITTER_STATE.value, self.__splitter.saveState())
        self.__config_api.endGroup()

        self.__clips_controller.save_preferences()

    def __cut_playlists(self):
        self.__copy_playlists()
        self.__playlists_controller.delete_permanently()

    def __duplicate_playlists(self):
        self.__copy_playlists()
        self.__paste_playlists()

    def __copy_playlists(self):
        selected_playlist_ids = \
            self.__playlists_controller.get_selected_playlists()

        playlists_data = {}
        for playlist_id in selected_playlist_ids:
            clip_ids = self.__rpa.session_api.get_clips(playlist_id)

            playlists_data.setdefault(playlist_id, {})["name"] = \
                self.__rpa.session_api.get_playlist_name(playlist_id)
            playlists_data[playlist_id]["clips_data"] = \
                self.__get_clips_data(playlist_id, clip_ids)
        self.__dict_to_clipboard(playlists_data, "rpa/playlists")

    def __paste_playlists(self):
        playlists_data = self.__clipboard_to_dict("rpa/playlists")
        if not playlists_data: return

        playlist_names = []
        for _, playlist_data in playlists_data.items():
            playlist_names.append(playlist_data["name"] + " copy")

        playlist_ids = self.__rpa.session_api.create_playlists(playlist_names)

        cnt = 0
        for _, playlist_data in playlists_data.items():
            playlist_id = playlist_ids[cnt]
            cnt += 1
            clips_data = playlist_data.get("clips_data")
            if clips_data is None: continue
            self.__paste_clips(playlist_id, clips_data)

    def __move_playlists(self, drop_index:int):
        all_playlist_ids = self.__rpa.session_api.get_playlists()
        selected_playlist_ids = \
            self.__playlists_controller.get_selected_playlists()

        if drop_index == -1:
            drop_index = len(all_playlist_ids) - 1
        self.__rpa.session_api.move_playlists_to_index(
            drop_index, selected_playlist_ids)

    def __add_clips_to_playlist(self, playlist_id, clip_ids):
        self.__dict_to_clipboard(
            self.__get_clips_data(playlist_id, clip_ids), "rpa/clips")
        clips_data = self.__clipboard_to_dict("rpa/clips")
        if not clips_data:
            return
        fg_playlist_id = self.__rpa.session_api.get_fg_playlist()
        if fg_playlist_id != playlist_id:
            self.__rpa.session_api.set_fg_playlist(playlist_id)
        self.__paste_clips(playlist_id, clips_data)

    def __cut_clips(self):
        self.__copy_clips()
        self.__clips_controller.delete_permanently()

    def __copy_clips(self):
        playlist_id = self.__rpa.session_api.get_fg_playlist()
        clip_ids = self.__rpa.session_api.get_active_clips(playlist_id)
        self.__dict_to_clipboard(
            self.__get_clips_data(playlist_id, clip_ids), "rpa/clips")

    def paste_clips(self):
        playlist_id = self.__rpa.session_api.get_fg_playlist()
        clips_data = self.__clipboard_to_dict("rpa/clips")
        if not clips_data: return
        self.__paste_clips(playlist_id, clips_data)

    def __move_clips(self, drop_index:int):
        playlist_id = self.__rpa.session_api.get_fg_playlist()
        clip_ids = self.__rpa.session_api.get_clips(playlist_id)
        active_clip_ids = self.__rpa.session_api.get_active_clips(playlist_id)

        if drop_index == -1:
            drop_index = len(clip_ids) - 1
        self.__rpa.session_api.move_clips_to_index(drop_index, active_clip_ids)

    def __dict_to_clipboard(self, data:dict, mime_key:str):
        data = json.dumps(data).encode("utf-8")
        mime_data = QtCore.QMimeData()
        mime_data.setData(mime_key, data)
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setMimeData(mime_data)

    def __clipboard_to_dict(self, mime_key:str):
        clipboard = QtWidgets.QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if not mime_data.hasFormat(mime_key): return
        raw = mime_data.data(mime_key)
        try: clips_data = json.loads(bytes(raw))
        except json.JSONDecodeError: return {}
        return clips_data

    def __get_clips_data(self, playlist, clips):
        clips_data = {}
        for clip in clips:
            clip_data = {}

            # Attrs
            attr_values = {}
            for attr_id, metadata in \
            self.__rpa.session_api.get_attrs_metadata().items():
                if metadata.get("is_read_only", True): continue
                attr_values[attr_id] = self.__rpa.session_api.get_attr_value(
                    clip, attr_id)
            media_path_attr_ids = ["media_path"]
            media_path_attr_ids.extend(self.__injected_media_path_attr_ids)
            for attr_id in media_path_attr_ids:
                attr_values[attr_id] = self.__rpa.session_api.get_attr_value(
                    clip, attr_id)
            clip_data["attrs"] = attr_values

            # Custom Attrs
            for attr_id in self.__rpa.session_api.get_custom_clip_attr_ids(clip):
                clip_data.setdefault("custom_attrs", {})[attr_id] = \
                    self.__rpa.session_api.get_custom_clip_attr(clip, attr_id)

            # Annotations
            for frame in self.__rpa.annotation_api.get_ro_frames(clip):
                ro_annos = \
                    self.__rpa.annotation_api.get_ro_annotations(clip, frame)
                ro_annos = [annos.__getstate__() for annos in ro_annos]
                clip_data.setdefault(
                    "annotations", {}).setdefault("ro", {})[frame] = ro_annos

            for frame in self.__rpa.annotation_api.get_rw_frames(clip):
                rw_anno = \
                    self.__rpa.annotation_api.get_rw_annotation(clip, frame)
                clip_data.setdefault(
                    "annotations", {}).setdefault("rw", {})[frame] = \
                        rw_anno.__getstate__()

            # Color Corrections
            # RO Clip CCs
            clip_ro_ccs = self.__rpa.color_api.get_ro_ccs(clip)
            clip_ro_ccs = [(None, cc.__getstate__()) for cc in clip_ro_ccs]
            clip_data.setdefault("color_corrections", {}).\
                setdefault("ro", []).extend(clip_ro_ccs)
            # RO Frame CCs
            for frame in self.__rpa.color_api.get_ro_frames(clip):
                clip_ro_ccs = self.__rpa.color_api.get_ro_ccs(clip, frame)
                clip_ro_ccs = [(frame, cc.__getstate__()) for cc in clip_ro_ccs]
                clip_data.setdefault("color_corrections", {}).\
                    setdefault("ro", []).extend(clip_ro_ccs)

            # RW Clip CCs
            clip_rw_ccs = self.__rpa.color_api.get_rw_ccs(clip)
            clip_rw_ccs = [(None, cc.__getstate__()) for cc in clip_rw_ccs]
            clip_data.setdefault("color_corrections", {}).\
                setdefault("rw", []).extend(clip_rw_ccs)
            # RW Frame CCs
            for frame in self.__rpa.color_api.get_rw_frames(clip):
                clip_rw_ccs = self.__rpa.color_api.get_rw_ccs(clip, frame)
                clip_rw_ccs = [(frame, cc.__getstate__()) for cc in clip_rw_ccs]
                clip_data.setdefault("color_corrections", {}).\
                    setdefault("rw", []).extend(clip_rw_ccs)

            clips_data[clip] = clip_data

        return clips_data

    def __paste_clips(self, playlist, clips_data, index=None):
        media_paths = []
        for _, clip_data in clips_data.items():
            attrs = clip_data.get("attrs")
            if self.__get_media_path_for_paste and \
            self.__get_media_path_for_paste(attrs) is not None:
                media_paths.append(self.__get_media_path_for_paste(attrs))
            else:
                media_paths.append(attrs.get("media_path"))

        clips = self.__rpa.session_api.get_clips(playlist)
        active_clips = self.__rpa.session_api.get_active_clips(playlist)
        if not clips: index = 0
        else:
            if active_clips:
                index = clips.index(active_clips[-1])
            else:
                if index is None:
                    index = len(clips) - 1

        clip_ids = self.__rpa.session_api.create_clips(
            playlist, media_paths, index + 1)

        cnt = 0
        attr_values = []
        ro_annos = {}
        rw_annos = {}
        ro_ccs = {}
        rw_ccs = {}
        for _, clip_data in clips_data.items():
            clip_id = clip_ids[cnt]
            cnt += 1

            attrs = clip_data.get("attrs")
            for attr_id, value in attrs.items():
                media_path_attr_ids = ["media_path"]
                media_path_attr_ids.extend(self.__injected_media_path_attr_ids)
                if attr_id in ["media_path"]: continue
                attr_values.append((playlist, clip_id,  attr_id, value))

            custom_attrs = clip_data.get("custom_attrs")
            if custom_attrs:
                for attr_id, value in custom_attrs.items():
                    self.__rpa.session_api.set_custom_clip_attr(clip_id, attr_id, value)

            if clip_data.get("annotations"):
                if clip_data["annotations"].get("ro"):
                    for frame, annos in clip_data["annotations"]["ro"].items():
                        annos = [Annotation().__setstate__(anno) for anno in annos]
                        ro_annos.setdefault(clip_id, {})[int(frame)] = annos

                if clip_data["annotations"].get("rw"):
                    for frame, anno in clip_data["annotations"]["rw"].items():
                        rw_annos.setdefault(clip_id, {})[int(frame)] = \
                            Annotation().__setstate__(anno)

            if clip_data.get("color_corrections"):
                if clip_data["color_corrections"].get("ro"):
                    for frame, ccs in clip_data["color_corrections"]["ro"]:
                        cc_objects = []
                        for cc in ccs:
                            color_correction = ColorCorrection()
                            color_correction.__setstate__(cc)
                            color_correction.id = uuid.uuid4().hex
                            cc_objects.append(color_correction)
                        ro_ccs.setdefault(clip_id, []).append((int(frame), cc_objects))

                if clip_data["color_corrections"].get("rw"):
                    for frame, cc in clip_data["color_corrections"]["rw"]:
                        frame = int(frame) if frame is not None else frame
                        cc["id"] = uuid.uuid4().hex
                        rw_ccs.setdefault(clip_id, []).append(
                            (frame, ColorCorrection().__setstate__(cc)))

        self.__rpa.session_api.set_attr_values(attr_values)
        if ro_annos: self.__rpa.annotation_api.set_ro_annotations(ro_annos)
        if rw_annos: self.__rpa.annotation_api.set_rw_annotations(rw_annos)
        if ro_ccs: self.__rpa.color_api.set_ro_ccs(ro_ccs)
        if rw_ccs: self.__rpa.color_api.set_rw_ccs(rw_ccs)
        self.__rpa.session_api.set_active_clips(playlist, clip_ids)

    def inject_get_media_path_for_paste(self, callable):
        self.__get_media_path_for_paste = callable

    def inject_media_path_attr_ids(self, attr_ids):
        self.__injected_media_path_attr_ids = attr_ids[:]
