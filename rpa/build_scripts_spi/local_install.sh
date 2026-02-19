#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
export PROJ_DIR="$(dirname $SCRIPT_DIR)"
export RV_SUPPORT_PATH=$PROJ_DIR/local_install/lib/open_rv
rm -rf $RV_SUPPORT_PATH
mkdir -p $RV_SUPPORT_PATH/Packages/
$SCRIPT_DIR/_install_rpa_core_pkg.sh
$SCRIPT_DIR/_install_rpa_widgets_pkg.sh
$SCRIPT_DIR/_install_node_graph_editor.sh
