#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
export PROJ_DIR="$(dirname $SCRIPT_DIR)"
export RV_SUPPORT_PATH=$PROJ_DIR/local_install/lib/open_rv
rm -rf $RV_SUPPORT_PATH
mkdir -p $RV_SUPPORT_PATH/Packages/
$PROJ_DIR/open_rv/pkgs/rpa_core_pkg/install.sh
$PROJ_DIR/open_rv/pkgs/rpa_widgets_pkg/install.sh
