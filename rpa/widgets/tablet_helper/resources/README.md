# TabletHelper Resources

This directory contains the Qt resource file for TabletHelper icons.

## Compiling Resources

To compile the `resources.qrc` file into `resources.py`, use the Qt resource compiler:

### PySide2 (Qt5):
```bash
pyside2-rcc resources.qrc -o resources.py
```

### PySide6 (Qt6):
```bash
pyside6-rcc resources.qrc -o resources.py
```

Or using Python:
```bash
python -m PySide2.pyside2-rcc resources.qrc -o resources.py
python -m PySide6.pyside6-rcc resources.qrc -o resources.py
```

The `resources.py` file will be auto-generated and should be committed to version control.

## Resource Paths

Icons are accessed using the resource path format:
```
:icon-name.png
```

For example: `:applications-graphics.png`
