#!/bin/bash

$RV_HOME/bin/rvpkg -uninstall $ITVIEW_RV_SUPPORT_PATH/Packages/itview-1.0.rvpkg
$RV_HOME/bin/rvpkg -remove $ITVIEW_RV_SUPPORT_PATH/Packages/itview-1.0.rvpkg

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJ_DIR="$(dirname $(dirname $(dirname $(dirname $SCRIPT_DIR))))"
cd $SCRIPT_DIR
zip -jr ./itview-1.0.rvpkg ./PACKAGE ./itview_mode.py

$RV_HOME/bin/rvpkg -add $ITVIEW_RV_SUPPORT_PATH itview-1.0.rvpkg
rm ./itview-1.0.rvpkg

$RV_HOME/bin/rvpkg -install $ITVIEW_RV_SUPPORT_PATH/Packages/itview-1.0.rvpkg
$RV_HOME/bin/rvpkg -optin $ITVIEW_RV_SUPPORT_PATH/Packages/itview-1.0.rvpkg

cd $PROJ_DIR

# # $RV_HOME/bin/rvpkg -list
