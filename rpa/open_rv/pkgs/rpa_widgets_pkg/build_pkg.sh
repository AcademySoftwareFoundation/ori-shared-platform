#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
cd $SCRIPT_DIR
zip -jr ./rpa_widgets-1.0.rvpkg ./PACKAGE ./rpa_widgets_mode.py

cp ./rpa_widgets-1.0.rvpkg $PROJ_DIR/build_scripts/pkgs/
echo "*** Built rpa_widgets-1.0.rvpkg ***"
rm ./rpa_widgets-1.0.rvpkg

cd $PROJ_DIR
