# Node Graph Editor - Architecture Documentation

## Overview

The Node Graph Editor is a sophisticated RV package that provides interactive visualization and editing of OpenRV's node graph. It follows industry best practices including SOLID principles, MVC pattern, and clean architecture.

## Architectural Patterns

### 1. Model-View-Controller (MVC)

The application strictly separates concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        Controller                            │
│                  (node_graph_editor.py)                      │
│  • Coordinates Model and View                                │
│  • Handles RV events                                         │
│  • Routes user interactions                                  │
└─────────────┬───────────────────────────┬───────────────────┘
              │                           │
              ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │     Model       │         │      View       │
    │                 │         │                 │
    │ • GraphModel    │         │ • GraphView     │
    │ • PropertyModel │         │ • PropertyEditor│
    │                 │         │ • Widgets       │
    │ Data & Logic    │         │ Presentation    │
    └─────────────────┘         └─────────────────┘
              │                           │
              └───────────┬───────────────┘
                          ▼
                 ┌─────────────────┐
                 │   RV Session    │
                 │   (External)    │
                 └─────────────────┘
```

### 2. Factory Pattern

`PropertyWidgetFactory` encapsulates the creation logic for different property widget types:

```python
widget = PropertyWidgetFactory.create_widget(
    property_name="gamma",
    property_type="float",
    value=[2.2]
)
```

Benefits:
- Easy to add new widget types
- Centralized creation logic
- Type-safe widget instantiation

### 3. Observer Pattern

Uses Qt's Signal/Slot mechanism for event-driven updates:

```python
# View emits signals
self.graph_view.nodeDoubleClicked.connect(controller.handle_selection)
self.property_editor.propertyChanged.connect(controller.update_rv)

# RV events trigger updates
"graph-state-change" → controller.sync_ui()
```

## SOLID Principles

### Single Responsibility Principle (SRP)

Each class has one reason to change:

| Class | Single Responsibility |
|-------|----------------------|
| `GraphModel` | Manage graph data structure |
| `PropertyModel` | Manage property data and RV sync |
| `GraphView` | Visualize node graph |
| `PropertyEditor` | Display and edit properties |
| `NodeGraphEditor` | Coordinate Model/View/Events |
| `PropertyWidgetFactory` | Create appropriate widgets |

### Open/Closed Principle (OCP)

The system is open for extension, closed for modification:

**Adding a new property widget type:**
```python
# 1. Create new widget class (extension)
class ColorPropertyWidget(PropertyWidgetBase):
    def _setup_ui(self):
        # Custom color picker UI
        pass

# 2. Register in factory (extension point)
def create_widget(prop_name, prop_type, value):
    if prop_type == "color":
        return ColorPropertyWidget(prop_name, prop_type)
    # Existing code unchanged
```

**Adding a new layout algorithm:**
```python
# Override in subclass (extension)
class CustomGraphView(GraphView):
    def _calculate_layout(self, nodes, edges):
        # Custom layout algorithm
        return positions
```

### Liskov Substitution Principle (LSP)

All property widgets are substitutable:

```python
# Any PropertyWidgetBase subclass works here
def add_property_widget(widget: PropertyWidgetBase):
    widget.valueChanged.connect(self.on_value_changed)
    widget.resetRequested.connect(self.on_reset)
    layout.addWidget(widget)

# All these work:
add_property_widget(IntPropertyWidget(...))
add_property_widget(FloatPropertyWidget(...))
add_property_widget(StringPropertyWidget(...))
```

### Interface Segregation Principle (ISP)

Focused interfaces prevent forced dependencies:

```python
class PropertyWidgetBase:
    # Minimal interface
    def set_value(self, value): pass
    def get_value(self): pass
    # Signals for communication
    valueChanged = Signal(str, object)
    resetRequested = Signal(str)
```

Clients only depend on methods they use:
- View layer doesn't need to know about RV API
- Widgets don't need to know about models
- Models don't need to know about Qt

### Dependency Inversion Principle (DIP)

High-level modules depend on abstractions:

```python
# High-level Controller depends on Model/View abstractions
class NodeGraphEditor:
    def __init__(self):
        self.graph_model = GraphModel()      # Abstraction
        self.property_model = PropertyModel() # Abstraction
        self.graph_view = GraphView(self.graph_model)
        self.property_editor = PropertyEditor()

