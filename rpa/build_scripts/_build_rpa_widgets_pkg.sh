#!/bin/bash

OPEN_RV_RPA_PKG="$PROJ_DIR/open_rv/pkgs/rpa_widgets_pkg"

cd $OPEN_RV_RPA_PKG
zip -jr $OPEN_RV_RPA_PKG/rpa_widgets-1.0.rvpkg $OPEN_RV_RPA_PKG/PACKAGE $OPEN_RV_RPA_PKG/rpa_widgets_mode.py

cp $OPEN_RV_RPA_PKG/rpa_widgets-1.0.rvpkg $PROJ_DIR/build_scripts/output/
echo "*** Built rpa_widgets-1.0.rvpkg ***"
rm $OPEN_RV_RPA_PKG/rpa_widgets-1.0.rvpkg

cd $PROJ_DIR
