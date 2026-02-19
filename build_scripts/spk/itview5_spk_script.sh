#!/bin/bash

#install python dependencies from the spk build script for the
#different python interpreter used by the plugin under spfs
export PYTHONPATH=""
export RV_HOME=/spfs/lib/openrv
RV_PYTHON="$RV_HOME/bin/python3"

${RV_PYTHON} -m pip install playwright
${RV_PYTHON} -m pip install scipy==1.13.1
${RV_PYTHON} -m pip install OpenImageIO==3.0.4
${RV_PYTHON} -m pip install imageio==2.37.0

echo "SUCCESS: RV Python dependencies installed!"

SPK_PY_DIR=`python -BEs -c 'import site; print(site.getsitepackages()[0])'`
RV_PY_DIR=`${RV_PYTHON} -BEs -c 'import site; print(site.getsitepackages()[0])'`
PTH_FILE="$RV_PY_DIR/shared_libraries.pth"

# 2. Check if the source directory actually exists
if [ ! -d "$SPK_PY_DIR" ]; then
    echo "Error: Source directory not found at $SPK_PY_DIR"
    exit 1
fi

# 3. Check if the destination directory actually exists
if [ ! -d "$RV_PY_DIR" ]; then
    echo "Error: Destination directory not found at $RV_PY_DIR"
    exit 1
fi

# 4. Create the .pth file containing the source path
# We use 'tee' here so it works nicely with sudo if needed
echo "$SPK_PY_DIR" | tee "$PTH_FILE" > /dev/null

# 5. Verify the result
if [ -f "$PTH_FILE" ]; then
    echo "Success!"
    echo "Created linkage file: $PTH_FILE"
    echo "Content: $(cat $PTH_FILE)"
else
    echo "Failed to create the .pth file. Check your permissions."
fi


if [ "$ITVIEW5_SPK_INSTALL" == "1" ]; then

    RV_PYTHON="$RV_HOME/bin/python3"

    for PY_DIR in $RV_PY_DIR $SPK_PY_DIR; do
        rm -rf $PY_DIR/rpa
        mkdir -p $PY_DIR/rpa/
        rsync -av --exclude='./.*' ./rpa/* $PY_DIR/rpa/
        echo "SUCCESS: RPA synced to $PY_DIR!"

        rm -rf $PY_DIR/itview
        mkdir -p $PY_DIR/itview
        rsync -av --exclude='./itview/.*' ./itview/* $PY_DIR/itview/
        echo "SUCCESS: itview synced to $PY_DIR!"

        rm -rf $PY_DIR/spi_itview
        mkdir -p $PY_DIR/spi_itview
        rsync -av --exclude='./spi_itview/.*' ./spi_itview/* $PY_DIR/spi_itview/
        echo "SUCCESS: spi_itview synced to $PY_DIR!"

        rm -rf $PY_DIR/itview5_plugins
        mkdir -p $PY_DIR/itview5_plugins
        rsync -av --exclude='./itview5_plugins/.*' ./itview5_plugins/* $PY_DIR/itview5_plugins/
        echo "SUCCESS: itview5_plugins synced to $PY_DIR!"
    done

    export ITVIEW_RV_SUPPORT_PATH=$RV_HOME/itview
    rm -rf $ITVIEW_RV_SUPPORT_PATH
    mkdir -p $ITVIEW_RV_SUPPORT_PATH/Packages/

    export RV_SUPPORT_PATH=$RV_HOME/rpa
    rm -rf $RV_SUPPORT_PATH
    mkdir -p $RV_SUPPORT_PATH/Packages/
    ./rpa/build_scripts_spi/_install_rpa_core_pkg.sh
    echo "SUCCESS: RPA Core Package installed on RV!"

    export RV_SUPPORT_PATH=$RV_SUPPORT_PATH:$ITVIEW_RV_SUPPORT_PATH
    ./itview/core/open_rv/install.sh

    cp ./itview/itview /spfs/bin/open_itview5
    cp ./spi_itview/itview /spfs/bin/itview5

fi
