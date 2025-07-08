#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
export PROJ_DIR="$(dirname $SCRIPT_DIR)"
mkdir -p $PROJ_DIR/build_scripts/output
rm -rf $PROJ_DIR/build_scripts/output/*
$SCRIPT_DIR/_build_rpa_whl.sh
$SCRIPT_DIR/_build_rpa_core_pkg.sh
$SCRIPT_DIR/_build_rpa_widgets_pkg.sh
