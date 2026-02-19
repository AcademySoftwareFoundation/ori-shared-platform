#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
export PROJ_DIR="$(dirname "$(dirname $SCRIPT_DIR)")/itview"
$PROJ_DIR/core/open_rv/build_pkg.sh
$PROJ_DIR/core/open_rv/build_whl.sh
