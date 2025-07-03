import json
from typing import Union

from PySide2 import QtCore, QtGui
import rpa.widgets.session_manager.clips_controller.view.resources.resources
from rpa.widgets.session_manager.clips_controller.view.thumbnail_loader import ThumbnailLoader


THUMBNAIL_WIDTH = 90
THUMBNAIL_HEIGHT = 44

class ProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def lessThan(self, left_model_index, right_model_index):
        try:
            out = left_model_index.data() > right_model_index.data()
        except TypeError:
            out = True
        return out


class DictList:
    def __init__(self, values:list):
        self.reset(values)

    def reset(self, values):
        self.__list = values[:]
        self.__dict = {id : index for index, id in \
            enumerate(self.__list)}

    def index(self, value):
        return self.__dict.get(value)

    def __getitem__(self, index):
        return self.__list[index]

    def __len__(self):
        return len(self.__list)


class Model(QtCore.QAbstractTableModel):

    SIG_MOVE = QtCore.Signal(int) # drop index

    def __init__(self, rpa, parent=None):
        super().__init__(parent)
        self.__session_api = rpa.session_api
        self.__playlist = None
        self.__proxy_model = None
        self.__thumbnail_loader = ThumbnailLoader()
        self.__clips = DictList([])
        self.__attrs = DictList(self.__session_api.get_attrs())
        self.__session_api.get_attrs()

        self.__editable_icon = QtGui.QIcon(QtGui.QPixmap(":editable32.png"))
        self.__curr_clip_icon = QtGui.QIcon(QtGui.QPixmap(":curclip.png"))
        self.__blank_icon = QtGui.QIcon(QtGui.QPixmap(":blank.png"))
        self.update_playlist()

    @property
    def attrs(self):
        return self.__attrs

    @property
    def clips(self):
        return self.__clips

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.__clips)

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self.__attrs)

    def flags(self, index):
        drag_drop_flags = QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
        attr_id = self.__attrs[index.column()]
        if not self.__session_api.is_attr_read_only(attr_id):
            return super().flags(index) | QtCore.Qt.ItemIsEditable | drag_drop_flags

        return super().flags(index) | drag_drop_flags

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            attr_id = self.__attrs[section]
            if role == QtCore.Qt.DisplayRole:
                return self.__session_api.get_attr_name(attr_id)
            if role == QtCore.Qt.DecorationRole and \
            not self.__session_api.is_attr_read_only(attr_id):
                return self.__editable_icon

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        attr = self.__attrs[index.column()]
        clip = self.__clips[index.row()]
        value = self.__session_api.get_attr_value(clip, attr)

        if attr == "thumbnail_url" and value != "Loading,...":
            def callback(thumbnail: Union[str, QtGui.QPixmap]):
                if not thumbnail:
                    return
                if type(thumbnail) is str:
                    self.dataChanged.emit(index, index, QtCore.Qt.DisplayRole)
                if type(thumbnail) is QtGui.QPixmap:
                    self.dataChanged.emit(index, index, QtCore.Qt.DecorationRole)
            thumbnail_pixmap = self.__thumbnail_loader.request_thumbnail(value, callback)
        else:
            thumbnail_pixmap = None

        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            if attr == "thumbnail_url":
                return "Loading..." if not thumbnail_pixmap else thumbnail_pixmap
            if self.__session_api.is_attr_keyable(attr):
                if value is None: value = {}
                else: value = str(value.get("key_values", {}))
            return value

        if role == QtCore.Qt.DecorationRole:
            if attr == "play_order":
                if self.__session_api.get_current_clip() == clip:
                    return self.__curr_clip_icon
                return self.__blank_icon

            if attr == "thumbnail_url" and type(thumbnail_pixmap) is QtGui.QPixmap:
                return thumbnail_pixmap.scaled(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, QtCore.Qt.KeepAspectRatio)

        if role == QtCore.Qt.ForegroundRole:
            if attr == "length_diff":
                if value > 0:
                    return QtGui.QColor(0, 255, 0)
                elif value < 0:
                    return QtGui.QColor(255, 0, 0)

        if role == QtCore.Qt.CheckStateRole and \
        self.__session_api.get_attr_data_type(attr) == "bool":
            return QtCore.Qt.Checked if value is True else QtCore.Qt.Unchecked

        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.DisplayRole:
            return False
        elif role == QtCore.Qt.EditRole:
            clip = self.__clips[index.row()]
            attr = self.__attrs[index.column()]
            attr_value = [(self.__playlist, clip, attr, value)]
            self.__session_api.set_attr_values(attr_value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def get_proxy_model(self):
        if self.__proxy_model is None:
            self.__proxy_model = ProxyModel(self.parent())
            self.__proxy_model.setSourceModel(self)
            self.__proxy_model.setFilterCaseSensitivity(
                QtCore.Qt.CaseInsensitive)
            self.__proxy_model.setFilterKeyColumn(-1)

            for i, attr in enumerate(self.__session_api.get_attrs()):
                name = self.__session_api.get_attr_name(attr)
                self.__proxy_model.setHeaderData(
                    i, QtCore.Qt.Horizontal, name, QtCore.Qt.DisplayRole)

            self.__proxy_model.setSortCaseSensitivity(
                QtCore.Qt.CaseInsensitive)
        return self.__proxy_model

    def get_attr_data_type(self, attr):
        return self.__session_api.get_attr_data_type(attr)

    def update_playlist(self):
        self.beginResetModel()
        self.__playlist = self.__session_api.get_fg_playlist()
        clips = self.__session_api.get_clips(self.__playlist)
        self.__clips.reset(clips)
        self.endResetModel()

    def update_current_clip_icon(self):
        play_order_column = self.__attrs.index("play_order")
        start_index = self.index(0, play_order_column)
        end_index = self.index(self.rowCount()-1, play_order_column)
        self.dataChanged.emit(
            start_index, end_index, [QtCore.Qt.DecorationRole])

    def update_attr_values(self, attr_values):
        for attr_value in attr_values:
            playlist, clip, attr, value = attr_value
            if self.__playlist == playlist:
                row = self.__clips.index(clip)
                if row is None:
                    return
                column = self.__attrs.index(attr)
                index = self.index(row, column)
                self.dataChanged.emit(index, index)

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction

    def mimeTypes(self):
        return ["rpa/clips"]

    def mimeData(self, indexes):
        row_set = set(index.row() for index in indexes if index.isValid())
        clip_ids = [self.__clips[row] for row in row_set]

        serialized = json.dumps(clip_ids).encode("utf-8")
        ba = QtCore.QByteArray(serialized)

        mime_data = QtCore.QMimeData()
        mime_data.setData("rpa/clips", ba)
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        drop_index = None
        if data.hasFormat("rpa/clips"):
            drop_index = parent.row()

        if drop_index is None:
            return False
        else:
            self.SIG_MOVE.emit(drop_index)
            return True

        return False
