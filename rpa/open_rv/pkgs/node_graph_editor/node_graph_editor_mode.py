#
# Copyright (C) 2024  RPA Workspace
#
# SPDX-License-Identifier: Apache-2.0
#
"""
Node Graph Editor - Interactive node graph visualization and property editor for OpenRV.

This module implements the main RV Mode (Controller in MVC pattern).

SOLID Principles Applied:
- SRP: Controller coordinates between Model and View, handles events
- OCP: Extensible through inheritance, event system is pluggable
- LSP: Follows rv.rvtypes.MinorMode contract
- ISP: Uses focused interfaces for models and views
- DIP: Depends on abstractions (Model/View interfaces), not implementations
"""

import rv.rvtypes
import rv.commands as rvc

try:
    import rv.qtutils
    from PySide6.QtWidgets import QDockWidget, QSplitter, QWidget, QVBoxLayout
    from PySide6.QtCore import Qt, QTimer
except:
    try:
        import rv.qtutils
        from PySide2.QtWidgets import QDockWidget, QSplitter, QWidget, QVBoxLayout
        from PySide2.QtCore import Qt, QTimer
    except:
        print("Error: PySide2 or PySide6 required for Node Graph Editor")
        raise

from node_graph_editor.models import GraphModel, PropertyModel
from node_graph_editor.views import GraphView, PropertyEditor


