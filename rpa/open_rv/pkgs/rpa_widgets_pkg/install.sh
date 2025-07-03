#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJ_DIR="$(dirname $(dirname $(dirname $SCRIPT_DIR)))"
RPA_OPEN_RV="$PROJ_DIR/open_rv/rpa_core/"

$RV_HOME/bin/rvpkg -uninstall $RV_SUPPORT_PATH/Packages/rpa_widgets-1.0.rvpkg
$RV_HOME/bin/rvpkg -remove $RV_SUPPORT_PATH/Packages/rpa_widgets-1.0.rvpkg

cd $SCRIPT_DIR
zip -jr ./rpa_widgets-1.0.rvpkg ./PACKAGE ./rpa_widgets_mode.py

$RV_HOME/bin/rvpkg -add $RV_SUPPORT_PATH rpa_widgets-1.0.rvpkg
rm ./rpa_widgets-1.0.rvpkg
$RV_HOME/bin/rvpkg -install $RV_SUPPORT_PATH/Packages/rpa_widgets-1.0.rvpkg
$RV_HOME/bin/rvpkg -optin $RV_SUPPORT_PATH/Packages/rpa_widgets-1.0.rvpkg
cd $PROJ_DIR

# # $RV_HOME/bin/rvpkg -list
