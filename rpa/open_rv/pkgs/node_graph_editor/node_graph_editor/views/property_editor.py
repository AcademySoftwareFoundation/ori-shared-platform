#
# Copyright (C) 2024  RPA Workspace
#
# SPDX-License-Identifier: Apache-2.0
#
"""
Property Editor View - UI for viewing and editing node properties.

Follows MVC pattern: This is the View component for property editing.
"""

from typing import Dict, Optional, Callable

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QScrollArea, QGroupBox, QLineEdit, QSplitter
    )
    from PySide6.QtCore import Signal, Qt
except:
    from PySide2.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QScrollArea, QGroupBox, QLineEdit, QSplitter
    )
    from PySide2.QtCore import Signal, Qt

from node_graph_editor.models.property_model import PropertyInfo
from node_graph_editor.views.widgets.property_widgets import PropertyWidgetFactory, PropertyWidgetBase


class PropertyEditor(QWidget):
    """
    Property editor panel for displaying and editing node properties.

    SOLID Principles Applied:
    - SRP: Only handles property UI display and user input
    - OCP: Extensible for different property display styles
    - DIP: Depends on PropertyInfo abstraction, not concrete implementations

    This is the 'View' in MVC for properties.
    """

    # Signals
    propertyChanged = Signal(str, str, object)  # (node_name, property_name, new_value)
    propertyResetRequested = Signal(str, str)   # (node_name, property_name)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_node: Optional[str] = None
        self._property_widgets: Dict[str, PropertyWidgetBase] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup the property editor UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header with node name
        header_layout = QHBoxLayout()
        self.node_label = QLabel("No node selected")
        self.node_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.node_label)

        # Search/filter box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter properties...")
        self.search_box.textChanged.connect(self._filter_properties)
        header_layout.addWidget(self.search_box)

        layout.addLayout(header_layout)

        # Scroll area for properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container widget for properties
        self.properties_container = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_container)
        self.properties_layout.setAlignment(Qt.AlignTop)
        self.properties_layout.setSpacing(2)

        scroll_area.setWidget(self.properties_container)
        layout.addWidget(scroll_area)

        # Empty state label
        self.empty_label = QLabel("Double-click a node in the graph to view its properties")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: gray; padding: 20px;")
        self.properties_layout.addWidget(self.empty_label)

    def show_node_properties(self, node_name: str, properties: Dict[str, PropertyInfo]):
        """
        Display properties for a given node.

        Args:
            node_name: Name of the node
            properties: Dictionary of property name to PropertyInfo
        """
        # Clear existing widgets
        self._clear_properties()

        # Update current node
        self._current_node = node_name
        self.node_label.setText(f"Node: {node_name}")

        # Hide empty state
        self.empty_label.hide()

        if not properties:
            self.empty_label.setText("No editable properties found")
            self.empty_label.show()
            return

        # Group properties by component (part before last dot in property name)
        grouped_properties = self._group_properties(properties)

        # Create widgets for each group
        for group_name, group_props in grouped_properties.items():
            self._create_property_group(group_name, group_props)

        # Clear search box
        self.search_box.clear()

    def _group_properties(self, properties: Dict[str, PropertyInfo]) -> Dict[str, Dict[str, PropertyInfo]]:
        """
        Group properties by their component (namespace).

        Args:
            properties: Dictionary of all properties

        Returns:
            Dictionary mapping component name to properties in that component
        """
        groups: Dict[str, Dict[str, PropertyInfo]] = {}

        for prop_name, prop_info in properties.items():
            # Extract component name (everything before last dot, or "General")
            if '.' in prop_name:
                component = prop_name.rsplit('.', 1)[0]
                display_name = prop_name.rsplit('.', 1)[1]
            else:
                component = "General"
                display_name = prop_name

            if component not in groups:
                groups[component] = {}

            # Create a copy with display name
            display_info = PropertyInfo(
                display_name,
                prop_info.prop_type,
                prop_info.value,
                prop_info.default_value
            )
            display_info.size = prop_info.size
            display_info.width = prop_info.width

            groups[component][prop_name] = display_info  # Keep full name as key

        return groups

    def _create_property_group(self, group_name: str, properties: Dict[str, PropertyInfo]):
        """
        Create a collapsible group of properties.

        Args:
            group_name: Name of the property group/component
            properties: Properties in this group
        """
        # Create group box
        group_box = QGroupBox(group_name)
        group_layout = QVBoxLayout()
        group_layout.setSpacing(2)

        # Create widgets for each property
        for full_prop_name, prop_info in sorted(properties.items()):
            widget = PropertyWidgetFactory.create_widget(
                prop_info.name,  # Use display name
                prop_info.prop_type,
                prop_info.value,
                group_box
            )

            # Connect signals
            widget.valueChanged.connect(
                lambda prop_name, value, fpn=full_prop_name:
                self._on_property_changed(fpn, value)
            )
            widget.resetRequested.connect(
                lambda prop_name, fpn=full_prop_name:
                self._on_reset_requested(fpn)
            )

            # Store widget reference
            self._property_widgets[full_prop_name] = widget

            group_layout.addWidget(widget)

        group_box.setLayout(group_layout)
        self.properties_layout.addWidget(group_box)

    def _clear_properties(self):
        """Clear all property widgets."""
        # Remove all widgets from layout except the empty label
        while self.properties_layout.count() > 1:
            item = self.properties_layout.takeAt(1)  # Skip empty_label at index 0
            if item and item.widget():
                item.widget().deleteLater()

        # Clear widget references
        self._property_widgets.clear()

        # Show empty label (if it still exists)
        try:
            self.empty_label.show()
        except RuntimeError:
            # Label was deleted, recreate it
            self.empty_label = QLabel("Double-click a node in the graph to view its properties")
            self.empty_label.setAlignment(Qt.AlignCenter)
            self.empty_label.setStyleSheet("color: gray; padding: 20px;")
            self.properties_layout.insertWidget(0, self.empty_label)

    def _on_property_changed(self, full_prop_name: str, value):
        """
        Handle property value change from widget.

        Args:
            full_prop_name: Full property name (with component)
            value: New value
        """
        if self._current_node:
            self.propertyChanged.emit(self._current_node, full_prop_name, value)

    def _on_reset_requested(self, full_prop_name: str):
        """
        Handle reset button click.

        Args:
            full_prop_name: Full property name (with component)
        """
        if self._current_node:
            self.propertyResetRequested.emit(self._current_node, full_prop_name)

    def _filter_properties(self, search_text: str):
        """
        Filter properties based on search text.

        Args:
            search_text: Text to filter by
        """
        search_text = search_text.lower().strip()

        # If search text is empty, show everything
        if not search_text:
            # Show all widgets
            for widget in self._property_widgets.values():
                widget.setVisible(True)

            # Show all group boxes
            for i in range(self.properties_layout.count()):
                item = self.properties_layout.itemAt(i)
                if item and item.widget():
                    group_box = item.widget()
                    if isinstance(group_box, QGroupBox):
                        group_box.setVisible(True)
            return

        # Show/hide widgets based on filter
        for prop_name, widget in self._property_widgets.items():
            matches = search_text in prop_name.lower()
            widget.setVisible(matches)

        # Show/hide group boxes if all children are hidden
        for i in range(self.properties_layout.count()):
            item = self.properties_layout.itemAt(i)
            if item and item.widget():
                group_box = item.widget()
                if isinstance(group_box, QGroupBox):
                    # Check if any child is visible
                    has_visible = False
                    layout = group_box.layout()
                    if layout:
                        for j in range(layout.count()):
                            child_item = layout.itemAt(j)
                            if child_item and child_item.widget() and child_item.widget().isVisible():
                                has_visible = True
                                break
                    group_box.setVisible(has_visible)

    def update_property_value(self, prop_name: str, new_value):
        """
        Update a property widget's displayed value.

        Args:
            prop_name: Name of the property
            new_value: New value to display
        """
        if prop_name in self._property_widgets:
            widget = self._property_widgets[prop_name]
            widget.set_value(new_value)

    def clear(self):
        """Clear the property editor."""
        self._clear_properties()
        self._current_node = None
        self.node_label.setText("No node selected")
        self.search_box.clear()





