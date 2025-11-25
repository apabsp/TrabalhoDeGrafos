# -*- coding: utf-8 -*-
"""
Tests for BFS (Breadth-First Search) algorithm.

Requirements from project spec:
- BFS: correct levels in small graph
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graphs.graph import Grafo
from src.graphs.algorithms import bfs, bfs_path


def test_bfs_simple_graph():
    """Test BFS on a simple linear graph."""
    G = Grafo()

    # Create a simple path: A -> B -> C -> D
    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('C', 'D', 1.0)

    result = bfs(G, 'A')

    # Check that all nodes were visited
    assert 'A' in result['visited']
    assert 'B' in result['visited']
    assert 'C' in result['visited']
    assert 'D' in result['visited']

    # Check levels (distances from source)
    assert result['levels']['A'] == 0
    assert result['levels']['B'] == 1
    assert result['levels']['C'] == 2
    assert result['levels']['D'] == 3

    # Check parents
    assert result['parent']['A'] is None
    assert result['parent']['B'] == 'A'
    assert result['parent']['C'] == 'B'
    assert result['parent']['D'] == 'C'

    print(" test_bfs_simple_graph passed")


def test_bfs_tree_structure():
    """Test BFS on a tree structure with multiple branches."""
    G = Grafo()

    # Create a tree:
    #       A (level 0)
    #      / \
    #     B   C (level 1)
    #    / \   \
    #   D   E   F (level 2)

    G.add_edge('A', 'B', 1.0)
    G.add_edge('A', 'C', 1.0)
    G.add_edge('B', 'D', 1.0)
    G.add_edge('B', 'E', 1.0)
    G.add_edge('C', 'F', 1.0)

    result = bfs(G, 'A')

    # Check levels
    assert result['levels']['A'] == 0
    assert result['levels']['B'] == 1
    assert result['levels']['C'] == 1
    assert result['levels']['D'] == 2
    assert result['levels']['E'] == 2
    assert result['levels']['F'] == 2

    # Check that all nodes at same level were discovered
    level_1_nodes = [n for n, level in result['levels'].items() if level == 1]
    assert set(level_1_nodes) == {'B', 'C'}

    level_2_nodes = [n for n, level in result['levels'].items() if level == 2]
    assert set(level_2_nodes) == {'D', 'E', 'F'}

    print(" test_bfs_tree_structure passed")


def test_bfs_disconnected_graph():
    """Test BFS on a graph with disconnected components."""
    G = Grafo()

    # Component 1: A - B - C
    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)

    # Component 2: X - Y (disconnected from A-B-C)
    G.add_edge('X', 'Y', 1.0)

    result = bfs(G, 'A')

    # Should only visit component 1
    assert 'A' in result['visited']
    assert 'B' in result['visited']
    assert 'C' in result['visited']
    assert 'X' not in result['visited']
    assert 'Y' not in result['visited']

    print(" test_bfs_disconnected_graph passed")


def test_bfs_cycle_detection():
    """Test BFS on a graph with cycles."""
    G = Grafo()

    # Create a cycle: A - B - C - D - A
    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('C', 'D', 1.0)
    G.add_edge('D', 'A', 1.0)

    result = bfs(G, 'A')

    # All nodes should be visited
    assert len(result['visited']) == 4

    # Check that levels are computed correctly (shortest path)
    assert result['levels']['A'] == 0
    assert result['levels']['B'] == 1
    assert result['levels']['D'] == 1  # Direct edge from A to D
    assert result['levels']['C'] == 2

    print(" test_bfs_cycle_detection passed")


def test_bfs_path():
    """Test BFS path finding."""
    G = Grafo()

    # Create a graph with multiple paths
    #     A
    #    / \
    #   B   C
    #    \ / \
    #     D   E

    G.add_edge('A', 'B', 1.0)
    G.add_edge('A', 'C', 1.0)
    G.add_edge('B', 'D', 1.0)
    G.add_edge('C', 'D', 1.0)
    G.add_edge('C', 'E', 1.0)

    # Find path from A to D
    path = bfs_path(G, 'A', 'D')
    assert path is not None
    assert path[0] == 'A'
    assert path[-1] == 'D'
    assert len(path) == 3  # Should be shortest: A -> B -> D or A -> C -> D

    # Find path from A to E
    path = bfs_path(G, 'A', 'E')
    assert path is not None
    assert path == ['A', 'C', 'E']

    # Same source and target
    path = bfs_path(G, 'A', 'A')
    assert path == ['A']

    print(" test_bfs_path passed")


def test_bfs_path_no_connection():
    """Test BFS path when no path exists."""
    G = Grafo()

    # Two disconnected components
    G.add_edge('A', 'B', 1.0)
    G.add_edge('X', 'Y', 1.0)

    path = bfs_path(G, 'A', 'X')
    assert path is None  # No path between disconnected components

    print(" test_bfs_path_no_connection passed")


def test_bfs_order():
    """Test BFS traversal order (layer by layer)."""
    G = Grafo()

    # Create a simple tree
    #       1
    #      /|\
    #     2 3 4
    #    /|
    #   5 6

    G.add_edge('1', '2', 1.0)
    G.add_edge('1', '3', 1.0)
    G.add_edge('1', '4', 1.0)
    G.add_edge('2', '5', 1.0)
    G.add_edge('2', '6', 1.0)

    result = bfs(G, '1')
    order = result['order']

    # First element should be source
    assert order[0] == '1'

    # All level-1 nodes should come before level-2 nodes
    idx_2 = order.index('2')
    idx_3 = order.index('3')
    idx_4 = order.index('4')
    idx_5 = order.index('5')
    idx_6 = order.index('6')

    # Level 1 nodes (2, 3, 4) should all come before level 2 nodes (5, 6)
    assert max(idx_2, idx_3, idx_4) < min(idx_5, idx_6)

    print(" test_bfs_order passed")


def test_bfs_source_not_in_graph():
    """Test BFS with invalid source."""
    G = Grafo()
    G.add_edge('A', 'B', 1.0)

    try:
        bfs(G, 'Z')  # Z is not in the graph
        assert False, "Should have raised exception"
    except Exception as e:
        assert "not found in graph" in str(e)

    print(" test_bfs_source_not_in_graph passed")


if __name__ == "__main__":
    print("Starting tests...")

    test_bfs_simple_graph()
    test_bfs_tree_structure()
    test_bfs_disconnected_graph()
    test_bfs_cycle_detection()
    test_bfs_path()
    test_bfs_path_no_connection()
    test_bfs_order()
    test_bfs_source_not_in_graph()
