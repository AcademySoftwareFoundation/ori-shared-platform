#!/bin/bash

RPA_OPEN_RV="$PROJ_DIR/open_rv/rpa_core/"

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
cd $SCRIPT_DIR
zip -jr ./rpa_core-1.0.rvpkg ./PACKAGE ./rpa_core_mode.py $RPA_OPEN_RV/api/*.mu $RPA_OPEN_RV/api/*.glsl $RPA_OPEN_RV/api/*.gto

cp ./rpa_core-1.0.rvpkg $PROJ_DIR/build_scripts/pkgs/
echo "*** Built rpa_core-1.0.rvpkg  ***"
rm ./rpa_core-1.0.rvpkg

cd $PROJ_DIR

# $RV_HOME/bin/rvpkg -list
