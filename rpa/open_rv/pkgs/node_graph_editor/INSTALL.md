# Installation Guide - Node Graph Editor

## Quick Install

### For OpenRV Users

1. **Copy the package to RV's packages directory:**

   **Windows:**
   ```powershell
   xcopy /E /I "rv_tools\node_graph_editor" "%APPDATA%\RV\packages\node_graph_editor"
   ```

   **macOS/Linux:**
   ```bash
   cp -r rv_tools/node_graph_editor ~/Library/Application\ Support/RV/packages/
   # or on Linux:
   cp -r rv_tools/node_graph_editor ~/.rv/packages/
   ```

2. **Restart RV**

3. **Access the tool:**
   - Go to **Tools > Node Graph Editor**

## Verification

To verify the package is loaded correctly:

1. Open RV
2. Open the RV Console (Help > Show Console)
3. Look for any error messages related to "node_graph_editor"
4. Check if "Tools > Node Graph Editor" appears in the menu

## Troubleshooting

### Package not appearing

If the package doesn't appear in the Tools menu:

1. **Check package location:**
   - Verify the `PACKAGE` file exists in the package directory
   - Ensure the directory structure is intact

2. **Check RV console:**
   - Look for Python import errors
   - Look for PySide import errors

3. **Verify RV version:**
   - This package requires OpenRV 7.5.0 or later
   - Check your RV version: Help > About RV

### Import Errors

If you see errors about missing imports:

```python
ImportError: No module named 'PySide2' or 'PySide6'
```

This usually means RV's Python environment is not configured correctly. OpenRV should include PySide by default.

**Solution:**
- Reinstall OpenRV
- Or contact your OpenRV administrator

### Permission Errors

If you get permission errors when copying files:

**Windows:**
- Run PowerShell as Administrator
- Or copy to a user-writable location

**macOS/Linux:**
- Use `sudo` if necessary
- Or ensure proper ownership: `chown -R $USER ~/.rv/packages/node_graph_editor`

## Alternative Installation Methods

### Method 1: Symlink (Development)

For developers who want to edit the code while using it:

**Windows (requires admin PowerShell):**
```powershell
New-Item -ItemType SymbolicLink -Path "$env:APPDATA\RV\packages\node_graph_editor" -Target "C:\path\to\rv_tools\node_graph_editor"
```

**macOS/Linux:**
```bash
ln -s /path/to/rv_tools/node_graph_editor ~/Library/Application\ Support/RV/packages/node_graph_editor
```

### Method 2: RV_SUPPORT_PATH Environment Variable

Add the `rv_tools` directory to RV's support path:

**Windows:**
```powershell
setx RV_SUPPORT_PATH "C:\path\to\rv_tools;%RV_SUPPORT_PATH%"
```

**macOS/Linux:**
```bash
export RV_SUPPORT_PATH="/path/to/rv_tools:$RV_SUPPORT_PATH"
```

Then restart RV.

## Uninstallation

To remove the package:

1. **Delete the package directory:**

   **Windows:**
   ```powershell
   Remove-Item -Recurse -Force "$env:APPDATA\RV\packages\node_graph_editor"
   ```

   **macOS/Linux:**
   ```bash
   rm -rf ~/Library/Application\ Support/RV/packages/node_graph_editor
   ```

2. **Restart RV**

## Directory Structure After Installation

```
RV/packages/
└── node_graph_editor/
    ├── PACKAGE
    ├── README.md
    ├── INSTALL.md
    ├── node_graph_editor_mode.py
    └── node_graph_editor/
        ├── __init__.py
        ├── models/
        │   ├── __init__.py
        │   ├── graph_model.py
        │   └── property_model.py
        └── views/
            ├── __init__.py
            ├── graph_view.py
            ├── property_editor.py
            └── widgets/
                ├── __init__.py
                └── property_widgets.py
```

## First Launch

After installation:

1. **Launch OpenRV**
2. **Load some media** (File > Add Source)
3. **Open Node Graph Editor** (Tools > Node Graph Editor)
4. **Explore:**
   - View the node graph on the left
   - Double-click a node to see its properties on the right
   - Edit properties and see changes in real-time

## Getting Help

If you encounter issues:

1. Check the [README.md](README.md) for usage instructions
2. Check the RV Console for error messages
3. Verify all files are present in the package directory
4. Ensure you're using OpenRV 7.5.0 or later

## System Requirements

- **OpenRV**: 7.5.0 or later
- **Operating System**: Windows 10+, macOS 10.15+, or Linux
- **Python**: 3.7+ (included with OpenRV)
- **PySide**: 2 or 6 (included with OpenRV)

## Notes

- The package automatically activates when opened from the Tools menu
- The UI is dockable and can be moved to different positions
- Settings are preserved between RV sessions
- The package has no external dependencies beyond OpenRV





