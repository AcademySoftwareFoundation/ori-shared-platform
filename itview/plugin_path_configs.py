"""
Paths of the configs that need to be parsed by plugin manager
is configured here.
"""

import os
from typing import List
from itview.skin.plugin_manager.model import ConfigPath


def get()->List[ConfigPath]:
    out = []

    config_name = "itview5_plugins.cfg"

    # Current Directory
    # Example: CURRENT_DIRECTORY/
    current_dir = os.getcwd()
    plugins_config_path = os.path.join(current_dir, config_name)
    if os.path.isfile(plugins_config_path):
        out.append(ConfigPath("Current Dir", plugins_config_path))

    # Home Directory
    # Example: /net/homedirs/USER/.itview/
    home_dir = os.path.expanduser("~")
    plugins_config_path = os.path.join(home_dir, ".itview", config_name)
    if os.path.isfile(plugins_config_path):
        out.append(ConfigPath("Home Dir", plugins_config_path))

    # Core Plugins
    plugins_config = os.environ.get("ITVIEW5_CORE_PLUGINS_CONFIG")
    if plugins_config:
        out.append(ConfigPath("Core", plugins_config))

    return out
