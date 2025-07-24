# !!! REPLACE THE FOLLOWING VARIABLES WITH YOUR VALUES !!!
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Replace RV_HOME with your actual OpenRV installation path
$RV_HOME = "C:\OpenRV_1.0\OpenRV_1.0\"

# Set executables based on Windows environment
$RV_PYTHON_EXE = "$RV_HOME\bin\python3.exe"
$RV_PKG_EXE = "$RV_HOME\bin\rvpkg.exe"

# RV_PKG_PATH should point to a writable location where OpenRV will look for packages
$RV_PKG_PATH = "$RV_HOME\Plugins"

# RV_PYTHON_PATH should point to one of the python search path that is writable by this script
$RV_PYTHON_PATH = "$RV_HOME\lib"  

# Replace these with your actual rpa-wheel and rv-package names
$RPA_WHL = "rpa-0.2.4-py3-none-any.whl"
$RPA_CORE_PKG = "rpa_core-1.0.rvpkg"
$RPA_WIDGETS_PKG = "rpa_widgets-1.0.rvpkg"

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Validation checks
if ([string]::IsNullOrEmpty($RV_HOME)) {
    Write-Error "RV_HOME is not set. Please set it to your OpenRV installation path."
    exit 1
}

if ([string]::IsNullOrEmpty($RPA_WHL)) {
    Write-Error "RPA_WHL is not set. Please set it to your RPA wheel file from build_scripts/output directory."
    exit 1
}

if ([string]::IsNullOrEmpty($RPA_CORE_PKG)) {
    Write-Error "RPA_CORE_PKG is not set. Please set it to your RPA core package file from build_scripts/output directory."
    exit 1
}

if ([string]::IsNullOrEmpty($RPA_WIDGETS_PKG)) {
    Write-Error "RPA_WIDGETS_PKG is not set. Please set it to your RPA widgets package file from build_scripts/output directory."
    exit 1
}

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# Install RPA wheel package
Write-Host "Installing RPA wheel package..."
& $RV_PYTHON_EXE -m pip install --target $RV_PYTHON_PATH "$SCRIPT_DIR\output\$RPA_WHL" --force-reinstall --upgrade

# Install requirements
Write-Host "Installing requirements..."
& $RV_PYTHON_EXE -m pip install --target $RV_PYTHON_PATH -r "$SCRIPT_DIR\requirements.txt" --upgrade

# Uninstall existing packages
Write-Host "Uninstalling existing packages..."
& $RV_PKG_EXE -force -uninstall $RPA_CORE_PKG $RPA_WIDGETS_PKG

# Remove existing packages
Write-Host "Removing existing packages..."
& $RV_PKG_EXE -force -remove $RPA_CORE_PKG $RPA_WIDGETS_PKG

# Install new packages
Write-Host "Installing new packages..."
& $RV_PKG_EXE -force -install -add $RV_PKG_PATH "$SCRIPT_DIR\output\$RPA_CORE_PKG" "$SCRIPT_DIR\output\$RPA_WIDGETS_PKG"

# Opt-in to packages
Write-Host "Opting in to packages..."
& $RV_PKG_EXE -optin $RPA_CORE_PKG $RPA_WIDGETS_PKG

Write-Host "Installation completed successfully!"
