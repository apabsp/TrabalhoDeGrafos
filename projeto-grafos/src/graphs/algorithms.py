from heapq import heappush, heappop
from itertools import count
from collections import deque

# ===================================================================
# BFS (Breadth-First Search)
# ===================================================================

def bfs(G, source):
    """
    Breadth-First Search algorithm.

    Parameters
    ----------
    G : Graph object
        The graph to search (uses get_vizinhos method)
    source : node
        Starting node for BFS

    Returns
    -------
    dict
        Dictionary with:
        - 'visited': set of visited nodes
        - 'levels': dict mapping node -> level/distance from source
        - 'parent': dict mapping node -> parent in BFS tree
        - 'order': list of nodes in BFS traversal order

    Raises
    ------
    Exception
        If source is not in graph
    """
    if source not in G:
        raise Exception(f"Node {source} not found in graph")

    visited = set()
    levels = {}
    parent = {}
    order = []

    queue = deque()
    queue.append(source)
    visited.add(source)
    levels[source] = 0
    parent[source] = None

    while queue:
        current = queue.popleft()
        order.append(current)

        # Get neighbors (returns list of tuples: [(neighbor, weight), ...])
        neighbors = G.get_vizinhos(current)
        if neighbors:
            for neighbor, weight in neighbors: #
                if neighbor not in visited:
                    visited.add(neighbor)
                    levels[neighbor] = levels[current] + 1
                    parent[neighbor] = current
                    queue.append(neighbor)

    return {
        'visited': visited,
        'levels': levels,
        'parent': parent,
        'order': order
    }

def bfs_path(G, source, target):
    """
    Find shortest path using BFS (unweighted).

    Parameters
    ----------
    G : Graph object
        The graph to search
    source : node
        Starting node
    target : node
        Ending node

    Returns
    -------
    list
        Path from source to target, or None if no path exists
    """
    if source not in G:
        raise Exception(f"Node {source} not found in graph")
    if target not in G:
        raise Exception(f"Node {target} not found in graph")

    if source == target:
        return [source]

    bfs_result = bfs(G, source)

    if target not in bfs_result['visited']:
        return None

    # Reconstruct path from target to source
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = bfs_result['parent'][current]

    path.reverse()
    return path


# ===================================================================
# DFS (Depth-First Search)
# ===================================================================

def dfs(G, source):
    """
    Depth-First Search algorithm.

    Parameters
    ----------
    G : Graph object
        The graph to search (uses get_vizinhos method)
    source : node
        Starting node for DFS

    Returns
    -------
    dict
        Dictionary with:
        - 'visited': set of visited nodes
        - 'parent': dict mapping node -> parent in DFS tree
        - 'order': list of nodes in DFS traversal order
        - 'discovery_time': dict mapping node -> discovery time
        - 'finish_time': dict mapping node -> finish time
        - 'has_cycle': boolean indicating if cycle was detected
        - 'edge_classification': dict mapping edge tuple -> edge type
          (tree_edge, back_edge, forward_edge, cross_edge)

    Raises
    ------
    Exception
        If source is not in graph
    """
    if source not in G:
        raise Exception(f"Node {source} not found in graph")

    visited = set()
    parent = {}
    order = []
    discovery_time = {}
    finish_time = {}
    edge_classification = {}
    has_cycle = False
    time = [0]  

    def dfs_visit(node):
        nonlocal has_cycle

        visited.add(node)
        time[0] += 1
        discovery_time[node] = time[0]
        order.append(node)

        neighbors = G.get_vizinhos(node)
        if neighbors:
            for neighbor, weight in neighbors:
                edge = (node, neighbor)

                if neighbor not in visited:
                    # Tree edge
                    edge_classification[edge] = 'tree_edge'
                    parent[neighbor] = node
                    dfs_visit(neighbor)

                elif neighbor in discovery_time and neighbor not in finish_time:
                    # Back edge (cycle detected)
                    edge_classification[edge] = 'back_edge'
                    has_cycle = True

                elif discovery_time[neighbor] > discovery_time[node]:
                    # Forward edge
                    edge_classification[edge] = 'forward_edge'

                else:
                    # Cross edge
                    edge_classification[edge] = 'cross_edge'

        time[0] += 1
        finish_time[node] = time[0]

    parent[source] = None
    dfs_visit(source)

    return {
        'visited': visited,
        'parent': parent,
        'order': order,
        'discovery_time': discovery_time,
        'finish_time': finish_time,
        'has_cycle': has_cycle,
        'edge_classification': edge_classification
    }

