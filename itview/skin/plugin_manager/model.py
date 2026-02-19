""" All datastructures needed by Plugin Manager is contained in this module.
"""
from typing import Union
from enum import Enum, auto
from dataclasses import dataclass
from PySide2 import QtCore


@dataclass
class ConfigPath:
    """Container for plugin paths config file label and path"""
    label:str
    path:str


class PluginMdataAttrName(Enum):
    """Enmeration of Metadata attribute names"""
    PLUGIN_NAME = "plugin_name"
    DESCRIPTION = "description"
    AUTHOR_EMAIL = "author_email"
    ITVIEW_VERSION = "itview_version"
    CLASS_NAME = "class_name"


@dataclass
class PluginData:
    """As read from sources Plugin data held here as soon."""
    plugin_path:str
    label:str
    plugin: object
    mdata: dict


class PluginHeaderIndex(Enum):
    """Enumeration of the ordering of PluginHeaders"""
    NAME = 0
    LABEL = auto()
    PATH = auto()
    DESCRIPTION = auto()
    AUTHOR_EMAIL = auto()
    ITVIEW_VERSION = auto()


class PluginsHeader:
    """Hold headers under which plugins data is organized"""
    def __init__(self):
        self.__index_to_header = {}
        self.__header_to_index = {}

    def set_value(self, index:PluginHeaderIndex, header:str):
        """Set the value of the given index"""
        self.__index_to_header[index] = header
        self.__header_to_index[header] = index

    def get_value(self, index:PluginHeaderIndex):
        """Get value of the given index"""
        return self.__index_to_header.get(index)

    def get_index(self, header:str):
        """Set the index based on given value"""
        return self.__header_to_index.get(header)


class PluginRow(QtCore.QObject):
    """Plugin data that needs to be shown by Plugin Mngr is held here."""
    SIG_VALUE_CHANGED = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.__data = {}

    def set_value(self, key:PluginHeaderIndex, data):
        """Given value assigned to given PluginHeaderIndex"""
        self.__data[key] = data
        self.SIG_VALUE_CHANGED.emit()

    def get_value(self, key:PluginHeaderIndex):
        """Get value assigned to given PluginHeaderIndex"""
        return self.__data.get(key)

    def clear(self):
        """Clear all data"""
        self.__data.clear()


class PluginsModel(QtCore.QAbstractTableModel):
    """
    Holds PluginRows which in turn respectively hold plugin values and also
    ActionRows. The following is the design of the data-struture,

    PluginsModel
    |-----> PluginRow1
            |-----> Value1
            |-----> Value2
    |-----> PluginRow2
            |-----> Value1
            |-----> Value2
    |-----> PluginRow2
            |-----> Value1
            |-----> Value2
    """
    def __init__(self, plugins_header):
        super().__init__()
        self.__header = plugins_header
        self.__rows = []
        self.__proxy_model = None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        """
        Overwrite parent's headerData method to show plugin header names
        that has been set by the controller.
        """
        if orientation == QtCore.Qt.Horizontal and \
            role == QtCore.Qt.DisplayRole:
            return self.__header.get_value(PluginHeaderIndex(section))
        return None

    def data(self, index, role=None):
        """
        Based on given index, get the PluginRow and then get it's value using
        the PluginHeaderIndex cretaed using the column index.
        """
        role = QtCore.Qt.DisplayRole if role is None else role
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole:
            row = self.__rows[index.row()]
            return str(row.get_value(PluginHeaderIndex(index.column())))
        return None

    def rowCount(self, index=None): #pylint: disable=W0613
        """Return number of plugin rows."""
        return len(self.__rows)

    def columnCount(self, index=None): #pylint: disable=W0613
        """Return number of plugin columns."""
        return len(PluginHeaderIndex)

    def add_row(self, row:PluginRow):
        """
        Add an PluginRow to the PluginsModel.
        All hotkeys and custom-hotkeys are respectively registered to
        help with making sure all the hotkeys are unique.
        """
        self.__rows.append(row)
        row.SIG_VALUE_CHANGED.connect(self.__value_changed)

    def __value_changed(self):
        start_index = self.index(0, 0)
        end_index = self.index(self.rowCount(), self.columnCount())
        self.dataChanged.emit(start_index, end_index)

    def get_row(self, row_index:int)->Union[PluginRow, None]:
        """Return the PluginRow with the given row-index."""
        return self.__rows[row_index]

    def get_proxy_model(self):
        """
        Return the proxy model that wraps around the original plugins model.
        We need this to power our views, so that even when we sort/filter the
        data shown in the view, the original indexes of the plugins model
        remains unchanged.
        """
        if self.__proxy_model is None:
            self.__proxy_model = QtCore.QSortFilterProxyModel(self)
            self.__proxy_model.setFilterCaseSensitivity(
                QtCore.Qt.CaseInsensitive)
            self.__proxy_model.setFilterKeyColumn(-1)
            self.__proxy_model.setSourceModel(self)
            for index in PluginHeaderIndex:
                self.__proxy_model.setHeaderData(
                    index.value, QtCore.Qt.Horizontal,
                    self.__header.get_value(index), QtCore.Qt.DisplayRole)
            self.__proxy_model.setSortCaseSensitivity(
                QtCore.Qt.CaseInsensitive)
            self.__proxy_model.sort(1, QtCore.Qt.AscendingOrder)

        return self.__proxy_model

    def filter_plugin_rows(self, filter_text:str):
        """Filter the plugins row list based on the given filter text."""
        self.__proxy_model.setFilterFixedString(filter_text)

    def proxy_row_index_to_row_index(self, proxy_row_index:int)->int:
        """
        Return the original plugin row index on the PluginsModel from the
        proxy plugin row index given.
        """
        proxy_model = self.get_proxy_model()
        model_index = proxy_model.mapToSource(
            proxy_model.index(proxy_row_index, 0))
        return model_index.row()

    def clear(self):
        """Clear all data.
        """
        for row in self.__rows:
            row.clear()
        self.__rows.clear()


class Model(QtCore.QObject):
    """
    Main Model interface through which all the data models needed by
    the Plugin Mngr can be accessed.
    """
    def __init__(self):
        self.__plugins_header = PluginsHeader()
        self.__plugins_model = PluginsModel(self.__plugins_header)

        self.__copyable_plugin_cols = {}
        for index in PluginHeaderIndex:
            self.__copyable_plugin_cols[index.value] = False

    @property
    def plugins_header(self):
        """Returns headers under which Plugins data is organized."""
        return self.__plugins_header

    @property
    def plugins_model(self)->PluginsModel:
        """Get the data model that holds all the plugins data."""
        return self.__plugins_model

    @property
    def default_copyable_column_index(self):
        """
        Return the column index of the column whose value should be copied
        if the user has not made a choice and the copy action is used.
        """
        return PluginHeaderIndex.PATH

    def make_column_copyable(
        self, header_index:PluginHeaderIndex, is_copyable:bool):
        """
        Set column with the given PluginHeaderIndex to be copyable when
        the copy action is used.
        """
        self.__copyable_plugin_cols[header_index] = is_copyable

    def get_copyable_column_indexes(self)->list:
        """
        Return the list of the column indexes of the columns whose values
        should be copied.
        """
        out = []
        for index in PluginHeaderIndex:
            if self.__copyable_plugin_cols.get(index, False):
                out.append(index.value)
        return out
