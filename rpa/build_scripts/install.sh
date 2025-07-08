#!/bin/bash

# !!! REPLACE THE FOLLOWING VARIABLES WITH YOUR VALUES !!! 
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Replace RV_HOME with your actual OpenRV installation path
RV_HOME=/c/OpenRV_1.0/OpenRV_1.0
# Replace these with your actual rpa-wheel and rv-package names
RPA_WHL=rpa-0.2.4-py3-none-any.whl
RPA_CORE_PKG=rpa_core-1.0.rvpkg
RPA_WIDGETS_PKG=rpa_widgets-1.0.rvpkg
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if [ -z "$RV_HOME" ]; then
    echo "RV_HOME is not set. Please set it to your OpenRV installation path."    
    exit 1
fi
if [ -z "$RPA_WHL" ]; then
    echo "RPA_WHL is not set. Please set it to your RPA wheel file from build_scripts/output directory."
    exit 1
fi
if [ -z "$RPA_CORE_PKG" ]; then
    echo "RPA_CORE_PKG is not set. Please set it to your RPA core package file from build_scripts/output directory."
    exit 1
fi
if [ -z "$RPA_WIDGETS_PKG" ]; then
    echo "RPA_WIDGETS_PKG is not set. Please set it to your RPA widgets package file from build_scripts/output directory."
    exit 1
fi

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    echo "Running on Windows"
    RV_PYTHON="$RV_HOME/bin/python3.exe"
    RV_PKG="$RV_HOME/bin/rvpkg.exe"
else
    RV_PYTHON="$RV_HOME/bin/python3"
    RV_PKG="$RV_HOME/bin/rvpkg"
fi

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
$RV_PYTHON -m pip install --user $SCRIPT_DIR/output/$RPA_WHL --force-reinstall
$RV_PYTHON -m pip install --user -r $SCRIPT_DIR/requirements.txt

$RV_PKG -force -uninstall $RPA_CORE_PKG $RPA_WIDGETS_PKG
$RV_PKG -force -remove $RPA_CORE_PKG $RPA_WIDGETS_PKG
$RV_PKG -force -install -add $RV_HOME/plugins $SCRIPT_DIR/output/$RPA_CORE_PKG $SCRIPT_DIR/output/$RPA_WIDGETS_PKG
$RV_PKG -optin $RPA_CORE_PKG $RPA_WIDGETS_PKG