# Models define their own abstractions
@dataclass
class NodeInfo:  # Abstraction
    name: str
    node_type: str

@dataclass
class PropertyInfo:  # Abstraction
    name: str
    prop_type: str
    value: Any
```

## Data Flow

### 1. Initialization Flow

```
RV loads package
       ↓
createMode() called
       ↓
NodeGraphEditor.__init__()
       ├→ Create GraphModel
       ├→ Create PropertyModel
       ├→ Create GraphView
       ├→ Create PropertyEditor
       ├→ Register RV events
       └→ Connect UI signals
```

### 2. User Interaction Flow (Property Edit)

```
User edits property in UI
       ↓
PropertyWidget.valueChanged signal
       ↓
PropertyEditor.propertyChanged signal
       ↓
Controller._on_property_changed()
       ↓
PropertyModel.set_property_value()
       ↓
rv.commands.setXProperty(..., push=True)
       ↓
RV session updated immediately
       ↓
RV emits "graph-state-change" event
       ↓
Controller._on_rv_property_changed()
       ↓
(Debounced) Refresh UI display
```

### 3. RV Event Flow (Node Added)

```
User adds source in RV
       ↓
RV emits "new-node" event
       ↓
Controller._on_rv_node_added()
       ↓
GraphModel.update_single_node()
       ├→ Query RV for node info
       └→ Update internal data
       ↓
GraphView.render_graph()
       ├→ Create NodeGraphicsItem
       ├→ Position node
       └→ Draw connections
       ↓
UI displays new node
```

## Component Details

### GraphModel

**Purpose:** Independent representation of RV's node graph

**Key Methods:**
- `sync_from_rv()`: Full graph traversal and sync
- `update_single_node()`: Incremental update
- `remove_node()`: Handle node deletion
- `_traverse_node()`: Recursive graph walking

**Data Structures:**
```python
_nodes: Dict[str, NodeInfo]        # Node name → Info
_edges: List[Tuple[str, str]]      # Connections
_root_node: Optional[str]          # View node
```

### PropertyModel

**Purpose:** Manage node properties and RV synchronization

**Key Methods:**
- `load_node_properties()`: Query all properties from RV
- `set_property_value()`: Write property to RV
- `reset_property_to_default()`: Restore default value
- `_get_property_value()`: Type-aware value retrieval

**Caching Strategy:**
```python
_properties: Dict[str, Dict[str, PropertyInfo]]  # Cache
_defaults_cache: Dict[str, Any]                   # Defaults
```

### GraphView

**Purpose:** Visual representation of the node graph

**Key Features:**
- Custom `NodeGraphicsItem` for each node
- Color-coded by node type
- Interactive (drag, zoom, pan)
- Selection and hover effects

**Layout Algorithm:**
- Simple grid layout (current)
- Extensible for NetworkX layouts
- Configurable spacing

### PropertyEditor

**Purpose:** Dynamic property editing interface

**Key Features:**
- Property grouping by component
- Search/filter functionality
- Dynamic widget creation per property type
- Collapsible groups

**Widget Creation Flow:**
```
PropertyEditor.show_node_properties()
       ↓
_group_properties()  # Organize by component
       ↓
_create_property_group()  # For each group
       ↓
PropertyWidgetFactory.create_widget()  # For each property
       ↓
Connect signals  # Wire up events
```

### NodeGraphEditor (Controller)

**Purpose:** Coordinate all components and handle events

**Responsibilities:**
1. **Initialization:** Set up models, views, UI
2. **Event Routing:** RV events → Model updates → View refresh
3. **User Input:** View signals → Model updates → RV updates
4. **Lifecycle:** Activate/deactivate mode

**Event Handlers:**
- `_on_node_double_clicked()`: Load and display properties
- `_on_property_changed()`: Update RV session
- `_on_rv_node_added()`: Sync graph model
- `_on_rv_property_changed()`: Refresh UI

## Performance Considerations

### 1. Debouncing

Property change events are debounced to avoid UI thrashing:

```python
self._property_update_timer = QTimer()
self._property_update_timer.setSingleShot(True)
self._property_update_timer.setInterval(100)  # 100ms
```

### 2. Incremental Updates

Graph updates are incremental when possible:

```python
# Instead of full resync:
if node_name:
    self.graph_model.update_single_node(node_name)