def dfs_full(G):
    """
    Complete DFS traversal of all components in graph.

    Parameters
    ----------
    G : Graph object
        The graph to search

    Returns
    -------
    dict
        Dictionary with same structure as dfs(), but covering all nodes
    """
    all_nodes = G.get_todos_os_nos()
    visited_global = set()
    parent_global = {}
    order_global = []
    discovery_time_global = {}
    finish_time_global = {}
    edge_classification_global = {}
    has_cycle_global = False
    time = [0]

    def dfs_visit(node):
        nonlocal has_cycle_global

        visited_global.add(node)
        time[0] += 1
        discovery_time_global[node] = time[0]
        order_global.append(node)

        neighbors = G.get_vizinhos(node)
        if neighbors:
            for neighbor, weight in neighbors:
                edge = (node, neighbor)

                if neighbor not in visited_global:
                    edge_classification_global[edge] = 'tree_edge'
                    parent_global[neighbor] = node
                    dfs_visit(neighbor)

                elif neighbor in discovery_time_global and neighbor not in finish_time_global:
                    edge_classification_global[edge] = 'back_edge'
                    has_cycle_global = True

                elif discovery_time_global[neighbor] > discovery_time_global[node]:
                    edge_classification_global[edge] = 'forward_edge'

                else:
                    edge_classification_global[edge] = 'cross_edge'

        time[0] += 1
        finish_time_global[node] = time[0]

    for node in all_nodes:
        if node not in visited_global:
            parent_global[node] = None
            dfs_visit(node)

    return {
        'visited': visited_global,
        'parent': parent_global,
        'order': order_global,
        'discovery_time': discovery_time_global,
        'finish_time': finish_time_global,
        'has_cycle': has_cycle_global,
        'edge_classification': edge_classification_global
    }
# DIJKSTRA'S ALGORITHM

def _weight_function(G, weight):
    """Returns a function that returns the weight of an edge.

    The returned function is specifically suitable for input to
    functions :func:`_dijkstra` and :func:`_bellman_ford_relaxation`.

    Parameters
    ----------
    G : NetworkX graph.

    weight : string or function
        If it is callable, `weight` itself is returned. If it is a string,
        it is assumed to be the name of the edge attribute that represents
        the weight of an edge. In that case, a function is returned that
        gets the edge weight according to the specified edge attribute.

    Returns
    -------
    function
        This function returns a callable that accepts exactly three inputs:
        a node, an node adjacent to the first one, and the edge attribute
        dictionary for the eedge joining those nodes. That function returns
        a number representing the weight of an edge.

    If `G` is a multigraph, and `weight` is not callable, the
    minimum edge weight over all parallel edges is returned. If any edge
    does not have an attribute with key `weight`, it is assumed to
    have weight one.

    """
    if callable(weight):
        return weight
    # If the weight keyword argument is not callable, we assume it is a
    # string representing the edge attribute containing the weight of
    # the edge.
    if G.is_multigraph():
        return lambda u, v, d: min(attr.get(weight, 1) for attr in d.values())
    return lambda u, v, data: data.get(weight, 1)

