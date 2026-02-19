#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJ_DIR="$(dirname $SCRIPT_DIR)"

RV_PKG=$RV_HOME/bin/rvpkg

$RV_PKG -uninstall $RV_SUPPORT_PATH/Packages/node_graph_editor-1.0.rvpkg
$RV_PKG -remove $RV_SUPPORT_PATH/Packages/node_graph_editor-1.0.rvpkg

PKG_ROOT="$PROJ_DIR/open_rv/pkgs/node_graph_editor"
PKG_MODULES="$PKG_ROOT/node_graph_editor"

cp -rf $PKG_MODULES $RV_SUPPORT_PATH/Python/

zip -jr ./node_graph_editor-1.0.rvpkg $PKG_ROOT/PACKAGE $PKG_ROOT/node_graph_editor_mode.py

$RV_PKG -add $RV_SUPPORT_PATH node_graph_editor-1.0.rvpkg
rm ./node_graph_editor-1.0.rvpkg
$RV_PKG -install $RV_SUPPORT_PATH/Packages/node_graph_editor-1.0.rvpkg
$RV_PKG -optin $RV_SUPPORT_PATH/Packages/node_graph_editor-1.0.rvpkg


# $RV_HOME/bin/rvpkg -list
