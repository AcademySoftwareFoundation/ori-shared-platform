#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
export PROJ_DIR="$(dirname "$(dirname $SCRIPT_DIR)")"
$PROJ_DIR/open_rv/pkgs/rpa_core_pkg/build_pkg.sh
$PROJ_DIR/open_rv/pkgs/rpa_core_pkg/build_whl.sh
$PROJ_DIR/open_rv/pkgs/rpa_widgets_pkg/build_pkg.sh