#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
cd $SCRIPT_DIR
zip -jr ./itview-1.0.rvpkg ./PACKAGE ./itview_mode.py

cp ./itview-1.0.rvpkg $PROJ_DIR/build_scripts/pkgs/
echo "*** Built itview-1.0.rvpkg  ***"
rm ./itview-1.0.rvpkg

cd $PROJ_DIR
