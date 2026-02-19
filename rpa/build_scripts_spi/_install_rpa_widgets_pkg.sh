#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJ_DIR="$(dirname $SCRIPT_DIR)"

RV_PKG=$RV_HOME/bin/rvpkg

$RV_PKG -uninstall $RV_SUPPORT_PATH/Packages/rpa_widgets-1.0.rvpkg
$RV_PKG -remove $RV_SUPPORT_PATH/Packages/rpa_widgets-1.0.rvpkg

RPA_WIDGETS_PKG="$PROJ_DIR/open_rv/pkgs/rpa_widgets_pkg"

zip -jr ./rpa_widgets-1.0.rvpkg $RPA_WIDGETS_PKG/PACKAGE $RPA_WIDGETS_PKG/rpa_widgets_mode.py

$RV_PKG -add $RV_SUPPORT_PATH rpa_widgets-1.0.rvpkg
rm ./rpa_widgets-1.0.rvpkg
$RV_PKG -install $RV_SUPPORT_PATH/Packages/rpa_widgets-1.0.rvpkg
$RV_PKG -optin $RV_SUPPORT_PATH/Packages/rpa_widgets-1.0.rvpkg

# # $RV_HOME/bin/rvpkg -list
