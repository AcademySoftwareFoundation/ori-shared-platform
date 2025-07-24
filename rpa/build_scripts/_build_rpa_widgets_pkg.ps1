$OPEN_RV_RPA_PKG = Join-Path $env:PROJ_DIR 'open_rv\pkgs\rpa_widgets_pkg'

Push-Location $OPEN_RV_RPA_PKG

$mainFiles = @('PACKAGE', 'rpa_widgets_mode.py')
$files = @()
foreach ($f in $mainFiles) {
    $fullPath = Join-Path $OPEN_RV_RPA_PKG $f
    if (Test-Path $fullPath) { $files += $fullPath }
}

$zipPath = Join-Path $OPEN_RV_RPA_PKG 'rpa_widgets-1.0.zip'
$rvpkgPath = Join-Path $OPEN_RV_RPA_PKG 'rpa_widgets-1.0.rvpkg'
if ($files.Count -gt 0) {
    Compress-Archive -Path $files -DestinationPath $zipPath -Force
    Rename-Item $zipPath $rvpkgPath -Force
    Copy-Item $rvpkgPath "$env:PROJ_DIR\build_scripts\output\"
    Write-Host "*** Built rpa_widgets-1.0.rvpkg ***"
    Remove-Item $rvpkgPath
} else {
    Write-Host "No files found to package. Skipping archive creation."
}

Pop-Location