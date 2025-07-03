#!/bin/bash

set -e

INCLUDE_DIRS=("api" "open_rv/rpa_core" "session_state" "utils" "widgets")
PACKAGE_NAME="rpa"

TMPDIR=$(mktemp -d)
cp "$PROJ_DIR/setup.py" "$PROJ_DIR/pyproject.toml" "$TMPDIR/"

PKGDIR="$TMPDIR/$PACKAGE_NAME"
mkdir -p "$PKGDIR"

cp "$PROJ_DIR/rpa.py" "$PROJ_DIR/delegate_mngr.py" "$PROJ_DIR/__init__.py" "$PKGDIR/"

for SRC in "${INCLUDE_DIRS[@]}"; do
    DEST="$PKGDIR/$SRC"
    mkdir -p "$DEST"
    rsync -av --include='*/' --include='*.py' --exclude='*' "$PROJ_DIR/$SRC/" "$DEST/"
done

# Add __init__.py recursively
find "$PKGDIR" -type d -exec touch {}/__init__.py \;

# Build the wheel
echo "Building wheel..."
cd "$TMPDIR"
python3 setup.py bdist_wheel

# Move built wheel back to original working directory
WHEEL_FILE=$(find dist -name "*.whl")
if [ -n "$WHEEL_FILE" ]; then
    mv "$WHEEL_FILE" "$PROJ_DIR/build_scripts/pkgs/"
    echo "✅ Wheel built: $(basename "$WHEEL_FILE")"
else
    echo "❌ Wheel build failed."
    exit 1
fi

# Cleanup
cd "$OLDPWD"
rm -rf "$TMPDIR"