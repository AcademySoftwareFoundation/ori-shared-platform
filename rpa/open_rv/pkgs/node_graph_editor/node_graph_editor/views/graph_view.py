#
# Copyright (C) 2024  RPA Workspace
#
# SPDX-License-Identifier: Apache-2.0
#
"""
Graph View - Visual representation of the RV node graph.

Follows MVC pattern: This is the View component for graph visualization.
"""

from typing import Dict, Optional, Set, Tuple, List

try:
    from PySide6.QtWidgets import (
        QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
        QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem, QWidget,
        QGraphicsPathItem, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
        QLabel, QToolBar
    )
    from PySide6.QtCore import Signal, Qt, QRectF, QPointF, QLineF
    from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont, QPainterPath
except:
    from PySide2.QtWidgets import (
        QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
        QGraphicsTextItem, QGraphicsLineItem, QGraphicsEllipseItem, QWidget,
        QGraphicsPathItem, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
        QLabel, QToolBar
    )
    from PySide2.QtCore import Signal, Qt, QRectF, QPointF, QLineF
    from PySide2.QtGui import QPen, QBrush, QColor, QPainter, QFont, QPainterPath

from node_graph_editor.models.graph_model import GraphModel, NodeInfo


class EdgeGraphicsItem(QGraphicsPathItem):
    """
    Dynamic edge that connects two nodes with a curved pipe-like appearance.

    Supports two edge types:
    - "connection": Data flow connections (solid blue lines)
    - "containment": Group-member relationships (dashed gray lines)

    The edge automatically updates its position when either node moves.
    """

    def __init__(self, source_node: 'NodeGraphicsItem', target_node: 'NodeGraphicsItem',
                 edge_type: str = "connection", parent=None):
        super().__init__(parent)

        self.source_node = source_node
        self.target_node = target_node
        self.edge_type = edge_type

        # Setup appearance based on edge type
        if edge_type == "containment":
            # Gray dashed line for containment (group-member relationships)
            pen = QPen(QColor(120, 120, 120))
            pen.setWidth(2)
            pen.setStyle(Qt.DashLine)
            pen.setDashPattern([5, 3])  # 5 pixels on, 3 pixels off
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            self.setPen(pen)
            self.setOpacity(0.5)
        else:  # "connection" (default)
            # Solid blue line for data flow connections
            pen = QPen(QColor(100, 150, 200))
            pen.setWidth(3)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            self.setPen(pen)
            self.setOpacity(0.8)

        # Draw behind nodes
        self.setZValue(-1)

        # Initial path update
        self.update_path()

        # Register with source and target nodes
        source_node.add_edge(self)
        target_node.add_edge(self)

    def update_path(self):
        """Update the edge path based on current node positions."""
        # Get connection points on the edges of the nodes
        start_point = self.source_node.get_output_point()
        end_point = self.target_node.get_input_point()

        # Create a curved path (Bezier curve) flowing top to bottom
        path = QPainterPath()
        path.moveTo(start_point)

        # Calculate control points for a smooth vertical curve
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()

        # Vertical distance influences the curve
        ctrl_offset = max(abs(dy) * 0.5, 50)

        # Control points for vertical flow (top to bottom)
        ctrl1 = QPointF(start_point.x(), start_point.y() + ctrl_offset)
        ctrl2 = QPointF(end_point.x(), end_point.y() - ctrl_offset)

        # Create cubic bezier curve
        path.cubicTo(ctrl1, ctrl2, end_point)

        self.setPath(path)