else:
    self.graph_model.sync_from_rv()  # Only when necessary
```

### 3. Lazy Loading

Properties are loaded on-demand:

```python
# Only load properties when node is selected
def _on_node_double_clicked(self, node_name):
    properties = self.property_model.load_node_properties(node_name)
    # Not loaded for all nodes upfront
```

### 4. View Optimization

Graphics view uses efficient rendering:

```python
setRenderHint(QPainter.Antialiasing)
setViewportUpdateMode(FullViewportUpdate)
setTransformationAnchor(AnchorUnderMouse)
```

## Error Handling

### Graceful Degradation

```python
try:
    node_type = rvc.nodeType(node_name)
except Exception as e:
    print(f"Warning: Could not get node type: {e}")
    # Continue with other nodes
```

### User Feedback

- Console logging for debugging
- Visual feedback (selection, hover)
- Property validation before setting

## Extension Points

### Adding New Features

1. **Custom Property Types:**
   - Subclass `PropertyWidgetBase`
   - Register in `PropertyWidgetFactory`

2. **Alternative Layouts:**
   - Override `GraphView._calculate_layout()`
   - Use NetworkX algorithms

3. **Additional Model Data:**
   - Extend `NodeInfo` or `PropertyInfo`
   - Update serialization logic

4. **Custom Node Rendering:**
   - Subclass `NodeGraphicsItem`
   - Override `_setup_appearance()`

5. **Additional RV Events:**
   - Add event handlers in `_register_mode()`
   - Implement handler methods

## Testing Strategy

### Unit Testing

```python
# Test models independently
def test_graph_model():
    model = GraphModel()
    model.sync_from_rv()
    assert len(model.nodes) > 0

# Test widgets independently
def test_float_widget():
    widget = FloatPropertyWidget("test", "float")
    widget.set_value([3.14])
    assert widget.get_value() == 3.14
```

### Integration Testing

```python
# Test Model-View coordination
def test_property_edit():
    model = PropertyModel()
    editor = PropertyEditor()
    
    # Simulate property edit
    editor.propertyChanged.emit("node", "prop", [42])
    # Verify model was updated
    assert model.get_cached_properties("node")["prop"].value == [42]
```

### Manual Testing Checklist

- [ ] Load various media types
- [ ] Edit different property types
- [ ] Add/remove nodes in RV
- [ ] Change connections
- [ ] Reset properties
- [ ] Search/filter
- [ ] Zoom/pan/drag
- [ ] Multiple sessions

## Future Enhancements

### Potential Features

1. **Property Presets:**
   - Save/load property configurations
   - Apply to multiple nodes

2. **Batch Editing:**
   - Edit properties on multiple nodes
   - Bulk operations

3. **Undo/Redo:**
   - Command pattern for property changes
   - History stack

4. **Property Animation:**
   - Keyframe support
   - Timeline integration

5. **Advanced Search:**
   - Regular expressions
   - Property value search

6. **Export/Import:**
   - Graph structure to JSON
   - Property configurations

## Dependencies

### Direct Dependencies

- `rv.rvtypes`: RV mode system
- `rv.commands`: RV API
- `rv.qtutils`: Qt integration
- `PySide2` or `PySide6`: UI framework

### Internal Dependencies

```
node_graph_editor.py
    ├─→ models.GraphModel
    ├─→ models.PropertyModel
    ├─→ views.GraphView
    └─→ views.PropertyEditor
        └─→ widgets.PropertyWidgetFactory
```

### No External Dependencies

The package has zero external dependencies beyond OpenRV itself.

## Conclusion

The Node Graph Editor demonstrates professional software engineering practices:

- **Maintainable:** Clear separation of concerns
- **Extensible:** Multiple extension points
- **Testable:** Decoupled components
- **Robust:** Error handling and validation
- **Performant:** Optimized updates and rendering
- **User-Friendly:** Intuitive interface with real-time feedback

The architecture supports evolution while maintaining stability through well-defined interfaces and SOLID principles.





