"""Logical controller of Plugin Manager"""
import sys
import os
import json
import importlib
import argparse
from importlib.abc import MetaPathFinder
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union, Any
from PySide2 import QtCore, QtWidgets
from itview.skin.main_window import MainWindow
from itview.skin.viewport_user_input_tx import ViewportUserInputTx
from itview.skin.widgets.itv_dock_widget import ItvDockWidget
from itview.skin.plugin_manager.model import Model, ConfigPath, \
    PluginRow, PluginHeaderIndex, PluginMdataAttrName, PluginData
from itview.skin.plugin_manager.view import View
from itview.skin.dbid_mapper import DbidMapper
from rpa.rpa import Rpa
from unittest.mock import Mock



class ImportPathEnforcer(MetaPathFinder):
    MODULE_NAME_TO_PATH = {}

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.MODULE_NAME_TO_PATH:
            return importlib.util.spec_from_file_location(
                fullname, self.MODULE_NAME_TO_PATH[fullname])
        return None

# Insert our custom finder at the start
sys.meta_path.insert(0, ImportPathEnforcer())


class Controller(QtCore.QObject):
    """ Controller of Plugin Manager
    """

    def __init__(
        self, main_window, config_paths:List[ConfigPath], logger_api):
        super().__init__()
        self.__main_window = main_window
        self.__logger_api = logger_api
        self.__plugin_instances = []
        self.__cmd_line_args = None
        self.__rpa = None
        self.__dbid_mapper = None
        self.__viewport_user_input = None
        self.__cmd_line_arg_parser = argparse.ArgumentParser(
            prog="itview5",
            description="Itview5 command line arguments")

        self.__setup_model(config_paths)

    def init(self, rpa, dbid_mapper, viewport_user_input):
        self.__rpa = rpa
        self.__dbid_mapper = dbid_mapper
        self.__viewport_user_input = viewport_user_input
        self.__dock_widget = None
        self.__copyable_column_indexes_key = \
            "plugin_mngr/copyable_cols"

        self.__itview = ItviewPluginParams(
            self.__rpa, self.__dbid_mapper, self.__main_window,
            self.__cmd_line_args,  self.__viewport_user_input, self)

        self.__inject_itview_into_all_plugins()
        self.__setup_view()

    def __setup_model(self, config_paths:List[ConfigPath]):
        self.__model = Model()
        self.__set_plugin_headers()
        self.__all_plugin_data = []
        for config_path in config_paths:
            self.__all_plugin_data.extend(
                self.__get_all_plugin_data(config_path))
        # self.__cmd_line_args = self.__cmd_line_arg_parser.parse_args()

    def __inject_itview_into_all_plugins(self):
        for plugin_data in self.__all_plugin_data:
            if not self.__inject_itview_into_plugin(plugin_data.plugin):
                self.__logger_api.info(
                    f"Cannot load plugin as Itview cannot be"\
                    f" injected into it, {plugin_data.plugin_path}")
                return None
            if type(plugin_data.plugin) is QtCore.QObject: #pylint: disable=C0123
                plugin_data.plugin.setParent(self.__main_window)

            plugin_row = self.__create_plugin_row(plugin_data)
            if plugin_row:
                self.__model.plugins_model.add_row(plugin_row)

        copyable_column_indexes = self.__read_copyable_column_indexes()
        if not copyable_column_indexes:
            self.__model.make_column_copyable(
                self.__model.default_copyable_column_index, True)
        else:
            for column in copyable_column_indexes:
                self.__model.make_column_copyable(
                    PluginHeaderIndex(int(column)), True)

    def __setup_view(self):
        self.__view = View()
        self.__view.set_plugins_table_model(
            self.__model.plugins_model.get_proxy_model())

        plugins_copyable_col_names =\
            [self.__model.plugins_header.get_value(PluginHeaderIndex(column))
                for column in self.__read_copyable_column_indexes()]
        headers = [self.__model.plugins_header.get_value(index)
            for index in PluginHeaderIndex]
        self.__view.create_plugins_context_menu(
            headers, plugins_copyable_col_names)

        self.__view.SIG_SEARCH_TXT_CHANGED.connect(
            self.__model.plugins_model.filter_plugin_rows)
        self.__view.SIG_COPY_TO_CLIPBOARD.connect(
            self.__copy_to_clipboard)
        self.__view.SIG_MAKE_COLUMN_COPYABLE.connect(
            self.__make_column_copyable)

        self.__dock_widget = ItvDockWidget(
            "Plugins Manager", self.__main_window)
        self.__dock_widget.setWidget(self.__view)
        self.__dock_widget.visibilityChanged.connect(
            self.__add_remove_copy_action)

        self.__toggle_action = self.__dock_widget.toggleViewAction()
        plugins_menu = self.__main_window.get_plugins_menu()
        plugins_menu.addAction(self.__toggle_action)

        self.__main_window.addDockWidget(
            QtCore.Qt.TopDockWidgetArea, self.__dock_widget)
        self.__main_window.addAction(self.__view.get_plugins_copy_action())
        self.__dock_widget.hide()


    def __get_all_plugin_data(self, config_path:ConfigPath)->list:
        all_plugin_data = []
        if not os.path.isfile(config_path.path):
            self.__logger_api.info(
                f"Following config file to get the plugin paths "
                f"doesn't not exist! {config_path.path}")
            return all_plugin_data
        plugin_paths = self.__get_plugin_paths(config_path.path)
        if len(plugin_paths) == 0:
            self.__logger_api.info(
                f"No plugin paths to load from, {config_path.path}")
            return all_plugin_data

        for plugin_path in plugin_paths:
            plugin_path = plugin_path.rstrip(os.sep)
            plugin_data = \
                self.__load_plugin_data(config_path.label, plugin_path)
            if plugin_data is None: continue
            all_plugin_data.append(plugin_data)
        return all_plugin_data

    def __create_plugin_row(self, plugin_data:PluginData)->PluginRow:
        plugin_row = PluginRow()
        plugin_row.set_value(
            PluginHeaderIndex.NAME,
            plugin_data.mdata.get(PluginMdataAttrName.PLUGIN_NAME.value))
        plugin_row.set_value(
            PluginHeaderIndex.LABEL, plugin_data.label)
        plugin_row.set_value(
            PluginHeaderIndex.PATH, plugin_data.plugin_path)
        plugin_row.set_value(
            PluginHeaderIndex.DESCRIPTION,
            plugin_data.mdata.get(PluginMdataAttrName.DESCRIPTION.value))
        plugin_row.set_value(
            PluginHeaderIndex.AUTHOR_EMAIL,
            plugin_data.mdata.get(PluginMdataAttrName.AUTHOR_EMAIL.value))
        plugin_row.set_value(
            PluginHeaderIndex.ITVIEW_VERSION, plugin_data.mdata.get(
                PluginMdataAttrName.ITVIEW_VERSION.value))

        return plugin_row

    def __get_plugin_paths(self, config_path:str):
        abs_plugin_paths = []
        try:
            with open(config_path, "r", encoding="utf-8") as file_:
                try:
                    config_dir = os.path.abspath(os.path.dirname(config_path))
                    plugin_paths = self.__read_plugin_paths(config_path)
                    for path in plugin_paths:
                        plugin_module_name = os.path.basename(path)
                        if plugin_module_name in ImportPathEnforcer.MODULE_NAME_TO_PATH:
                            continue
                        if os.path.isabs(path): abs_plugin_path = path
                        else: abs_plugin_path = os.path.join(config_dir, path)
                        abs_plugin_paths.append(abs_plugin_path)
                        ImportPathEnforcer.MODULE_NAME_TO_PATH[
                            plugin_module_name] = os.path.join(abs_plugin_path, "__init__.py")
                except Exception as exception:
                    self.__logger_api.warning(exception)
        except FileNotFoundError as exception:
            self.__logger_api.warning(exception)
        return abs_plugin_paths

    def __does_plugin_folder_path_exist(self, plugin_path:str)->bool:
        if not os.path.exists(plugin_path):
            self.__logger_api.info(
                f"Plugin folder path doesn't exist, {plugin_path}")
            return False
        return True

    def __does_mdata_file_exist(self, mdata_file_path)->bool:
        if not os.path.isfile(mdata_file_path):
            self.__logger_api.info(
                f"Plugin metadata file doesn't exist, {mdata_file_path}")
            return False
        return True

    def __get_mdata(self, mdata_file_path:str)->dict:
        out = {}
        try:
            with open(mdata_file_path, "r", encoding="utf-8") as file:
                out = json.load(file)
        except json.decoder.JSONDecodeError as exception:
            self.__logger_api.warning(exception)

        return out

    def __are_mdata_attrs_valid(self, mdata:dict)->bool:
        out = True
        for attr_name in PluginMdataAttrName:
            attr_value = mdata.get(attr_name.value)
            if attr_value is None:
                self.__logger_api.warning(f"Attribute {attr_value} not found!")
                out = False
                break
        return out

    def __does_plugin_file_exist(self, plugin_file_path:str)->bool:
        if not os.path.isfile(plugin_file_path):
            self.__logger_api.warning(
                f"Plugin file doesn't exist, {plugin_file_path}")
            return False
        return True

    def __get_cmd_line_args(self, plugin):
        if hasattr(plugin, "add_cmd_line_args"):
            plugin.add_cmd_line_args(self.__cmd_line_arg_parser)

    def __inject_itview_into_plugin(self, plugin)->bool:
        try:
            plugin.itview_init(self.__itview)
        except Exception as e:
            self.__logger_api.warning(e)
            import traceback
            traceback.print_exc()
            return False
        return True

    def get_settings_widget(self, plugin)->Union[QtWidgets.QWidget, None]:
        """Get settings widget of given plugin if it's available"""
        try:
            settings_widget = plugin.itview_settings_widget()
        except AttributeError as e:
            self.__logger_api.info(e)
            return None
        if isinstance(settings_widget, QtWidgets.QWidget):
            return settings_widget
        return None

    def __get_valid_mdata(self, plugin_path:str, plugin_name)->dict:
        if not self.__does_plugin_folder_path_exist(plugin_path):
            return {}

        mdata_file_path = \
            os.path.join(os.sep, plugin_path, f"{plugin_name}.json")
        if not self.__does_mdata_file_exist(mdata_file_path):
            self.__logger_api.info(f"Cannot load plugin from {plugin_path}")
            return {}
        mdata = self.__get_mdata(mdata_file_path)
        if not mdata:
            self.__logger_api.warning(
            f"Metadata not valid in, {mdata_file_path}"
            f"So cannot load plugin from {plugin_path}")
            return {}
        if not self.__are_mdata_attrs_valid(mdata):
            self.__logger_api.warning(
                f"Attributes not valid in metadata file, {mdata_file_path} !"
                f"So cannot load plugin from {plugin_path}")
            return {}

        return mdata

    def __load_plugin_module(self, plugin_path:str, plugin_name:str):
        plugin_file_path = os.path.join(
            os.sep, plugin_path, f"{plugin_name}.py")
        if not self.__does_plugin_file_exist(plugin_file_path):
            return None
        plugin_path = Path(plugin_path)
        plugin_folder_path_parent = plugin_path.parent
        if str(plugin_folder_path_parent) not in sys.path:
            sys.path.append(str(plugin_folder_path_parent))
        plugin_module = \
            importlib.import_module(f"{plugin_name}.{plugin_name}")
        return plugin_module

    def __load_plugin_data(
        self, label:str, plugin_path:str)->Union[PluginData, None]:
        plugin_name = os.path.basename(plugin_path)
        mdata = self.__get_valid_mdata(plugin_path, plugin_name)
        if not mdata: return None

        plugin_module = self.__load_plugin_module(plugin_path, plugin_name)
        if plugin_module is None: return None
        class_name = mdata.get(PluginMdataAttrName.CLASS_NAME.value)
        if not hasattr(plugin_module, class_name):
            self.__logger_api.warning(
                f"Cannot load plugin from \"{plugin_path}\" !"
                f"As it does not have a class called, \"{class_name}\"!")
            return None

        plugin_class = getattr(plugin_module, mdata.get(
            PluginMdataAttrName.CLASS_NAME.value))
        plugin_instance = plugin_class()
        self.__plugin_instances.append(plugin_instance)

        self.__get_cmd_line_args(plugin_instance)
        return PluginData(plugin_path, label, plugin_instance, mdata)

    def __set_plugin_headers(self):
        self.__model.plugins_header.set_value(
            PluginHeaderIndex.NAME, "Name")
        self.__model.plugins_header.set_value(
            PluginHeaderIndex.LABEL, "Label")
        self.__model.plugins_header.set_value(
            PluginHeaderIndex.PATH, "Path")
        self.__model.plugins_header.set_value(
            PluginHeaderIndex.DESCRIPTION, "Description")
        self.__model.plugins_header.set_value(
            PluginHeaderIndex.AUTHOR_EMAIL, "Author")
        self.__model.plugins_header.set_value(
            PluginHeaderIndex.ITVIEW_VERSION, "Itview Version")

    def __copy_to_clipboard(self, proxy_plugin_row_indexes):
        text = ""
        copyable_column_indexes = self.__read_copyable_column_indexes()
        if proxy_plugin_row_indexes and copyable_column_indexes:
            for proxy_plugin_row_index in proxy_plugin_row_indexes:
                plugin_row_index = self.__model.plugins_model.\
                        proxy_row_index_to_row_index(proxy_plugin_row_index)
                for column_index in copyable_column_indexes:
                    header = self.__model.plugins_header.get_value(
                        PluginHeaderIndex(column_index))
                    text += f"{header}: "
                    plugin_row = \
                        self.__model.plugins_model.get_row(plugin_row_index)
                    text += str(plugin_row.get_value(
                            PluginHeaderIndex(column_index)))
                    text += " | "
                text += "\n"
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(str(text))

    def __add_remove_copy_action(self, should_add:bool):
        if should_add:
            self.__main_window.addAction(
                self.__view.get_plugins_copy_action())
        else:
            self.__main_window.removeAction(
                self.__view.get_plugins_copy_action())

    def __make_column_copyable(self, header:str, is_copyable:bool):
        header_index = self.__model.plugins_header.get_index(header)
        self.__model.make_column_copyable(header_index, is_copyable)
        if len(self.__read_copyable_column_indexes()) == 0:
            header_name = self.__model.plugins_header.get_value(
                self.__model.default_copyable_column_index)
            self.__view.make_column_copyable(header_name)
        self.__write_copyable_column_indexes(
            self.__model.get_copyable_column_indexes())

    def __read_plugin_paths(self, cfg_path):
        plugin_paths = []

        with open(cfg_path, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip empty or commented lines
                if not line or line.startswith("#"):
                    continue

                # Remove trailing comma if present
                path = line.rstrip(",")
                plugin_paths.append(path)

        return plugin_paths

    def __write_copyable_column_indexes(self, copyable_plugin_col_indexes):
        """
        Get the current list of copyable plugin column indexes and write it to
        config file on disk.
        """
        self.__rpa.config_api.setValue(
            self.__copyable_column_indexes_key,
            json.dumps(copyable_plugin_col_indexes))

    def __read_copyable_column_indexes(self)->list:
        """
        Read from config file and return the list of plugin columns that the
        user has opted to be copied when the copy action is used.
        """
        copyable_cols = self.__rpa.config_api.value(
            self.__copyable_column_indexes_key)

        return [] if copyable_cols is None else json.loads(copyable_cols)

@dataclass
class ItviewPluginParams:
    rpa: Rpa
    dbid_mapper: DbidMapper
    main_window: MainWindow
    cmd_line_args: argparse.Namespace
    viewport_user_input: ViewportUserInputTx
    plugin_manager_controller: Controller
