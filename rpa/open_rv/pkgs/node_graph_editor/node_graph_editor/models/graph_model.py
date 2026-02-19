#
# Copyright (C) 2024  RPA Workspace
# 
# SPDX-License-Identifier: Apache-2.0
#
"""
Graph Model - Independent representation of the RV node graph.

This module follows the Single Responsibility Principle (SRP) by handling
only graph data management, separate from UI and RV API concerns.
"""

from typing import Dict, List, Tuple, Set, Optional
import rv.commands as rvc


class NodeInfo:
    """
    Data class representing a node in the graph.
    
    Follows SRP: Only stores node data, no logic.
    """
    
    def __init__(self, name: str, node_type: str):
        self.name = name
        self.node_type = node_type
        self.inputs: List[str] = []
        self.outputs: List[str] = []
        
    def __repr__(self):
        return f"NodeInfo({self.name}, {self.node_type})"


class GraphModel:
    """
    Model representing the RV session's node graph structure.
    
    SOLID Principles Applied:
    - SRP: Only manages graph data structure and synchronization with RV
    - OCP: Extensible through inheritance, closed for modification
    - DIP: Depends on abstractions (node data), not concrete RV implementation
    
    This is the 'Model' in MVC pattern.
    """
    
    def __init__(self):
        """Initialize an empty graph model."""
        self._nodes: Dict[str, NodeInfo] = {}
        self._edges: List[Tuple[str, str, str]] = []  # (source, target, edge_type) tuples
        self._root_node: Optional[str] = None
        
    @property
    def nodes(self) -> Dict[str, NodeInfo]:
        """Get all nodes in the graph."""
        return self._nodes.copy()
    
    @property
    def edges(self) -> List[Tuple[str, str, str]]:
        """Get all edges in the graph with type information (source, target, type)."""
        return self._edges.copy()
    
    @property
    def root_node(self) -> Optional[str]:
        """Get the root (view) node of the graph."""
        return self._root_node
    
    def get_node(self, node_name: str) -> Optional[NodeInfo]:
        """
        Get information about a specific node.
        
        Args:
            node_name: Name of the node to retrieve
            
        Returns:
            NodeInfo if node exists, None otherwise
        """
        return self._nodes.get(node_name)
    
    def sync_from_rv(self) -> None:
        """
        Synchronize the model with the current RV session graph.
        
        This method traverses the entire RV node graph starting from
        the view node and builds an internal representation.
        """
        # Clear existing data
        self._nodes.clear()
        self._edges.clear()
        
        # Get the root node (view node)
        self._root_node = rvc.viewNode()
        if not self._root_node:
            return
        
        # Traverse the graph using DFS
        visited: Set[str] = set()
        self._traverse_node(self._root_node, visited)
    
    def _traverse_node(self, node_name: str, visited: Set[str]) -> None:
        """
        Recursively traverse the node graph, including internal nodes.
        
        Args:
            node_name: Current node to process
            visited: Set of already visited nodes to avoid cycles
        """
        if node_name in visited:
            return
        
        visited.add(node_name)
        
        # Get node type
        try:
            node_type = rvc.nodeType(node_name)
        except Exception:
            # Node might have been deleted, skip it
            return
        
        # Create node info
        node_info = NodeInfo(node_name, node_type)
        
        # Get connections
        try:
            inputs, outputs = rvc.nodeConnections(node_name)
            
            # Store connections in node info
            node_info.inputs = list(inputs) if inputs else []
            node_info.outputs = list(outputs) if outputs else []
            
            # Add edges to graph (connection type)
            for input_node in node_info.inputs:
                self._edges.append((input_node, node_name, "connection"))
            
            # Store the node
            self._nodes[node_name] = node_info
            
            # Recursively traverse connected nodes
            for input_node in node_info.inputs:
                self._traverse_node(input_node, visited)
            
            for output_node in node_info.outputs:
                self._traverse_node(output_node, visited)
            
            # Also traverse internal nodes if this is a group node
            self._traverse_group_members(node_name, visited)
                
        except Exception as e:
            # Handle errors gracefully (node might be in invalid state)
            print(f"Warning: Error traversing node {node_name}: {e}")
            self._nodes[node_name] = node_info
    
    def _traverse_group_members(self, group_node: str, visited: Set[str]) -> None:
        """
        Traverse internal nodes within a group node and create containment edges.
        
        Args:
            group_node: Name of the group node
            visited: Set of already visited nodes
        """
        try:
            # Get members of this group
            members = rvc.nodesInGroup(group_node)
            if members:
                for member in members:
                    # Create containment edge (group contains member)
                    self._edges.append((group_node, member, "containment"))
                    # Traverse the member node
                    self._traverse_node(member, visited)
        except Exception:
            # Not a group or error getting members
            pass
    
    def update_single_node(self, node_name: str) -> bool:
        """
        Update information for a single node.
        
        Args:
            node_name: Name of the node to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            node_type = rvc.nodeType(node_name)
            
            # Get or create node info
            if node_name in self._nodes:
                node_info = self._nodes[node_name]
                node_info.node_type = node_type
            else:
                node_info = NodeInfo(node_name, node_type)
                self._nodes[node_name] = node_info
            
            # Update connections
            inputs, outputs = rvc.nodeConnections(node_name)
            
            # Remove old edges involving this node
            self._edges = [
                (src, dst, edge_type) for src, dst, edge_type in self._edges 
                if dst != node_name
            ]
            
            # Add new edges
            node_info.inputs = list(inputs) if inputs else []
            node_info.outputs = list(outputs) if outputs else []
            
            for input_node in node_info.inputs:
                self._edges.append((input_node, node_name, "connection"))
            
            return True
            
        except Exception as e:
            print(f"Error updating node {node_name}: {e}")
            return False
    
    def remove_node(self, node_name: str) -> None:
        """
        Remove a node from the graph model.
        
        Args:
            node_name: Name of the node to remove
        """
        if node_name in self._nodes:
            del self._nodes[node_name]
        
        # Remove all edges involving this node
        self._edges = [
            (src, dst, edge_type) for src, dst, edge_type in self._edges 
            if src != node_name and dst != node_name
        ]
    
    def get_node_count(self) -> int:
        """Get the total number of nodes in the graph."""
        return len(self._nodes)
    
    def get_edge_count(self) -> int:
        """Get the total number of edges in the graph."""
        return len(self._edges)
    
    def clear(self) -> None:
        """Clear all graph data."""
        self._nodes.clear()
        self._edges.clear()
        self._root_node = None