def _dijkstra_multisource(
    G, sources, weight, pred=None, paths=None, cutoff=None, target=None
):
    """Uses Dijkstra's algorithm to find shortest weighted paths

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty iterable of nodes
        Starting nodes for paths. If this is just an iterable containing
        a single node, then all paths computed by this function will
        start from that node. If there are two or more nodes in this
        iterable, the computed paths may begin from any one of the start
        nodes.

    weight: function
        Function with (u, v, data) input that returns that edge's weight
        or None to indicate a hidden edge

    pred: dict of lists, optional(default=None)
        dict to store a list of predecessors keyed by that node
        If None, predecessors are not stored.

    paths: dict, optional (default=None)
        dict to store the path list from source to each node, keyed by node.
        If None, paths are not stored.

    target : node label, optional
        Ending node for path. Search is halted when target is found.

    cutoff : integer or float, optional
        Length (sum of edge weights) at which the search is stopped.
        If cutoff is provided, only return paths with summed weight <= cutoff.

    Returns
    -------
    distance : dictionary
        A mapping from node to shortest distance to that node from one
        of the source nodes.

    Raises
    ------
    NodeNotFound
        If any of `sources` is not in `G`.

    Notes
    -----
    The optional predecessor and path dictionaries can be accessed by
    the caller through the original pred and paths objects passed
    as arguments. No need to explicitly return pred or paths.

    """
    G_succ = G._adj  # For speed-up (and works for both directed and undirected graphs)

    dist = {}  # dictionary of final distances
    seen = {}
    # fringe is heapq with 3-tuples (distance,c,node)
    # use the count c to avoid comparing nodes (may not be able to)
    c = count()
    fringe = []
    for source in sources:
        seen[source] = 0
        heappush(fringe, (0, next(c), source))
    while fringe:
        (d, _, v) = heappop(fringe)
        if v in dist:
            continue  # already searched this node.
        dist[v] = d
        if v == target:
            break
        for u, e in G_succ[v].items():
            cost = weight(v, u, e)
            if cost is None:
                continue
            vu_dist = dist[v] + cost
            if cutoff is not None:
                if vu_dist > cutoff:
                    continue
            if u in dist:
                u_dist = dist[u]
                if vu_dist < u_dist:
                    raise ValueError("Contradictory paths found:", "negative weights?")
                elif pred is not None and vu_dist == u_dist:
                    pred[u].append(v)
            elif u not in seen or vu_dist < seen[u]:
                seen[u] = vu_dist
                heappush(fringe, (vu_dist, next(c), u))
                if paths is not None:
                    paths[u] = paths[v] + [u]
                if pred is not None:
                    pred[u] = [v]
            elif vu_dist == seen[u]:
                if pred is not None:
                    pred[u].append(v)

    # The optional predecessor and path dictionaries can be accessed
    # by the caller via the pred and paths objects passed as arguments.
    return dist

def _dijkstra(G, source, weight, pred=None, paths=None, cutoff=None, target=None):
    """Uses Dijkstra's algorithm to find shortest weighted paths from a
    single source.

    This is a convenience function for :func:`_dijkstra_multisource`
    with all the arguments the same, except the keyword argument
    `sources` set to ``[source]``.

    """
    return _dijkstra_multisource(
        G, [source], weight, pred=pred, paths=paths, cutoff=cutoff, target=target
    )

