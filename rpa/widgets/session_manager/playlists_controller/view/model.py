import json
from PySide2 import QtCore, QtGui
import rpa.widgets.session_manager.playlists_controller.view.resources.resources


class Model(QtCore.QAbstractListModel):

    SIG_MOVE = QtCore.Signal(int) # drop index
    SIG_ADD_CLIPS = QtCore.Signal(int, list) # drop index, clip_ids

    def __init__(self, rpa, parent=None):
        super().__init__(parent)
        self.__reg_icon = QtGui.QIcon(QtGui.QPixmap(":reg_playlist.png"))
        self.__fg_icon = QtGui.QIcon(QtGui.QPixmap(":fg_playlist.png"))
        self.__bg_icon = QtGui.QIcon(QtGui.QPixmap(":bg_playlist.png"))
        self.__off_icon = QtGui.QIcon(QtGui.QPixmap(":off_playlist.png"))
        self.__session_api = rpa.session_api
        self.__pl_ids = []
        self.__pl_id_to_name = {}
        self.update_playlists()

    def flags(self, index):
        drag_drop_flags = QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        if not index.isValid():
            return QtCore.Qt.NoItemFlags | QtCore.Qt.ItemIsDropEnabled
        return super().flags(index) | QtCore.Qt.ItemIsEditable \
            | QtCore.Qt.ItemIsEnabled | drag_drop_flags

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.__pl_ids)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        pl_id = self.__pl_ids[index.row()]
        pl_name = self.__pl_id_to_name.get(pl_id)
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            return pl_name

        elif role == QtCore.Qt.DecorationRole:
            if self.__session_api.get_bg_playlist() is not None:
                if pl_id == self.__session_api.get_fg_playlist():
                    return self.__fg_icon
                if pl_id == self.__session_api.get_bg_playlist():
                    return self.__bg_icon
                return self.__off_icon
            else:
                if pl_id == self.__session_api.get_fg_playlist():
                    return self.__reg_icon
                return self.__off_icon

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        pl_id = self.__pl_ids[index.row()]
        pl_name = self.__pl_id_to_name.get(pl_id)
        if role == QtCore.Qt.EditRole and pl_name != value:
            pl_name = value
            self.dataChanged.emit(index, index, [role])
            self.__session_api.set_playlist_name(pl_id, pl_name)
            return True
        return False

    def update_playlists(self):
        self.beginResetModel()
        self.__pl_ids.clear()
        self.__pl_id_to_name.clear()
        pl_ids = self.__session_api.get_playlists()
        for pl_id in pl_ids:
            pl_name = self.__session_api.get_playlist_name(pl_id)
            self.__pl_ids.append(pl_id)
            self.__pl_id_to_name[pl_id] = pl_name
        self.endResetModel()

    def update_playlist_name(self, pl_id):
        name = self.__session_api.get_playlist_name(pl_id)
        if self.__pl_id_to_name.get(pl_id) is None: return
        self.__pl_id_to_name[pl_id] = name
        index = self.__pl_ids.index(pl_id)
        self.dataChanged.emit(index, index)

    @property
    def playlist_ids(self):
        return self.__pl_ids

    def get_fg_index(self):
        fg_playlist = self.__session_api.get_fg_playlist()
        if fg_playlist not in self.__pl_ids:
            return 0
        return self.__pl_ids.index(
            self.__session_api.get_fg_playlist())

    def get_bg_index(self):
        bg = self.__session_api.get_bg_playlist()
        if bg is None:
            return None
        return self.__pl_ids.index(
            self.__session_api.get_bg_playlist())

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def mimeTypes(self):
        return ["rpa/playlists", "rpa/clips"]

    def mimeData(self, indexes):
        mime_data = QtCore.QMimeData()
        ba = QtCore.QByteArray()
        mime_data.setData("rpa/playlists", ba)
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        drop_index = None
        if data.hasFormat("rpa/clips"):
            drop_index = parent.row()
            serialized = data.data("rpa/clips")
            clip_ids = json.loads(bytes(serialized).decode("utf-8"))

            if drop_index is None:
                return False
            else:
                self.SIG_ADD_CLIPS.emit(drop_index, clip_ids)
                return True

        elif data.hasFormat("rpa/playlists"):
            drop_index = parent.row()
            if drop_index == -1 and row != -1:
                drop_index = row

            if drop_index is None:
                return False
            else:
                self.SIG_MOVE.emit(drop_index)
                return True

        return False
