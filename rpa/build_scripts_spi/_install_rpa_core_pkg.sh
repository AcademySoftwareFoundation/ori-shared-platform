#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJ_DIR="$(dirname $SCRIPT_DIR)"

RV_PKG=$RV_HOME/bin/rvpkg

$RV_PKG -uninstall $RV_SUPPORT_PATH/Packages/rpa_core-1.0.rvpkg
$RV_PKG -remove $RV_SUPPORT_PATH/Packages/rpa_core-1.0.rvpkg

RPA_CORE="$PROJ_DIR/open_rv/rpa_core/"
RPA_CORE_PKG="$PROJ_DIR/open_rv/pkgs/rpa_core_pkg"

zip -jr ./rpa_core-1.0.rvpkg $RPA_CORE_PKG/PACKAGE $RPA_CORE_PKG/rpa_core_mode.py $RPA_CORE/api/*.mu $RPA_CORE/api/*.glsl $RPA_CORE/api/*.gto

$RV_PKG -add $RV_SUPPORT_PATH rpa_core-1.0.rvpkg
rm ./rpa_core-1.0.rvpkg
$RV_PKG -install $RV_SUPPORT_PATH/Packages/rpa_core-1.0.rvpkg
$RV_PKG -optin $RV_SUPPORT_PATH/Packages/rpa_core-1.0.rvpkg


# $RV_HOME/bin/rvpkg -list
