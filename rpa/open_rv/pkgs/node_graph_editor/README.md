# Node Graph Editor for OpenRV

An interactive node graph visualization and property editor for OpenRV that provides real-time bi-directional synchronization between the UI and RV session.

## Features

### 🎨 **Dynamic Graph Visualization**
- Visual representation of the complete RV session node graph
- Color-coded nodes by type (Source, Stack, Sequence, Layout, etc.)
- Interactive graph with zoom, pan, and drag capabilities
- Real-time updates when nodes are added, removed, or connections change

### ⚙️ **Interactive Property Editor**
- Double-click any node to view and edit its properties
- Type-appropriate UI elements:
  - **Sliders/SpinBoxes** for integer values
  - **Precision inputs** for float values
  - **Text fields** for string values
  - **Read-only display** for array/complex properties
- Search/filter properties by name
- Properties grouped by component for better organization

### 🔄 **Real-time Bi-directional Sync**
- Changes made in the editor **immediately affect RV**
- Changes made in RV **immediately update the editor**
- No manual refresh needed

### 🔧 **Property Management**
- **Reset to Default**: Each property has a reset button to restore original values
- Cached default values per property
- Error handling for inaccessible properties

## Installation

### Option 1: As RV Package (Recommended)

1. Copy the `node_graph_editor` folder to your RV packages directory:
   - **Windows**: `%APPDATA%/RV/packages/`
   - **macOS**: `~/Library/Application Support/RV/packages/`
   - **Linux**: `~/.rv/packages/`

2. Restart RV

3. The package will appear under **Tools > Node Graph Editor**

### Option 2: Direct Integration

The package is located at `rv_tools/node_graph_editor/` and can be loaded directly by RV if the `rv_tools` directory is in RV's Python path.

## Usage

### Opening the Editor

1. Launch OpenRV
2. Go to **Tools > Node Graph Editor**
3. The dockable panel will appear on the right side

### Viewing the Node Graph

- The left panel shows a visual representation of all nodes in the session
- Nodes are color-coded by type:
  - **Light Blue**: Source nodes (RVSourceGroup, RVFileSource, RVImageSource)
  - **Light Green**: Sequence nodes (RVSequenceGroup)
  - **Light Pink**: Stack nodes (RVStackGroup)
  - **Peach**: Switch nodes (RVSwitchGroup)
  - **Light Yellow**: Layout nodes (RVLayoutGroup)
  - **Light Coral**: Color nodes (RVColor, RVDisplayColor)
  - **Light Gray**: View nodes (RVViewGroup)
  - **Plum**: Retime nodes (RVRetimeGroup)
  - **Bisque**: Folder nodes (RVFolderGroup)

### Interacting with Nodes

- **Click and drag** to move nodes
- **Mouse wheel** to zoom in/out
- **Click and drag background** to pan
- **Single-click** a node to select it (red border)
- **Double-click** a node to view/edit its properties

### Editing Properties

1. **Double-click a node** in the graph
2. The right panel will show all editable properties
3. Properties are **grouped by component** (e.g., "color", "lut", "pipeline")
4. Use the **search box** at the top to filter properties
5. **Edit values** directly:
   - Type in text fields for strings
   - Use spin boxes or sliders for numbers
   - Changes apply **immediately** to RV
6. **Click the ↺ button** next to any property to reset it to default

### Real-time Updates

The editor automatically stays in sync with RV:

- **Add a source**: The graph updates to show the new node
- **Delete a node**: Removed from the graph immediately
- **Change connections**: Edges update in real-time
- **Modify properties in RV**: The editor reflects changes automatically

## Architecture

The package follows **SOLID principles** and **MVC pattern**:

```
node_graph_editor/
├── PACKAGE                                    # Package metadata
├── README.md                                  # This file
├── node_graph_editor_mode.py                  # Controller (Main RV Mode)
└── node_graph_editor/                         # Python module (models & views)
    ├── __init__.py
    ├── models/
    │   ├── __init__.py
    │   ├── graph_model.py                     # Model: Graph data structure
    │   └── property_model.py                  # Model: Property management
    └── views/
        ├── __init__.py
        ├── graph_view.py                      # View: Graph visualization
        ├── property_editor.py                 # View: Property editing panel
        └── widgets/
            ├── __init__.py
            └── property_widgets.py            # View: Individual property widgets
```

### Design Principles Applied

#### **Single Responsibility Principle (SRP)**
- `GraphModel`: Only manages graph data structure
- `PropertyModel`: Only manages property data
- `GraphView`: Only handles graph visualization
- `PropertyEditor`: Only handles property UI
- `NodeGraphEditor`: Only coordinates between Model and View

#### **Open/Closed Principle (OCP)**
- Models can be extended with new node/property types
- Views can be customized without modifying core logic
- Widget factory easily accommodates new property types

#### **Liskov Substitution Principle (LSP)**
- All property widgets inherit from `PropertyWidgetBase`
- Can substitute different widget implementations

