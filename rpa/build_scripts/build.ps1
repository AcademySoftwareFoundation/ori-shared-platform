$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PROJ_DIR = Split-Path $ScriptDir -Parent
$env:PROJ_DIR = $PROJ_DIR

$outputDir = Join-Path $PROJ_DIR 'build_scripts\output'
if (!(Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir | Out-Null }
Remove-Item "$outputDir\*" -Recurse -Force -ErrorAction SilentlyContinue

& "$ScriptDir\_build_rpa_whl.ps1"
& "$ScriptDir\_build_rpa_core_pkg.ps1"
& "$ScriptDir\_build_rpa_widgets_pkg.ps1"