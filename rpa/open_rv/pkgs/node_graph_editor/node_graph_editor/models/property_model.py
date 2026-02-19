#
# Copyright (C) 2024  RPA Workspace
# 
# SPDX-License-Identifier: Apache-2.0
#
"""
Property Model - Manages node properties and their values.

This module follows the Single Responsibility Principle (SRP) by handling
only property data management, separate from UI rendering.
"""

from typing import Dict, List, Any, Optional, Tuple
import rv.commands as rvc


class PropertyInfo:
    """
    Data class representing a single property.
    
    Follows SRP: Only stores property data.
    """
    
    def __init__(self, name: str, prop_type: str, value: Any, default_value: Any = None):
        self.name = name
        self.prop_type = prop_type  # 'int', 'float', 'string', 'byte'
        self.value = value
        self.default_value = default_value if default_value is not None else value
        self.size = 1  # Number of elements
        self.width = 1  # Width of each element
        
    def __repr__(self):
        return f"PropertyInfo({self.name}, {self.prop_type}, {self.value})"


class PropertyModel:
    """
    Model representing properties of RV nodes.
    
    SOLID Principles Applied:
    - SRP: Only manages property data and synchronization with RV
    - OCP: Extensible for different property types
    - LSP: Can be subclassed to handle custom property types
    - DIP: Depends on abstractions (PropertyInfo), not RV specifics
    
    Responsibilities:
    - Query properties from RV nodes
    - Cache default values
    - Provide property metadata (type, size, etc.)
    """
    
    def __init__(self):
        """Initialize the property model."""
        self._properties: Dict[str, Dict[str, PropertyInfo]] = {}  # node -> {prop_name -> PropertyInfo}
        self._defaults_cache: Dict[str, Any] = {}  # prop_path -> default value
    
    def load_node_properties(self, node_name: str) -> Dict[str, PropertyInfo]:
        """
        Load all properties for a given node.
        
        Args:
            node_name: Name of the node to query
            
        Returns:
            Dictionary mapping property names to PropertyInfo objects
        """
        properties: Dict[str, PropertyInfo] = {}
        
        try:
            # Get node type for debugging
            node_type = rvc.nodeType(node_name)
            print(f"Loading properties for node: {node_name} (type: {node_type})")
            
            # Get all property paths for this node
            # This returns full property paths like "node.component.property"
            prop_names = rvc.properties(node_name)
            print(f"Found {len(prop_names)} properties")
            
            if not prop_names:
                # No properties found
                self._properties[node_name] = {}
                return {}
            
            for prop_full_path in prop_names:
                try:
                    # prop_full_path is already the complete path like "node.component.property"
                    # Extract just the component.property part for display
                    if prop_full_path.startswith(node_name + "."):
                        prop_name = prop_full_path[len(node_name) + 1:]  # Remove "node." prefix
                    else:
                        # Property doesn't start with node name (shouldn't happen, but handle it)
                        prop_name = prop_full_path
                    
                    # Get property info (type, size, width, etc.)
                    info = rvc.propertyInfo(prop_full_path)
                    
                    # info is a dictionary with keys: 'type', 'size', 'width'
                    prop_type = self._get_type_string(info['type'])
                    
                    # Get property value using the full path
                    value = self._get_property_value(prop_full_path, prop_type)
                    
                    # Get or set default value
                    if prop_full_path not in self._defaults_cache:
                        self._defaults_cache[prop_full_path] = value
                    
                    default_value = self._defaults_cache[prop_full_path]
                    
                    # Create property info
                    prop_info = PropertyInfo(prop_name, prop_type, value, default_value)
                    prop_info.size = info.get('size', 1)
                    prop_info.width = info.get('width', 1)
                    
                    properties[prop_name] = prop_info
                    
                except Exception as e:
                    # Log error but continue with other properties
                    print(f"Warning: Could not load property '{prop_name}' for node {node_name}: {e}")
                    
        except Exception as e:
            print(f"Error loading properties for node {node_name}: {e}")
            import traceback
            traceback.print_exc()
        
        # Cache the properties
        self._properties[node_name] = properties
        print(f"Loaded {len(properties)} properties for {node_name}")
        return properties
    
    
    def _get_type_string(self, type_const: int) -> str:
        """
        Convert RV property type constant to string.
        
        Args:
            type_const: Integer type constant from propertyInfo
            
        Returns:
            Type string ('int', 'float', 'string', 'byte', 'half', 'short')
        """
        # Type constants from rv.commands
        # FloatType = 1, IntType = 2, HalfType = 5, ByteType = 6, ShortType = 7, StringType = 8
        type_map = {
            1: "float",
            2: "int",
            5: "half",
            6: "byte",
            7: "short",
            8: "string"
        }
        return type_map.get(type_const, "unknown")
    
    def _get_property_value(self, prop_path: str, prop_type: str) -> Any:
        """
        Get the current value of a property.
        
        Args:
            prop_path: Full path to the property (node.component.property)
            prop_type: Type of the property
            
        Returns:
            Property value (type depends on prop_type)
        """
        
        try:
            if prop_type == "int":
                return rvc.getIntProperty(prop_path)
            elif prop_type == "float":
                return rvc.getFloatProperty(prop_path)
            elif prop_type == "string":
                return rvc.getStringProperty(prop_path)
            elif prop_type == "byte":
                return rvc.getByteProperty(prop_path)
            else:
                return f"[Unsupported type: {prop_type}]"
        except Exception as e:
            print(f"Error getting value for {prop_path}: {e}")
            return None
    
    def set_property_value(self, node_name: str, prop_name: str, value: Any) -> bool:
        """
        Set a property value in RV.
        
        Args:
            node_name: Name of the node
            prop_name: Name of the property
            value: New value to set
            
        Returns:
            True if successful, False otherwise
        """
        # Get cached property info to determine type
        if node_name not in self._properties:
            self.load_node_properties(node_name)
        
        if node_name not in self._properties or prop_name not in self._properties[node_name]:
            print(f"Property {prop_name} not found for node {node_name}")
            return False
        
        prop_info = self._properties[node_name][prop_name]
        prop_path = f"{node_name}.{prop_name}"
        prop_type = prop_info.prop_type
        
        try:
            # Ensure value is in list format (RV expects lists)
            if not isinstance(value, (list, tuple)):
                value = [value]
            
            # Set the property with push=True for real-time updates
            if prop_type == "int":
                rvc.setIntProperty(prop_path, [int(v) for v in value], True)
            elif prop_type == "float":
                rvc.setFloatProperty(prop_path, [float(v) for v in value], True)
            elif prop_type == "string":
                rvc.setStringProperty(prop_path, [str(v) for v in value], True)
            else:
                print(f"Cannot set property of type {prop_type}")
                return False
            
            # Force RV to redraw the viewport immediately
            rvc.redraw()
            
            # Update cached value
            prop_info.value = value
            return True
            
        except Exception as e:
            print(f"Error setting property {prop_path}: {e}")
            return False
    
    def reset_property_to_default(self, node_name: str, prop_name: str) -> bool:
        """
        Reset a property to its default value.
        
        Args:
            node_name: Name of the node
            prop_name: Name of the property
            
        Returns:
            True if successful, False otherwise
        """
        if node_name not in self._properties or prop_name not in self._properties[node_name]:
            return False
        
        prop_info = self._properties[node_name][prop_name]
        return self.set_property_value(node_name, prop_name, prop_info.default_value)
    
    def get_cached_properties(self, node_name: str) -> Optional[Dict[str, PropertyInfo]]:
        """
        Get cached properties for a node without reloading.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Dictionary of properties if cached, None otherwise
        """
        return self._properties.get(node_name)
    
    def refresh_property(self, node_name: str, prop_name: str) -> bool:
        """
        Refresh a single property's value from RV.
        
        Args:
            node_name: Name of the node
            prop_name: Name of the property
            
        Returns:
            True if successful, False otherwise
        """
        if node_name not in self._properties or prop_name not in self._properties[node_name]:
            return False
        
        prop_info = self._properties[node_name][prop_name]
        prop_path = f"{node_name}.{prop_name}"
        
        try:
            new_value = self._get_property_value(prop_path, prop_info.prop_type)
            prop_info.value = new_value
            return True
        except Exception:
            return False
    
    def clear(self) -> None:
        """Clear all cached property data."""
        self._properties.clear()
    
    def clear_node(self, node_name: str) -> None:
        """
        Clear cached data for a specific node.
        
        Args:
            node_name: Name of the node to clear
        """
        if node_name in self._properties:
            del self._properties[node_name]





