import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #

from src.graphs.graph import Grafo
from src.graphs.algorithms import bellman_ford, bellman_ford_path, bellman_ford_path_length


def test_bellman_ford_simple_path():
    G = Grafo()

    # A -5-> B -3-> C -2-> D
    G.add_edge('A', 'B', 5.0)
    G.add_edge('B', 'C', 3.0)
    G.add_edge('C', 'D', 2.0)

    result = bellman_ford(G, 'A')

    # checando soma
    assert result['distances']['A'] == 0
    assert result['distances']['B'] == 5.0
    assert result['distances']['C'] == 8.0
    assert result['distances']['D'] == 10.0

    # No negative cycle
    assert result['has_negative_cycle'] == False

    print(" test_bellman_ford_simple_path passed")


def test_bellman_ford_with_negative_weights_no_cycle():
    G = Grafo(dirigido=True)

    G.add_edge('A', 'B', 5.0)
    G.add_edge('A', 'C', 1.0)
    G.add_edge('B', 'D', -3.0)  # Negative weight
    G.add_edge('C', 'D', 7.0)

    result = bellman_ford(G, 'A')
    assert result['has_negative_cycle'] == False

    assert result['distances']['A'] == 0
    assert result['distances']['B'] == 5.0
    assert result['distances']['C'] == 1.0
    # A->B->D é 5 + (-3) = 2
    # A->C->D é 1 + 7 = 8
    assert result['distances']['D'] == 2.0

    print("test_bellman_ford_with_negative_weights_no_cycle passed")


def test_bellman_ford_negative_cycle_detection():
    G = Grafo(dirigido=True) 

    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('C', 'A', -5.0)

    result = bellman_ford(G, 'A')

    assert result['has_negative_cycle'] == True
    assert len(result['negative_cycle']) > 0

    print("test_bellman_ford_negative_cycle_detection passed")


def test_bellman_ford_another_negative_cycle():
    G = Grafo(dirigido=True)

    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 2.0)
    G.add_edge('C', 'D', 3.0)
    G.add_edge('D', 'B', -8.0) 

    result = bellman_ford(G, 'A')
    assert result['has_negative_cycle'] == True

    print("test_bellman_ford_another_negative_cycle")


def test_bellman_ford_path_with_negative_weights():
    G = Grafo(dirigido=True)

    G.add_edge('A', 'B', 10.0)
    G.add_edge('A', 'C', 5.0)
    G.add_edge('C', 'B', -2.0) 

    result = bellman_ford(G, 'A')

    assert result['distances']['B'] == 3.0

    path = bellman_ford_path(G, 'A', 'B')
    assert path == ['A', 'C', 'B']

    length = bellman_ford_path_length(G, 'A', 'B')
    assert length == 3.0

    print("test_bellman_ford_path_with_negative_weights passed")


def test_bellman_ford_path_raises_on_negative_cycle():
    G = Grafo(dirigido=True)

    G.add_edge('A', 'B', 1.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('C', 'A', -5.0)

    try:
        bellman_ford_path(G, 'A', 'B')
        assert False, "Should have raised exception for negative cycle"
    except Exception as e:
        assert "negative cycle" in str(e).lower()

    print("test_bellman_ford_path_raises_on_negative_cycle")


def test_bellman_ford_unreachable_nodes():
    G = Grafo(dirigido=True)

    G.add_edge('A', 'B', 1.0)
    G.add_edge('X', 'Y', 2.0)

    result = bellman_ford(G, 'A')

    assert result['distances']['A'] == 0
    assert result['distances']['B'] == 1.0

    assert result['distances']['X'] == float('inf')
    assert result['distances']['Y'] == float('inf')

    print("test_bellman_ford_unreachable_nodes")


def test_bellman_ford_same_source_target():
    G = Grafo()
    G.add_edge('A', 'B', 5.0)

    length = bellman_ford_path_length(G, 'A', 'A')
    assert length == 0

    path = bellman_ford_path(G, 'A', 'A')
    assert path == ['A']

    print("test_bellman_ford_same_source_target")


def test_bellman_ford_multiple_negative_weights():
    G = Grafo(dirigido=True)

    #   A -10-> B
    #   A -5-> C
    #   B -(-8)-> D
    #   C -(-3)-> D
    #   D -2-> E

    G.add_edge('A', 'B', 10.0)
    G.add_edge('A', 'C', 5.0)
    G.add_edge('B', 'D', -8.0)
    G.add_edge('C', 'D', -3.0)
    G.add_edge('D', 'E', 2.0)

    result = bellman_ford(G, 'A')

    assert result['has_negative_cycle'] == False

    assert result['distances']['A'] == 0
    # A->B costs 10, A->C costs 5
    # A->B->D costs 10 + (-8) = 2
    # A->C->D costs 5 + (-3) = 2
    # Both paths to D cost 2
    assert result['distances']['D'] == 2.0
    # A->...->D->E costs 2 + 2 = 4
    assert result['distances']['E'] == 4.0

    print(" test_bellman_ford_multiple_negative_weights passed")


def test_bellman_ford_complex_graph():
    """Test Bellman-Ford on a more complex graph."""
    G = Grafo(dirigido=True)


    G.add_edge('S', 'A', 3.0)
    G.add_edge('S', 'B', 5.0)
    G.add_edge('A', 'B', -2.0)  
    G.add_edge('A', 'C', 7.0)
    G.add_edge('B', 'C', 1.0)
    G.add_edge('B', 'D', 8.0)
    G.add_edge('C', 'D', -4.0)  
    G.add_edge('D', 'E', 2.0)

    result = bellman_ford(G, 'S')


    assert result['has_negative_cycle'] == False


    assert result['distances']['S'] == 0

    assert result['distances']['E'] != float('inf')

    print("test_bellman_ford_complex_graph")




def test_bellman_ford_vs_dijkstra_positive_weights():
    """Test that Bellman-Ford gives same results as Dijkstra for positive weights."""
    from src.graphs.algorithms import dijkstra_path_length

    G = Grafo()

    G.add_edge('A', 'B', 4.0)
    G.add_edge('A', 'C', 2.0)
    G.add_edge('B', 'D', 5.0)
    G.add_edge('C', 'D', 8.0)
    G.add_edge('C', 'E', 10.0)
    G.add_edge('D', 'E', 2.0)

    # Both algorithms should give the same results
    bf_result = bellman_ford(G, 'A')
    dijk_dist_B = dijkstra_path_length(G, 'A', 'B', weight='weight')
    dijk_dist_E = dijkstra_path_length(G, 'A', 'E', weight='weight')

    assert bf_result['distances']['B'] == dijk_dist_B
    assert bf_result['distances']['E'] == dijk_dist_E

    print("test_bellman_ford_vs_dijkstra_positive_weights")


if __name__ == "__main__":
    print("\n=== Running Bellman-Ford Tests ===\n")

    test_bellman_ford_simple_path()
    test_bellman_ford_with_negative_weights_no_cycle()  
    test_bellman_ford_negative_cycle_detection()         
    test_bellman_ford_another_negative_cycle()
    test_bellman_ford_path_with_negative_weights()
    test_bellman_ford_path_raises_on_negative_cycle()
    test_bellman_ford_unreachable_nodes()
    test_bellman_ford_same_source_target()
    test_bellman_ford_multiple_negative_weights()
    test_bellman_ford_complex_graph()
    test_bellman_ford_vs_dijkstra_positive_weights()

    print("\n=== All Bellman-Ford Tests Passed!===\n")
