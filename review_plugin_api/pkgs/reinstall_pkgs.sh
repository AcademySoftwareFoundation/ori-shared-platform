#!/bin/bash

RV_HOME="/path/to/your/openrv/"
RV_PKG_BIN="$RV_HOME/bin/rvpkg"
RV_PYTHON_BIN="$RV_HOME/bin/python3"

# Create and install review_plugin_api pip modules
# ++++++++++++++++++++++++++++++++++++++++++
cd ../review_plugin_api/
TEMP_DIR=$(mktemp -d)
$RV_PYTHON_BIN setup.py sdist bdist_wheel --dist-dir "$TEMP_DIR"
cp "$TEMP_DIR/review_plugin_api-0.1-py3-none-any.whl" ../pkgs/
$RV_PYTHON_BIN -m pip install --user ../pkgs/review_plugin_api-0.1-py3-none-any.whl

# Install ReviewPluginApi Rv-Pkg
# ++++++++++++++++++++++++++++++
$RV_PKG_BIN -uninstall ~/.rv/Packages/review_plugin_api-0.1.rvpkg
$RV_PKG_BIN -remove ~/.rv/Packages/review_plugin_api-0.1.rvpkg

cd ../openrv/review_plugin_api
zip -jr ../../pkgs/review_plugin_api-0.1.rvpkg review_plugin_api_mode.py PACKAGE api/* connector/*

$RV_PKG_BIN -add ~/.rv/Packages ../../pkgs/review_plugin_api-0.1.rvpkg
$RV_PKG_BIN -install ~/.rv/Packages/review_plugin_api-0.1.rvpkg
$RV_PKG_BIN -optin ~/.rv/Packages/review_plugin_api-0.1.rvpkg

# Install Color-Corrector Rv-Pkg
# ++++++++++++++++++++++++++++++
$RV_PKG_BIN -uninstall ~/.rv/Packages/color_corrector-1.0.rvpkg
$RV_PKG_BIN -remove ~/.rv/Packages/color_corrector-1.0.rvpkg

cd ../color_corrector
zip -jr ../../pkgs/color_corrector-1.0.rvpkg ./*

$RV_PKG_BIN -add ~/.rv/Packages ../../pkgs/color_corrector-1.0.rvpkg
$RV_PKG_BIN -install ~/.rv/Packages/color_corrector-1.0.rvpkg
$RV_PKG_BIN -optin ~/.rv/Packages/color_corrector-1.0.rvpkg