class NodeGraphicsItem(QGraphicsRectItem):
    """
    Graphics item representing a node in the graph.

    Follows SRP: Only handles visual representation of a node.
    """

    # Node type colors
    TYPE_COLORS = {
        'RVSourceGroup': QColor(173, 216, 230),      # Light blue
        'RVFileSource': QColor(173, 216, 230),
        'RVImageSource': QColor(173, 216, 230),
        'RVSequenceGroup': QColor(144, 238, 144),    # Light green
        'RVStackGroup': QColor(255, 182, 193),       # Light pink
        'RVSwitchGroup': QColor(255, 218, 185),      # Peach
        'RVLayoutGroup': QColor(255, 255, 224),      # Light yellow
        'RVColor': QColor(240, 128, 128),            # Light coral
        'RVDisplayColor': QColor(240, 128, 128),
        'RVViewGroup': QColor(211, 211, 211),        # Light gray
        'RVRetimeGroup': QColor(221, 160, 221),      # Plum
        'RVFolderGroup': QColor(255, 228, 196),      # Bisque
    }

    DEFAULT_COLOR = QColor(255, 255, 255)  # White

    def __init__(self, node_info: NodeInfo, parent=None):
        super().__init__(parent)

        self.node_info = node_info
        self.node_name = node_info.name
        self.node_type = node_info.node_type

        # Track connected edges for dynamic updates
        self._connected_edges: Set[EdgeGraphicsItem] = set()

        # Track children for hierarchical movement
        self._child_nodes: Set['NodeGraphicsItem'] = set()

        # Setup appearance
        self._setup_appearance()

        # Make it interactive
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.PointingHandCursor)

        # Accept hover events for highlighting
        self.setAcceptHoverEvents(True)

        self._is_hovered = False
        self._ctrl_drag_active = False
        self._last_pos = None

    def _setup_appearance(self):
        """Setup the visual appearance of the node."""
        # Determine color based on node type
        color = self.TYPE_COLORS.get(self.node_type, self.DEFAULT_COLOR)

        # Set size
        width = 180
        height = 60
        self.setRect(0, 0, width, height)

        # Set brush (fill)
        self.setBrush(QBrush(color))

        # Set pen (border)
        pen = QPen(QColor(100, 100, 100))
        pen.setWidth(2)
        self.setPen(pen)

        # Add text labels
        self._create_labels()

    def _create_labels(self):
        """Create text labels for node name and type."""
        # Node name label (bold)
        self.name_label = QGraphicsTextItem(self.node_name, self)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.name_label.setFont(font)
        self.name_label.setPos(10, 5)
        self.name_label.setTextWidth(160)

        # Node type label (smaller, gray)
        self.type_label = QGraphicsTextItem(self.node_type, self)
        type_font = QFont()
        type_font.setPointSize(8)
        self.type_label.setFont(type_font)
        self.type_label.setDefaultTextColor(QColor(100, 100, 100))
        self.type_label.setPos(10, 35)
        self.type_label.setTextWidth(160)

    def hoverEnterEvent(self, event):
        """Handle mouse hover enter."""
        self._is_hovered = True
        pen = self.pen()
        pen.setColor(QColor(50, 50, 255))  # Blue highlight
        pen.setWidth(3)
        self.setPen(pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Handle mouse hover leave."""
        self._is_hovered = False
        if not self.isSelected():
            pen = self.pen()
            pen.setColor(QColor(100, 100, 100))
            pen.setWidth(2)
            self.setPen(pen)
        super().hoverLeaveEvent(event)

    def add_edge(self, edge: EdgeGraphicsItem):
        """Register an edge connected to this node."""
        self._connected_edges.add(edge)

    def remove_edge(self, edge: EdgeGraphicsItem):
        """Unregister an edge from this node."""
        self._connected_edges.discard(edge)

    def add_child_node(self, child: 'NodeGraphicsItem'):
        """Register a child node (for hierarchical movement)."""
        self._child_nodes.add(child)

    def get_all_descendants(self) -> Set['NodeGraphicsItem']:
        """Get all descendant nodes (children, grandchildren, etc.)."""
        descendants = set()
        to_visit = list(self._child_nodes)

        while to_visit:
            child = to_visit.pop()
            if child not in descendants:
                descendants.add(child)
                to_visit.extend(child._child_nodes)

        return descendants

    def get_output_point(self) -> QPointF:
        """Get the connection point for outgoing edges (bottom of node)."""
        rect = self.rect()
        # Bottom center of the node
        local_point = QPointF(rect.width() / 2, rect.height())
        return self.mapToScene(local_point)

    def get_input_point(self) -> QPointF:
        """Get the connection point for incoming edges (top of node)."""
        rect = self.rect()
        # Top center of the node
        local_point = QPointF(rect.width() / 2, 0)
        return self.mapToScene(local_point)

    def mousePressEvent(self, event):
        """Handle mouse press for Ctrl+drag hierarchical movement."""
        if event.modifiers() & Qt.ControlModifier:
            self._ctrl_drag_active = True
            self._last_pos = self.pos()
        else:
            self._ctrl_drag_active = False

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for Ctrl+drag hierarchical movement."""
        if self._ctrl_drag_active and self._last_pos is not None:
            # Calculate movement delta
            delta = self.pos() - self._last_pos

            # Move all descendants
            descendants = self.get_all_descendants()
            for child in descendants:
                child.setPos(child.pos() + delta)

            self._last_pos = self.pos()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self._ctrl_drag_active = False
        self._last_pos = None
        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        """Handle item changes (e.g., selection, position)."""
        if change == QGraphicsItem.ItemSelectedChange:
            if value:  # Selected
                pen = self.pen()
                pen.setColor(QColor(255, 0, 0))  # Red for selection
                pen.setWidth(3)
                self.setPen(pen)
            else:  # Deselected
                pen = self.pen()
                pen.setColor(QColor(100, 100, 100))
                pen.setWidth(2)
                self.setPen(pen)

        elif change == QGraphicsItem.ItemPositionHasChanged:
            # Update all connected edges when node moves
            for edge in self._connected_edges:
                edge.update_path()

        return super().itemChange(change, value)


class GraphicsViewWidget(QGraphicsView):
    """
    Internal graphics view widget for displaying the node graph scene.

    SOLID Principles Applied:
    - SRP: Only handles graph scene rendering and user interaction
    - OCP: Extensible for different layout algorithms
    - DIP: Depends on GraphModel abstraction
    """

    # Signals
    nodeSelected = Signal(str)        # Emitted when a node is clicked
    nodeDoubleClicked = Signal(str)   # Emitted when a node is double-clicked

    def __init__(self, model: GraphModel, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.model = model
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Node graphics items
        self._node_items: Dict[str, NodeGraphicsItem] = {}
        self._edge_items: Set[EdgeGraphicsItem] = set()

        # Setup view properties
        self._setup_view()

    def _setup_view(self):
        """Setup the graphics view properties."""
        # Enable antialiasing for smooth rendering
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)

        # Set background color
        self.setBackgroundBrush(QBrush(QColor(45, 45, 48)))  # Dark background

        # Enable dragging and zooming
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # Set viewport update mode for better performance
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

    def render_graph(self):
        """
        Render the graph from the model.

        This method reads the GraphModel and creates visual representations.
        """
        # Clear existing items
        self._clear_scene()

        # Get nodes from model
        nodes = self.model.nodes
        edges = self.model.edges

        if not nodes:
            return

        # Layout nodes using a simple hierarchical layout
        node_positions = self._calculate_layout(nodes, edges)

        # Create node graphics items
        for node_name, node_info in nodes.items():
            pos = node_positions.get(node_name, (0, 0))
            self._create_node_item(node_info, pos)

        # Build parent-child relationships for hierarchical movement
        for source, target, edge_type in edges:
            if source in self._node_items and target in self._node_items:
                # Source node is parent, target is child (top-to-bottom flow)
                self._node_items[source].add_child_node(self._node_items[target])

        # Create edge graphics items
        for source, target, edge_type in edges:
            self._create_edge_item(source, target, edge_type)

        # Fit view to show all items
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def _calculate_layout(self, nodes: Dict[str, NodeInfo],
                         edges: list) -> Dict[str, Tuple[float, float]]:
        """
        Calculate positions for nodes using hierarchical layout (top to bottom).

        Uses a layered graph drawing approach where nodes are arranged in
        horizontal layers based on their depth in the graph.

        Args:
            nodes: Dictionary of nodes
            edges: List of edges

        Returns:
            Dictionary mapping node names to (x, y) positions
        """
        if not nodes:
            return {}

        # Calculate node layers (depth in graph)
        node_layers = self._calculate_node_layers(nodes, edges)

        # Organize nodes by layer
        layers: Dict[int, List[str]] = {}
        for node_name, layer in node_layers.items():
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(node_name)

        # Layout parameters
        layer_spacing_y = 150  # Vertical spacing between layers
        node_spacing_x = 220   # Horizontal spacing between nodes
        start_y = 50           # Top margin

        positions = {}

        # Position nodes layer by layer
        for layer_idx in sorted(layers.keys()):
            layer_nodes = layers[layer_idx]
            layer_width = len(layer_nodes) * node_spacing_x

            # Center the layer horizontally
            start_x = -layer_width / 2

            # Position each node in this layer
            for i, node_name in enumerate(sorted(layer_nodes)):
                x = start_x + (i + 0.5) * node_spacing_x
                y = start_y + layer_idx * layer_spacing_y
                positions[node_name] = (x, y)

        return positions

    def _calculate_node_layers(self, nodes: Dict[str, NodeInfo],
                               edges: list) -> Dict[str, int]:
        """
        Calculate the layer (depth) for each node in the graph.

        Uses topological sorting to assign layers. Nodes with no inputs
        are at layer 0, and each subsequent layer is based on the maximum
        layer of input nodes + 1.

        Args:
            nodes: Dictionary of nodes
            edges: List of edges (source, target)

        Returns:
            Dictionary mapping node name to layer number
        """
        # Build adjacency information
        in_degree = {name: 0 for name in nodes.keys()}
        children = {name: [] for name in nodes.keys()}

        for source, target, edge_type in edges:
            if source in nodes and target in nodes:
                in_degree[target] += 1
                children[source].append(target)

        # Find root nodes (no inputs)
        roots = [name for name, degree in in_degree.items() if degree == 0]

        # If no roots (cyclic graph), use nodes with minimum in-degree
        if not roots:
            min_degree = min(in_degree.values())
            roots = [name for name, degree in in_degree.items() if degree == min_degree]

        # Assign layers using BFS
        layers = {}
        queue = [(name, 0) for name in roots]

        while queue:
            node_name, layer = queue.pop(0)

            # Update layer to maximum of current and new layer
            if node_name in layers:
                layers[node_name] = max(layers[node_name], layer)
            else:
                layers[node_name] = layer

            # Process children
            if node_name in children:
                for child in children[node_name]:
                    queue.append((child, layers[node_name] + 1))

        # Ensure all nodes have a layer
        for node_name in nodes.keys():
            if node_name not in layers:
                layers[node_name] = 0

        return layers

    def _create_node_item(self, node_info: NodeInfo, pos: Tuple[float, float]):
        """
        Create a graphics item for a node.

        Args:
            node_info: Information about the node
            pos: (x, y) position for the node
        """
        item = NodeGraphicsItem(node_info)
        item.setPos(pos[0], pos[1])
        self.scene.addItem(item)
        self._node_items[node_info.name] = item

    def _create_edge_item(self, source: str, target: str, edge_type: str = "connection"):
        """
        Create a dynamic edge graphics item.

        Args:
            source: Source node name
            target: Target node name
            edge_type: Type of edge ("connection" or "containment")
        """
        if source not in self._node_items or target not in self._node_items:
            return

        source_item = self._node_items[source]
        target_item = self._node_items[target]

        # Create dynamic edge with specified type
        edge = EdgeGraphicsItem(source_item, target_item, edge_type)

        self.scene.addItem(edge)
        self._edge_items.add(edge)

    def _clear_scene(self):
        """Clear all items from the scene."""
        self.scene.clear()
        self._node_items.clear()
        self._edge_items.clear()

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events on nodes."""
        item = self.itemAt(event.pos())

        # Check if a node was clicked
        if isinstance(item, (NodeGraphicsItem, QGraphicsTextItem)):
            # If text item, get parent node
            if isinstance(item, QGraphicsTextItem):
                node_item = item.parentItem()
            else:
                node_item = item

            if isinstance(node_item, NodeGraphicsItem):
                self.nodeDoubleClicked.emit(node_item.node_name)
                return

        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        item = self.itemAt(event.pos())

        if isinstance(item, (NodeGraphicsItem, QGraphicsTextItem)):
            if isinstance(item, QGraphicsTextItem):
                node_item = item.parentItem()
            else:
                node_item = item

            if isinstance(node_item, NodeGraphicsItem):
                self.nodeSelected.emit(node_item.node_name)

        super().mousePressEvent(event)

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        # Zoom factor
        factor = 1.15

        if event.angleDelta().y() > 0:
            # Zoom in
            self.scale(factor, factor)
        else:
            # Zoom out
            self.scale(1 / factor, 1 / factor)

    def refresh(self):
        """Refresh the graph display."""
        self.render_graph()

    def highlight_node(self, node_name: str):
        """
        Highlight a specific node in the graph.

        Args:
            node_name: Name of the node to highlight
        """
        # Reset all nodes to default appearance
        for item in self._node_items.values():
            item.setSelected(False)

        # Highlight the target node
        if node_name in self._node_items:
            target_item = self._node_items[node_name]
            target_item.setSelected(True)
            # Center view on the node
            self.centerOn(target_item)

    def filter_nodes(self, search_text: str):
        """
        Filter/highlight nodes matching search text by name or type, and center on first match.

        Args:
            search_text: Text to search for in node names or node types
        """
        search_lower = search_text.lower()
        first_match = None

        for node_name, item in self._node_items.items():
            if not search_text:
                # Show all nodes when search is empty
                item.setOpacity(1.0)
                item.setSelected(False)
            else:
                # Check if search text matches node name OR node type
                name_matches = search_lower in node_name.lower()
                type_matches = search_lower in item.node_type.lower()

                if name_matches or type_matches:
                    # Highlight matching nodes
                    item.setOpacity(1.0)
                    item.setSelected(True)
                    # Track first match
                    if first_match is None:
                        first_match = item
                else:
                    # Dim non-matching nodes
                    item.setOpacity(0.3)
                    item.setSelected(False)

        # Center view on first matching node
        if first_match is not None:
            self.centerOn(first_match)


class GraphView(QWidget):
    """
    Composite widget containing toolbar and graph visualization.

    SOLID Principles Applied:
    - SRP: Manages UI composition and delegates graph operations
    - OCP: Extensible through toolbar customization
    - DIP: Depends on GraphModel abstraction

    This is the main 'View' component in MVC for the graph editor.
    """

    # Forward signals from internal graphics view
    nodeSelected = Signal(str)
    nodeDoubleClicked = Signal(str)

    def __init__(self, model: GraphModel, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.model = model

        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create toolbar
        self._create_toolbar()
        layout.addWidget(self.toolbar)

        # Create graphics view
        self.graphics_view = GraphicsViewWidget(model, self)
        layout.addWidget(self.graphics_view)

        # Forward signals
        self.graphics_view.nodeSelected.connect(self.nodeSelected.emit)
        self.graphics_view.nodeDoubleClicked.connect(self.nodeDoubleClicked.emit)

        # Connect search box to filter function
        self.search_box.textChanged.connect(self._on_search_changed)

        # Connect refresh button
        self.refresh_button.clicked.connect(self._on_refresh_clicked)

    def _create_toolbar(self):
        """Create the toolbar with search and refresh controls."""
        self.toolbar = QWidget()
        self.toolbar.setStyleSheet("background-color: #2d2d30; padding: 5px;")

        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout.setSpacing(10)

        # Search label
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: white;")
        toolbar_layout.addWidget(search_label)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search nodes by name or type...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
                min-width: 200px;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
        """)
        toolbar_layout.addWidget(self.search_box)

        # Spacer
        toolbar_layout.addStretch()

        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh Graph")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5689;
            }
        """)
        self.refresh_button.setToolTip("Refresh the node graph from current RV session")
        toolbar_layout.addWidget(self.refresh_button)

    def _on_search_changed(self, text: str):
        """Handle search box text changes."""
        self.graphics_view.filter_nodes(text)

    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        # Reload model from RV session
        self.model.sync_from_rv()
        # Re-render the graph
        self.graphics_view.render_graph()
        # Clear search
        self.search_box.clear()

    # Delegate methods to internal graphics view
    def render_graph(self):
        """Render the graph from the model."""
        self.graphics_view.render_graph()

    def refresh(self):
        """Refresh the graph display."""
        self.graphics_view.refresh()