def multi_source_dijkstra(G, sources, target=None, cutoff=None, weight="weight"):
    """Find shortest weighted paths and lengths from a given set of
    source nodes.

    Uses Dijkstra's algorithm to compute the shortest paths and lengths
    between one of the source nodes and the given `target`, or all other
    reachable nodes if not specified, for a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty set of nodes
        Starting nodes for paths. If this is just a set containing a
        single node, then all paths computed by this function will start
        from that node. If there are two or more nodes in the set, the
        computed paths may begin from any one of the start nodes.

    target : node label, optional
        Ending node for path

    cutoff : integer or float, optional
        Length (sum of edge weights) at which the search is stopped.
        If cutoff is provided, only return paths with summed weight <= cutoff.

    weight : string or function
        If this is a string, then edge weights will be accessed via the
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
        such edge attribute exists, the weight of the edge is assumed to
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    Returns
    -------
    distance, path : pair of dictionaries, or numeric and list
        If target is None, returns a tuple of two dictionaries keyed by node.
        The first dictionary stores distance from one of the source nodes.
        The second stores the path from one of the sources to that node.
        If target is not None, returns a tuple of (distance, path) where
        distance is the distance from source to target and path is a list
        representing the path from source to target.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> length, path = nx.multi_source_dijkstra(G, {0, 4})
    >>> for node in [0, 1, 2, 3, 4]:
    ...     print(f"{node}: {length[node]}")
    0: 0
    1: 1
    2: 2
    3: 1
    4: 0
    >>> path[1]
    [0, 1]
    >>> path[3]
    [4, 3]

    >>> length, path = nx.multi_source_dijkstra(G, {0, 4}, 1)
    >>> length
    1
    >>> path
    [0, 1]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    Based on the Python cookbook recipe (119466) at
    https://code.activestate.com/recipes/119466/

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems).

    Raises
    ------
    ValueError
        If `sources` is empty.
    NodeNotFound
        If any of `sources` is not in `G`.

    See Also
    --------
    multi_source_dijkstra_path
    multi_source_dijkstra_path_length

    """
    if not sources:
        raise ValueError("sources must not be empty")
    for s in sources:
        if s not in G:
            raise Exception(f"Node {s} not found in graph")
    if target in sources:
        return (0, [target])
    weight = _weight_function(G, weight)
    paths = {source: [source] for source in sources}  # dictionary of paths
    dist = _dijkstra_multisource(
        G, sources, weight, paths=paths, cutoff=cutoff, target=target
    )
    if target is None:
        return (dist, paths)
    try:
        return (dist[target], paths[target])
    except KeyError as err:
        raise Exception(f"No path to {target}.") from err
    
def single_source_dijkstra(G, source, target=None, cutoff=None, weight="weight"):
    """Find shortest weighted paths and lengths from a source node.

    Compute the shortest path length between source and all other
    reachable nodes for a weighted graph.

    Uses Dijkstra's algorithm to compute shortest paths and lengths
    between a source and all other reachable nodes in a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
        Starting node for path

    target : node label, optional
        Ending node for path

    cutoff : integer or float, optional
        Length (sum of edge weights) at which the search is stopped.
        If cutoff is provided, only return paths with summed weight <= cutoff.


    weight : string or function
        If this is a string, then edge weights will be accessed via the
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
        such edge attribute exists, the weight of the edge is assumed to
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    Returns
    -------
    distance, path : pair of dictionaries, or numeric and list.
        If target is None, paths and lengths to all nodes are computed.
        The return value is a tuple of two dictionaries keyed by target nodes.
        The first dictionary stores distance to each target node.
        The second stores the path to each target node.
        If target is not None, returns a tuple (distance, path), where
        distance is the distance from source to target and path is a list
        representing the path from source to target.

    Raises
    ------
    NodeNotFound
        If `source` is not in `G`.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> length, path = nx.single_source_dijkstra(G, 0)
    >>> length[4]
    4
    >>> for node in [0, 1, 2, 3, 4]:
    ...     print(f"{node}: {length[node]}")
    0: 0
    1: 1
    2: 2
    3: 3
    4: 4
    >>> path[4]
    [0, 1, 2, 3, 4]
    >>> length, path = nx.single_source_dijkstra(G, 0, 1)
    >>> length
    1
    >>> path
    [0, 1]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    Based on the Python cookbook recipe (119466) at
    https://code.activestate.com/recipes/119466/

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems).

    See Also
    --------
    single_source_dijkstra_path
    single_source_dijkstra_path_length
    single_source_bellman_ford
    """
    return multi_source_dijkstra(
        G, {source}, cutoff=cutoff, target=target, weight=weight
    )

