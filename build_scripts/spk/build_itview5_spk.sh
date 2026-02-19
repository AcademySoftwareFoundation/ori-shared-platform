#!/bin/bash
spk_info=$(spk info 2>&1)

search_string="No current spfs runtime environment"
if [[ "$spk_info" == *"$search_string"* ]]; then

    spk rm -y rpa
    spk rm -y itview5

    SCRIPT_DIR="$(dirname "$(realpath "$0")")"
    PROJ_DIR="$(dirname $(dirname $SCRIPT_DIR))"
    # RPA_DIR="$PROJ_DIR/rpa"

    if [[ $1 == "install" ]]; then
        export ITVIEW5_SPK_INSTALL=1
    fi

    spk build $SCRIPT_DIR/itview5.spk.yaml
    # spk build --solver-to-run resolvo $SCRIPT_DIR/itview5.spk.yaml
else
    echo "KINDLY EXIT FROM SPK-ENV BEFORE RUNNNIG THIS SCRIPT!!!"
fi