#### **Interface Segregation Principle (ISP)**
- Minimal, focused interfaces for each component
- No forced dependencies on unused functionality

#### **Dependency Inversion Principle (DIP)**
- Views depend on Model abstractions (NodeInfo, PropertyInfo)
- Controller depends on View/Model interfaces
- No direct RV API calls in Views

## API Reference

### GraphModel

```python
graph_model = GraphModel()

# Sync with RV session
graph_model.sync_from_rv()

# Get all nodes
nodes = graph_model.nodes  # Dict[str, NodeInfo]

# Get all edges (source, target, edge_type)
edges = graph_model.edges  # List[Tuple[str, str, str]]

# Update single node
graph_model.update_single_node("sourceGroup000001")

# Remove node
graph_model.remove_node("sourceGroup000001")
```

### PropertyModel

```python
property_model = PropertyModel()

# Load properties for a node
properties = property_model.load_node_properties("sourceGroup000001")

# Set property value
success = property_model.set_property_value(
    "sourceGroup000001", 
    "color.gamma", 
    [2.2]
)

# Reset to default
success = property_model.reset_property_to_default(
    "sourceGroup000001",
    "color.gamma"
)
```

### GraphView

```python
graph_view = GraphView(graph_model)

# Render graph
graph_view.render_graph()

# Connect to signals
graph_view.nodeDoubleClicked.connect(on_node_selected)
graph_view.nodeSelected.connect(on_node_highlighted)
```

### PropertyEditor

```python
property_editor = PropertyEditor()

# Show node properties
property_editor.show_node_properties(node_name, properties)

# Connect to signals
property_editor.propertyChanged.connect(on_property_changed)
property_editor.propertyResetRequested.connect(on_property_reset)
```

## Events Handled

The editor responds to the following RV events:

- `new-node`: Node added to session
- `after-node-delete`: Node removed from session
- `graph-node-inputs-changed`: Node connections changed
- `graph-state-change`: Property values changed
- `after-graph-view-change`: View node changed
- `after-session-read`: Session loaded from file
- `after-clear-session`: Session cleared

## Troubleshooting

### Package doesn't appear in Tools menu

1. Verify the package is in the correct directory
2. Check RV console for any error messages
3. Ensure PySide2 or PySide6 is available in RV's Python environment

### Properties not updating

1. Check RV console for error messages
2. Verify the property exists and is writable
3. Some properties may be read-only or computed

### Graph is empty

1. Ensure a session is loaded in RV
2. Try loading media or creating a simple session
3. Check that `rv.commands.viewNode()` returns a valid node

### Performance with large graphs

For sessions with many nodes (100+):
- The graph uses a simple grid layout
- Consider zooming to focus on specific areas
- Property editing is not affected by graph size

## Extending the Package

### Adding New Property Widget Types

1. Create a new widget class inheriting from `PropertyWidgetBase`
2. Implement `_setup_ui()`, `set_value()`, and `get_value()`
3. Update `PropertyWidgetFactory.create_widget()` to handle the new type

Example:

```python
class BoolPropertyWidget(PropertyWidgetBase):
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        self.checkbox = QCheckBox(self.property_name)
        self.checkbox.stateChanged.connect(self._on_value_changed)
        layout.addWidget(self.checkbox)
    
    def set_value(self, value):
        self.checkbox.setChecked(bool(value))
    
    def get_value(self):
        return self.checkbox.isChecked()
    
    def _on_value_changed(self):
        self.valueChanged.emit(self.property_name, [self.get_value()])
```

### Custom Graph Layouts

Modify `GraphView._calculate_layout()` to implement different layout algorithms:

```python
def _calculate_layout(self, nodes, edges):
    # Example: Use NetworkX for hierarchical layout
    import networkx as nx
    G = nx.DiGraph(edges)
    positions = nx.spring_layout(G, k=3, iterations=50)
    return {node: (pos[0] * 500, pos[1] * 500) 
            for node, pos in positions.items()}
```

## Dependencies

- **OpenRV** 7.5.0 or later
- **PySide2** or **PySide6** (included with OpenRV)
- **Python** 3.7+ (included with OpenRV)

## License

Copyright (C) 2024 RPA Workspace

SPDX-License-Identifier: Apache-2.0

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Follow SOLID principles and MVC pattern
2. Add docstrings to all public methods
3. Keep Model, View, and Controller layers separate
4. Write clean, readable code with clear variable names
5. Test with various RV sessions and node types

## Support

For issues, questions, or feature requests, please check:
1. This README for common solutions
2. RV console output for error messages
3. OpenRV documentation at https://aswf-openrv.readthedocs.io/

## Version History

### 1.0.0 (2024-11-05)
- Initial release
- Complete graph visualization
- Interactive property editing
- Real-time bi-directional sync
- Property reset functionality
- Color-coded node types
- Search/filter properties
- Zoom, pan, drag interactions