class NodeGraphEditor(rv.rvtypes.MinorMode):
    """
    Main controller for the Node Graph Editor.

    This is the 'Controller' in MVC pattern, coordinating between:
    - GraphModel/PropertyModel (Model layer)
    - GraphView/PropertyEditor (View layer)
    - RV events (external system)

    Responsibilities:
    - Initialize and coordinate Model and View components
    - Handle RV events and update Model/View accordingly
    - Route user interactions from View to Model
    - Maintain bi-directional sync between RV and UI
    """

    def __init__(self):
        """Initialize the Node Graph Editor mode."""
        rv.rvtypes.MinorMode.__init__(self)

        # Initialize models (data layer)
        self.graph_model = GraphModel()
        self.property_model = PropertyModel()

        # Create main window reference
        try:
            self.main_window = rv.qtutils.sessionWindow()
        except Exception as e:
            print(f"Error: Could not get RV session window: {e}")
            raise

        # Create UI components
        self._setup_ui()

        # Initialize mode with event bindings
        self._register_mode()

        # Debounce timer for property changes
        self._property_update_timer = QTimer()
        self._property_update_timer.setSingleShot(True)
        self._property_update_timer.setInterval(100)  # 100ms debounce
        self._property_update_timer.timeout.connect(self._refresh_current_properties)

        # Track currently displayed node
        self._current_node = None

    def _setup_ui(self):
        """Setup the UI components."""
        # Create dock widget
        self.dock_widget = QDockWidget("Node Graph Editor", self.main_window)
        self.dock_widget.setObjectName("NodeGraphEditorDock")

        # Create main container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for graph view and property editor
        splitter = QSplitter(Qt.Horizontal)

        # Create views
        self.graph_view = GraphView(self.graph_model)
        self.property_editor = PropertyEditor()

        # Add views to splitter
        splitter.addWidget(self.graph_view)
        splitter.addWidget(self.property_editor)

        # Set initial splitter sizes (70% graph, 30% properties)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)

        container_layout.addWidget(splitter)

        # Set dock widget properties
        self.dock_widget.setWidget(container)
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)

        # Add to main window
        self.main_window.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

        # Connect view signals to controller methods
        self._connect_signals()

    def _connect_signals(self):
        """Connect view signals to controller methods."""
        # Graph view signals
        self.graph_view.nodeDoubleClicked.connect(self._on_node_double_clicked)
        self.graph_view.nodeSelected.connect(self._on_node_selected)

        # Property editor signals
        self.property_editor.propertyChanged.connect(self._on_property_changed)
        self.property_editor.propertyResetRequested.connect(self._on_property_reset)

    def _register_mode(self):
        """Register the mode with RV event system."""
        self.init(
            "node_graph_editor",
            [
                # Graph structure events
                ("new-node", self._on_rv_node_added, "Node added to RV"),
                ("after-node-delete", self._on_rv_node_deleted, "Node deleted from RV"),
                ("graph-node-inputs-changed", self._on_rv_connections_changed, "Node connections changed"),

                # Property events
                ("graph-state-change", self._on_rv_property_changed, "Property changed in RV"),

                # Session events
                ("after-graph-view-change", self._on_rv_view_changed, "View node changed"),
                ("after-session-read", self._on_rv_session_loaded, "Session loaded"),
                ("after-clear-session", self._on_rv_session_cleared, "Session cleared"),
            ],
            None,
            None
        )

    # =========================================================================
    # View Event Handlers (User Interactions)
    # =========================================================================

    def _on_node_double_clicked(self, node_name: str):
        """
        Handle node double-click in graph view.

        Args:
            node_name: Name of the double-clicked node
        """
        print(f"Node double-clicked: {node_name}")
        self._current_node = node_name

        # Load properties from model
        properties = self.property_model.load_node_properties(node_name)

        # Display in property editor
        self.property_editor.show_node_properties(node_name, properties)

    def _on_node_selected(self, node_name: str):
        """
        Handle node selection in graph view.

        Args:
            node_name: Name of the selected node
        """
        print(f"Node selected: {node_name}")

    def _on_property_changed(self, node_name: str, prop_name: str, new_value):
        """
        Handle property change from property editor.

        Args:
            node_name: Name of the node
            prop_name: Name of the property
            new_value: New value for the property
        """
        print(f"Property changed: {node_name}.{prop_name} = {new_value}")

        # Update property in RV via model
        success = self.property_model.set_property_value(node_name, prop_name, new_value)

        if success:
            print(f"  ✓ Successfully updated property in RV")
        else:
            print(f"  ✗ Failed to update property in RV")

    def _on_property_reset(self, node_name: str, prop_name: str):
        """
        Handle property reset request.

        Args:
            node_name: Name of the node
            prop_name: Name of the property
        """
        print(f"Reset requested: {node_name}.{prop_name}")

        # Reset to default via model
        success = self.property_model.reset_property_to_default(node_name, prop_name)

        if success:
            print(f"  ✓ Successfully reset property to default")
            # Refresh the property display
            self._refresh_current_properties()
        else:
            print(f"  ✗ Failed to reset property")

    # =========================================================================
    # RV Event Handlers (System Events)
    # =========================================================================

    def _on_rv_node_added(self, event):
        """
        Handle node addition in RV.

        Args:
            event: RV event object
        """
        node_name = event.contents() if hasattr(event, 'contents') else None
        print(f"RV Event: Node added - {node_name}")

        # Update graph model
        if node_name:
            self.graph_model.update_single_node(node_name)
        else:
            self.graph_model.sync_from_rv()

        # Refresh graph view
        self.graph_view.render_graph()

        # Don't call event.reject() - let other modes handle it too

    def _on_rv_node_deleted(self, event):
        """
        Handle node deletion in RV.

        Args:
            event: RV event object
        """
        node_name = event.contents() if hasattr(event, 'contents') else None
        print(f"RV Event: Node deleted - {node_name}")

        # Update graph model
        if node_name:
            self.graph_model.remove_node(node_name)

            # Clear property editor if this was the displayed node
            if self._current_node == node_name:
                self.property_editor.clear()
                self._current_node = None

        # Refresh graph view
        self.graph_view.render_graph()

    def _on_rv_connections_changed(self, event):
        """
        Handle connection changes in RV.

        Args:
            event: RV event object
        """
        node_name = event.contents() if hasattr(event, 'contents') else None
        print(f"RV Event: Connections changed - {node_name}")

        # Update graph model
        if node_name:
            self.graph_model.update_single_node(node_name)
        else:
            self.graph_model.sync_from_rv()

        # Refresh graph view
        self.graph_view.render_graph()

    def _on_rv_property_changed(self, event):
        """
        Handle property changes in RV.

        Args:
            event: RV event object
        """
        prop_path = event.contents() if hasattr(event, 'contents') else None

        if not prop_path or not self._current_node:
            return

        # Check if this property belongs to the currently displayed node
        if prop_path.startswith(f"{self._current_node}."):
            # Extract property name
            prop_name = prop_path[len(self._current_node) + 1:]

            # Use debounce timer to avoid too many updates
            self._property_update_timer.start()

    def _refresh_current_properties(self):
        """Refresh the currently displayed properties."""
        if self._current_node:
            # Reload properties from RV
            properties = self.property_model.load_node_properties(self._current_node)

            # Update property editor display
            self.property_editor.show_node_properties(self._current_node, properties)

    def _on_rv_view_changed(self, event):
        """
        Handle view node change in RV.

        Args:
            event: RV event object
        """
        print("RV Event: View node changed")

        # Resync entire graph
        self.graph_model.sync_from_rv()
        self.graph_view.render_graph()

    def _on_rv_session_loaded(self, event):
        """
        Handle session load in RV.

        Args:
            event: RV event object
        """
        print("RV Event: Session loaded")

        # Resync entire graph
        self.graph_model.sync_from_rv()
        self.graph_view.render_graph()

        # Clear property editor
        self.property_editor.clear()
        self._current_node = None

    def _on_rv_session_cleared(self, event):
        """
        Handle session clear in RV.

        Args:
            event: RV event object
        """
        print("RV Event: Session cleared")

        # Clear models
        self.graph_model.clear()
        self.property_model.clear()

        # Clear views
        self.graph_view.refresh()
        self.property_editor.clear()
        self._current_node = None

    # =========================================================================
    # Mode Lifecycle Methods
    # =========================================================================

    def activate(self):
        """
        Activate the mode (show UI and sync with RV).

        This is called when the mode is turned on.
        """
        rv.rvtypes.MinorMode.activate(self)

        print("Node Graph Editor: Activating")

        # Sync models with RV
        self.graph_model.sync_from_rv()

        # Render initial graph
        self.graph_view.render_graph()

        # Show dock widget
        self.dock_widget.show()
        self.dock_widget.raise_()

    def deactivate(self):
        """
        Deactivate the mode (hide UI).

        This is called when the mode is turned off.
        """
        rv.rvtypes.MinorMode.deactivate(self)

        print("Node Graph Editor: Deactivating")

        # Hide dock widget
        self.dock_widget.hide()


# ============================================================================
# Module-level functions required by RV
# ============================================================================

# Global mode instance
_mode_instance = None


def createMode():
    """
    Create and return the mode instance.

    This function is called by RV to instantiate the mode.
    Required by RV's mode loading system.

    Returns:
        NodeGraphEditor instance
    """
    global _mode_instance

    if _mode_instance is None:
        _mode_instance = NodeGraphEditor()

    return _mode_instance





