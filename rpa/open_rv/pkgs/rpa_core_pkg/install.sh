#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJ_DIR="$(dirname $(dirname $(dirname $SCRIPT_DIR)))"
RPA_OPEN_RV="$PROJ_DIR/open_rv/rpa_core/"

$RV_HOME/bin/rvpkg -uninstall $RV_SUPPORT_PATH/Packages/rpa_core-1.0.rvpkg
$RV_HOME/bin/rvpkg -remove $RV_SUPPORT_PATH/Packages/rpa_core-1.0.rvpkg

cd $SCRIPT_DIR
zip -jr ./rpa_core-1.0.rvpkg ./PACKAGE ./rpa_core_mode.py $RPA_OPEN_RV/api/*.mu $RPA_OPEN_RV/api/*.glsl $RPA_OPEN_RV/api/*.gto

$RV_HOME/bin/rvpkg -add $RV_SUPPORT_PATH rpa_core-1.0.rvpkg
rm ./rpa_core-1.0.rvpkg
$RV_HOME/bin/rvpkg -install $RV_SUPPORT_PATH/Packages/rpa_core-1.0.rvpkg
$RV_HOME/bin/rvpkg -optin $RV_SUPPORT_PATH/Packages/rpa_core-1.0.rvpkg
cd $PROJ_DIR

# $RV_HOME/bin/rvpkg -list
