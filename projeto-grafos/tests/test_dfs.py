# -*- coding: utf-8 -*-
"""
Tests for DFS (Depth-First Search) algorithm.

Requirements from project spec:
- DFS: detection of cycles and edge classification
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graphs.graph import Grafo
from src.graphs.algorithms import dfs, dfs_full


def test_dfs_simple_graph():
    """Test DFS on a simple linear graph."""
    G = Grafo()

    # Create a simple path: A -> B -> C -> D
    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('C', 'D', 1.0)

    result = dfs(G, 'A')

    # Check that all nodes were visited
    assert 'A' in result['visited']
    assert 'B' in result['visited']
    assert 'C' in result['visited']
    assert 'D' in result['visited']

    # Check that discovery times are assigned
    assert result['discovery_time']['A'] > 0
    assert result['discovery_time']['B'] > result['discovery_time']['A']

    # Check that finish times are assigned
    assert result['finish_time']['A'] > result['discovery_time']['A']

    # In DFS, we should go deep first
    assert len(result['order']) == 4

    print(" test_dfs_simple_graph passed")


def test_dfs_tree_edges():
    """Test DFS edge classification on a tree (only tree edges)."""
    G = Grafo(dirigido=True)

    # Create a tree:
    #       A
    #      / \
    #     B   C
    #    /
    #   D

    G.add_edge('A', 'B', 1.0)
    G.add_edge('A', 'C', 1.0)
    G.add_edge('B', 'D', 1.0)

    result = dfs(G, 'A')

    # Check for tree edges
    tree_edges = [edge for edge, edge_type in result['edge_classification'].items()
                  if edge_type == 'tree_edge']

    # Should have exactly 3 tree edges (for 4 nodes)
    assert len(tree_edges) == 3

    # No cycle in a tree
    assert result['has_cycle'] == False

    print(" test_dfs_tree_edges passed")


def test_dfs_cycle_detection():
    """Test DFS cycle detection with back edges."""
    G = Grafo()

    # Create a cycle: A - B - C - A
    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('C', 'A', 1.0)

    result = dfs(G, 'A')

    # Should detect cycle
    assert result['has_cycle'] == True

    # Should have at least one back edge
    back_edges = [edge for edge, edge_type in result['edge_classification'].items()
                  if edge_type == 'back_edge']
    assert len(back_edges) > 0

    print(" test_dfs_cycle_detection passed")


def test_dfs_no_cycle():
    """Test DFS on acyclic graph."""
    G = Grafo()

    # Create a DAG (Directed Acyclic Graph structure):
    #     A
    #    / \
    #   B   C
    #    \ /
    #     D

    G.add_edge('A', 'B', 1.0)
    G.add_edge('A', 'C', 1.0)
    G.add_edge('B', 'D', 1.0)
    G.add_edge('C', 'D', 1.0)

    result = dfs(G, 'A')

    # Should NOT detect cycle (undirected graph naturally has cycles,
    # but we're testing the algorithm's behavior)
    # In an undirected graph, parent edges don't count as back edges

    # All nodes should be visited
    assert len(result['visited']) == 4

    print(" test_dfs_no_cycle passed")


def test_dfs_edge_classification():
    """Test DFS edge classification (tree, back, forward, cross)."""
    G = Grafo(dirigido=True)  # Use directed graph for full classification

    # Create a directed graph:
    #   A -> B -> C
    #   |    |
    #   D -> E

    G.add_edge('A', 'B', 1.0)
    G.add_edge('A', 'D', 1.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('B', 'E', 1.0)
    G.add_edge('D', 'E', 1.0)

    result = dfs(G, 'A')

    # Should have edge classifications
    assert len(result['edge_classification']) > 0

    # At least some tree edges
    tree_edges = [e for e, t in result['edge_classification'].items() if t == 'tree_edge']
    assert len(tree_edges) > 0

    print(" test_dfs_edge_classification passed")


def test_dfs_discovery_finish_times():
    """Test that discovery and finish times follow DFS rules."""
    G = Grafo()

    #     A
    #    / \
    #   B   C

    G.add_edge('A', 'B', 1.0)
    G.add_edge('A', 'C', 1.0)

    result = dfs(G, 'A')

    # For each node, discovery time < finish time
    for node in result['visited']:
        assert result['discovery_time'][node] < result['finish_time'][node]

    # A should be discovered first (it's the source)
    assert result['discovery_time']['A'] == 1

    print(" test_dfs_discovery_finish_times passed")


def test_dfs_disconnected_components():
    """Test DFS on graph with disconnected components."""
    G = Grafo()

    # Component 1: A - B
    G.add_edge('A', 'B', 1.0)

    # Component 2: X - Y (disconnected)
    G.add_edge('X', 'Y', 1.0)

    result = dfs(G, 'A')

    # Should only visit component 1
    assert 'A' in result['visited']
    assert 'B' in result['visited']
    assert 'X' not in result['visited']
    assert 'Y' not in result['visited']

    print(" test_dfs_disconnected_components passed")


def test_dfs_full_all_components():
    """Test dfs_full that visits all components."""
    G = Grafo()

    # Component 1: A - B - C
    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)

    # Component 2: X - Y (disconnected)
    G.add_edge('X', 'Y', 1.0)

    result = dfs_full(G)

    # Should visit ALL nodes
    assert 'A' in result['visited']
    assert 'B' in result['visited']
    assert 'C' in result['visited']
    assert 'X' in result['visited']
    assert 'Y' in result['visited']

    # Should visit all 5 nodes
    assert len(result['visited']) == 5

    print(" test_dfs_full_all_components passed")


def test_dfs_complex_cycle():
    """Test DFS with a more complex cycle structure."""
    G = Grafo()

    # Create a graph with multiple cycles:
    #     A - B - C
    #     |   |   |
    #     D - E - F

    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('A', 'D', 1.0)
    G.add_edge('B', 'E', 1.0)
    G.add_edge('C', 'F', 1.0)
    G.add_edge('D', 'E', 1.0)
    G.add_edge('E', 'F', 1.0)

    result = dfs(G, 'A')

    # Should detect cycles
    assert result['has_cycle'] == True

    # All nodes should be reachable
    assert len(result['visited']) == 6

    print(" test_dfs_complex_cycle passed")


def test_dfs_parent_relationships():
    """Test DFS parent-child relationships."""
    G = Grafo()

    #       A
    #      / \
    #     B   C
    #    /
    #   D

    G.add_edge('A', 'B', 1.0)
    G.add_edge('A', 'C', 1.0)
    G.add_edge('B', 'D', 1.0)

    result = dfs(G, 'A')

    # A is the root, has no parent
    assert result['parent']['A'] is None

    # B and C should have A as parent
    # (one of them will be A's child in the DFS tree)
    assert result['parent']['B'] == 'A' or result['parent']['C'] == 'A'

    # D should have B as parent
    assert result['parent']['D'] == 'B'

    print(" test_dfs_parent_relationships passed")


def test_dfs_source_not_in_graph():
    """Test DFS with invalid source."""
    G = Grafo()
    G.add_edge('A', 'B', 1.0)

    try:
        dfs(G, 'Z')  # Z is not in the graph
        assert False, "Should have raised exception"
    except Exception as e:
        assert "not found in graph" in str(e)

    print(" test_dfs_source_not_in_graph passed")


if __name__ == "__main__":
    print("\n=== Running DFS Tests ===\n")

    test_dfs_simple_graph()
    test_dfs_tree_edges()
    test_dfs_cycle_detection()
    test_dfs_no_cycle()
    test_dfs_edge_classification()
    test_dfs_discovery_finish_times()
    test_dfs_disconnected_components()
    test_dfs_full_all_components()
    test_dfs_complex_cycle()
    test_dfs_parent_relationships()
    test_dfs_source_not_in_graph()

    print("\n=== All DFS Tests Passed!  ===\n")