def dijkstra_path(G, source, target, weight="weight"):
    """Returns the shortest weighted path from source to target in G.

    Uses Dijkstra's Method to compute the shortest weighted path
    between two nodes in a graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node
        Starting node

    target : node
        Ending node

    weight : string or function
        If this is a string, then edge weights will be accessed via the
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
        such edge attribute exists, the weight of the edge is assumed to
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    Returns
    -------
    path : list
        List of nodes in a shortest path.

    Raises
    ------
    NodeNotFound
        If `source` is not in `G`.

    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> print(nx.dijkstra_path(G, 0, 4))
    [0, 1, 2, 3, 4]

    Find edges of shortest path in Multigraph

    >>> G = nx.MultiDiGraph()
    >>> G.add_weighted_edges_from([(1, 2, 0.75), (1, 2, 0.5), (2, 3, 0.5), (1, 3, 1.5)])
    >>> nodes = nx.dijkstra_path(G, 1, 3)
    >>> edges = nx.utils.pairwise(nodes)
    >>> list(
    ...     (u, v, min(G[u][v], key=lambda k: G[u][v][k].get("weight", 1)))
    ...     for u, v in edges
    ... )
    [(1, 2, 1), (2, 3, 0)]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    The weight function can be used to include node weights.

    >>> def func(u, v, d):
    ...     node_u_wt = G.nodes[u].get("node_weight", 1)
    ...     node_v_wt = G.nodes[v].get("node_weight", 1)
    ...     edge_wt = d.get("weight", 1)
    ...     return node_u_wt / 2 + node_v_wt / 2 + edge_wt

    In this example we take the average of start and end node
    weights of an edge and add it to the weight of the edge.

    The function :func:`single_source_dijkstra` computes both
    path and length-of-path if you need both, use that.

    See Also
    --------
    bidirectional_dijkstra
    bellman_ford_path
    single_source_dijkstra
    """
    (length, path) = single_source_dijkstra(G, source, target=target, weight=weight)
    return path

def dijkstra_path_length(G, source, target, weight="weight"):
    """Returns the shortest weighted path length in G from source to target.

    Uses Dijkstra's Method to compute the shortest weighted path length
    between two nodes in a graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
        starting node for path

    target : node label
        ending node for path

    weight : string or function
        If this is a string, then edge weights will be accessed via the
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
        such edge attribute exists, the weight of the edge is assumed to
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    Returns
    -------
    length : number
        Shortest path length.

    Raises
    ------
    NodeNotFound
        If `source` is not in `G`.

    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.dijkstra_path_length(G, 0, 4)
    4

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    The function :func:`single_source_dijkstra` computes both
    path and length-of-path if you need both, use that.

    See Also
    --------
    bidirectional_dijkstra
    bellman_ford_path_length
    single_source_dijkstra

    """
    if source not in G:
        raise Exception(f"Node {source} not found in graph")
    if source == target:
        return 0
    weight = _weight_function(G, weight)
    length = _dijkstra(G, source, weight, target=target)
    try:
        return length[target]
    except KeyError as err:
        raise Exception(f"Node {target} not reachable from {source}") from err

# Bellmman Ford

