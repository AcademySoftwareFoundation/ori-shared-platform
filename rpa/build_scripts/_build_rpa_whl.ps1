$ErrorActionPreference = "Stop"

$INCLUDE_DIRS = @("api", "open_rv/rpa_core", "session_state", "utils", "widgets")
$PACKAGE_NAME = "rpa"

$TMPDIR = New-Item -ItemType Directory -Path ([System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString())
Copy-Item @("$env:PROJ_DIR\build_scripts\setup.py", "$env:PROJ_DIR\build_scripts\pyproject.toml") -Destination $TMPDIR.FullName

$PKGDIR = Join-Path $TMPDIR.FullName $PACKAGE_NAME
New-Item -ItemType Directory -Path $PKGDIR | Out-Null

Copy-Item "$env:PROJ_DIR\rpa.py", "$env:PROJ_DIR\delegate_mngr.py", "$env:PROJ_DIR\__init__.py" $PKGDIR

foreach ($SRC in $INCLUDE_DIRS) {
    $srcPath = Join-Path $env:PROJ_DIR $SRC
    $destPath = Join-Path $PKGDIR $SRC
    New-Item -ItemType Directory -Path $destPath -Force | Out-Null
    Get-ChildItem -Path $srcPath -Recurse -Include *.py | ForEach-Object {
        $targetDir = Join-Path $destPath ($_.FullName.Substring($srcPath.Length)).TrimStart('\')
        $targetDir = Split-Path $targetDir -Parent
        if (!(Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
        Copy-Item $_.FullName $targetDir
    }
}

# Add __init__.py recursively
Get-ChildItem -Path $PKGDIR -Directory -Recurse | ForEach-Object {
    $initFile = Join-Path $_.FullName "__init__.py"
    if (!(Test-Path $initFile)) { New-Item -ItemType File -Path $initFile | Out-Null }
}

Write-Host "Building wheel..."
Push-Location $TMPDIR.FullName
python setup.py bdist_wheel

$wheel = Get-ChildItem -Path "$TMPDIR\dist" -Filter *.whl -Recurse | Select-Object -First 1
if ($wheel) {
    Copy-Item $wheel.FullName "$env:PROJ_DIR\build_scripts\output\"
    Write-Host "✅ Wheel built: $($wheel.Name)"
} else {
    Write-Host "❌ Wheel build failed."
    exit 1
}
Pop-Location
Remove-Item $TMPDIR.FullName -Recurse -Force