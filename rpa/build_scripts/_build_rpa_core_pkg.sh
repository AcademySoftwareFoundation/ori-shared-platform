#!/bin/bash

OPEN_RV_RPA_PKG="$PROJ_DIR/open_rv/pkgs/rpa_core_pkg"
OPEN_RV_RPA_CORE="$PROJ_DIR/open_rv/rpa_core/"

cd $OPEN_RV_RPA_PKG
zip -jr $OPEN_RV_RPA_PKG/rpa_core-1.0.rvpkg $OPEN_RV_RPA_PKG/PACKAGE $OPEN_RV_RPA_PKG/rpa_core_mode.py $OPEN_RV_RPA_CORE/api/*.mu $OPEN_RV_RPA_CORE/api/*.glsl $OPEN_RV_RPA_CORE/api/*.gto

cp $OPEN_RV_RPA_PKG/rpa_core-1.0.rvpkg $PROJ_DIR/build_scripts/output/
echo "*** Built rpa_core-1.0.rvpkg  ***"
rm $OPEN_RV_RPA_PKG/rpa_core-1.0.rvpkg

cd $PROJ_DIR

# $RV_HOME/bin/rvpkg -list