def bellman_ford(G, source, weight="weight"):
    """
    Compute shortest paths from a single source using Bellman-Ford algorithm.

    This algorithm can handle negative edge weights and detects negative cycles.

    Parameters
    ----------
    G : Graph object
        The graph to search (uses get_todos_os_nos and get_vizinhos methods)
    source : node
        Starting node for paths
    weight : string, optional (default="weight")
        Edge weight attribute name. For custom Graph class, this is not used
        directly as weights are part of the adjacency list structure.

    Returns
    -------
    dict
        Dictionary with:
        - 'distances': dict mapping node -> shortest distance from source
        - 'predecessors': dict mapping node -> predecessor in shortest path tree
        - 'has_negative_cycle': boolean indicating if negative cycle was detected
        - 'negative_cycle': list of nodes forming the negative cycle (if detected)

    Raises
    ------
    Exception
        If source is not in graph

    Notes
    -----
    The Bellman-Ford algorithm runs in O(V*E) time complexity.
    It relaxes all edges |V|-1 times, then checks for negative cycles.

    Examples
    --------
    >>> result = bellman_ford(G, 'A')
    >>> if result['has_negative_cycle']:
    ...     print("Negative cycle detected:", result['negative_cycle'])
    ... else:
    ...     print("Shortest distances:", result['distances'])
    """
    if source not in G:
        raise Exception(f"Node {source} not found in graph")

    # Initializxe
    all_nodes = G.get_todos_os_nos()
    distances = {node: float('inf') for node in all_nodes}
    predecessors = {node: None for node in all_nodes}
    distances[source] = 0

    # |V| - 1 
    num_nodes = len(all_nodes)

    for iteration in range(num_nodes - 1):
        updated = False


        for u in all_nodes:
            if distances[u] == float('inf'):
                continue  # Skip 

            neighbors = G.get_vizinhos(u)
            if neighbors:
                for v, edge_weight in neighbors:

                    if distances[u] + edge_weight < distances[v]:
                        distances[v] = distances[u] + edge_weight
                        predecessors[v] = u
                        updated = True


        if not updated:
            break


    has_negative_cycle = False
    negative_cycle = []

    for u in all_nodes:
        if distances[u] == float('inf'):
            continue

        neighbors = G.get_vizinhos(u)
        if neighbors:
            for v, edge_weight in neighbors:
                if distances[u] + edge_weight < distances[v]:

                    has_negative_cycle = True


                    cycle_node = v
                    visited_in_trace = set()


                    for _ in range(num_nodes):
                        cycle_node = predecessors[cycle_node]
                        if cycle_node is None:
                            break


                    if cycle_node is not None:
                        current = cycle_node
                        cycle_path = []
                        while True:
                            if current in visited_in_trace:

                                cycle_start_idx = cycle_path.index(current)
                                negative_cycle = cycle_path[cycle_start_idx:]
                                break
                            visited_in_trace.add(current)
                            cycle_path.append(current)
                            current = predecessors[current]
                            if current is None:
                                break

                    break

        if has_negative_cycle:
            break

    return {
        'distances': distances,
        'predecessors': predecessors,
        'has_negative_cycle': has_negative_cycle,
        'negative_cycle': negative_cycle
    }

def bellman_ford_path(G, source, target, weight="weight"):
    """
    Returns the shortest path from source to target using Bellman-Ford.

    Parameters
    ----------
    G : Graph object
        The graph to search
    source : node
        Starting node
    target : node
        Ending node
    weight : string, optional (default="weight")
        Edge weight attribute name

    Returns
    -------
    list or None
        List of nodes in shortest path, or None if no path exists

    Raises
    ------
    Exception
        If source or target not in graph, or if negative cycle detected
    """
    if source not in G:
        raise Exception(f"Node {source} not found in graph")
    if target not in G:
        raise Exception(f"Node {target} not found in graph")

    if source == target:
        return [source]

    result = bellman_ford(G, source, weight)

    if result['has_negative_cycle']:
        raise Exception(f"Negative cycle detected: {result['negative_cycle']}")

    if result['distances'][target] == float('inf'):
        return None  


    path = []
    current = target
    while current is not None:
        path.append(current)
        current = result['predecessors'][current]

    path.reverse()
    return path

def bellman_ford_path_length(G, source, target, weight="weight"):
    """
    Returns the shortest path length from source to target using Bellman-Ford.

    Parameters
    ----------
    G : Graph object
        The graph to search
    source : node
        Starting node
    target : node
        Ending node
    weight : string, optional (default="weight")
        Edge weight attribute name

    Returns
    -------
    number
        Shortest path length, or float('inf') if no path exists

    Raises
    ------
    Exception
        If source or target not in graph, or if negative cycle detected
    """
    if source not in G:
        raise Exception(f"Node {source} not found in graph")
    if target not in G:
        raise Exception(f"Node {target} not found in graph")

    if source == target:
        return 0

    result = bellman_ford(G, source, weight)

    if result['has_negative_cycle']:
        raise Exception(f"Negative cycle detected: {result['negative_cycle']}")

    return result['distances'][target]

