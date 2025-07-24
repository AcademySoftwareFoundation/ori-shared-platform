$OPEN_RV_RPA_PKG = Join-Path $env:PROJ_DIR 'open_rv\pkgs\rpa_core_pkg'
$OPEN_RV_RPA_CORE = Join-Path $env:PROJ_DIR 'open_rv\rpa_core'

Push-Location $OPEN_RV_RPA_PKG

$files = @()
$mainFiles = @('PACKAGE', 'rpa_core_mode.py')
foreach ($f in $mainFiles) {
    $fullPath = Join-Path $OPEN_RV_RPA_PKG $f
    if (Test-Path $fullPath) { $files += $fullPath }
}
$apiFiles = Get-ChildItem -Path "$OPEN_RV_RPA_CORE\api" -Recurse -Include *.mu,*.glsl,*.gto -File -ErrorAction SilentlyContinue
foreach ($f in $apiFiles) {
    if (Test-Path $f.FullName) { $files += $f.FullName }
}

$zipPath = Join-Path $OPEN_RV_RPA_PKG 'rpa_core-1.0.zip'
$rvpkgPath = Join-Path $OPEN_RV_RPA_PKG 'rpa_core-1.0.rvpkg'
if ($files.Count -gt 0) {
    Compress-Archive -Path $files -DestinationPath $zipPath -Force
    Rename-Item $zipPath $rvpkgPath -Force
    Copy-Item $rvpkgPath "$env:PROJ_DIR\build_scripts\output\"
    Write-Host "*** Built rpa_core-1.0.rvpkg  ***"
    Remove-Item $rvpkgPath
} else {
    Write-Host "No files found to package. Skipping archive creation."
}

Pop-Location