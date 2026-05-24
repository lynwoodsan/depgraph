"""Extract a subgraph centred on a node, using ancestor/descendant traversal."""

from __future__ import annotations
from collections import deque
from depgraph.graph import Graph, Node
from depgraph.ancestors import get_neighbourhood, _find


def extract_subgraph(graph: Graph, node_name: str, depth: int = -1) -> Graph:
    """Return a new Graph containing only *node_name* and its neighbourhood.

    Parameters
    ----------
    graph:     Source graph.
    node_name: Centre node for the subgraph.
    depth:     Maximum edge distance to include.  ``-1`` means unlimited.
    """
    centre = _find(graph, node_name)
    if centre is None:
        return Graph()

    if depth < 0:
        keep_names = get_neighbourhood(graph, node_name)
    else:
        keep_names = _bfs_limited(graph, node_name, depth)

    # Rebuild node objects by name (case-insensitive lookup)
    name_to_node: dict[str, Node] = {
        n.name.lower(): n for n in graph.nodes
    }
    sub = Graph()
    for name in keep_names:
        if name in name_to_node:
            sub.add_node(name_to_node[name])

    for src, dst in graph.edges:
        if src.name.lower() in keep_names and dst.name.lower() in keep_names:
            sub.add_edge(src, dst)

    return sub


def _bfs_limited(graph: Graph, start: str, max_depth: int) -> set[str]:
    """BFS in both directions up to *max_depth* hops from *start*.

    Parameters
    ----------
    graph:     Source graph to traverse.
    start:     Name of the starting node (case-insensitive).
    max_depth: Maximum number of hops to follow in either direction.
                A value of ``0`` returns only the start node itself.
    """
    # Build forward and reverse adjacency maps keyed by lower-case node name
    fwd: dict[str, set[str]] = {n.name.lower(): set() for n in graph.nodes}
    rev: dict[str, set[str]] = {n.name.lower(): set() for n in graph.nodes}
    for src, dst in graph.edges:
        fwd[src.name.lower()].add(dst.name.lower())
        rev[dst.name.lower()].add(src.name.lower())

    visited: dict[str, int] = {start.lower(): 0}
    queue: deque[str] = deque([start.lower()])
    while queue:
        current = queue.popleft()
        dist = visited[current]
        if dist >= max_depth:
            continue
        for neighbour in fwd.get(current, set()) | rev.get(current, set()):
            if neighbour not in visited:
                visited[neighbour] = dist + 1
                queue.append(neighbour)
    return set(visited.keys())
