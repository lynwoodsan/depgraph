"""Graph pruning utilities: remove orphan nodes and redundant edges."""

from __future__ import annotations

from depgraph.graph import Graph, Node


def prune_orphans(graph: Graph) -> Graph:
    """Return a new graph with isolated nodes (no edges) removed.

    A node is considered an orphan if it has no incoming *and* no outgoing
    edges in the graph.
    """
    connected: set[Node] = set()
    for src, dst in graph.edges:
        connected.add(src)
        connected.add(dst)

    pruned = Graph()
    for node in graph.nodes:
        if node in connected:
            pruned.add_node(node)
    for src, dst in graph.edges:
        pruned.add_edge(src, dst)
    return pruned


def prune_transitive_edges(graph: Graph) -> Graph:
    """Return a new graph with redundant transitive edges removed.

    An edge A -> C is redundant if there is already a path A -> ... -> C
    through at least one intermediate node.  This is the *transitive reduction*
    for a DAG.
    """
    # Build adjacency for reachability check (without direct edge)
    def _reachable_without(src: Node, dst: Node) -> bool:
        """BFS: can we reach *dst* from *src* without using the direct edge?"""
        adj: dict[Node, list[Node]] = {}
        for s, d in graph.edges:
            if s == src and d == dst:
                continue  # skip the direct edge we are testing
            adj.setdefault(s, []).append(d)

        visited: set[Node] = set()
        queue = list(adj.get(src, []))
        while queue:
            current = queue.pop()
            if current == dst:
                return True
            if current in visited:
                continue
            visited.add(current)
            queue.extend(adj.get(current, []))
        return False

    reduced = Graph()
    for node in graph.nodes:
        reduced.add_node(node)
    for src, dst in graph.edges:
        if not _reachable_without(src, dst):
            reduced.add_edge(src, dst)
    return reduced


def prune_by_depth(graph: Graph, root: Node, max_depth: int) -> Graph:
    """Return a subgraph containing only nodes within *max_depth* hops from *root*."""
    if max_depth < 0:
        raise ValueError("max_depth must be >= 0")

    adj: dict[Node, list[Node]] = {}
    for src, dst in graph.edges:
        adj.setdefault(src, []).append(dst)

    visited: dict[Node, int] = {}
    queue: list[tuple[Node, int]] = [(root, 0)]
    while queue:
        node, depth = queue.pop(0)
        if node in visited:
            continue
        visited[node] = depth
        if depth < max_depth:
            for neighbour in adj.get(node, []):
                if neighbour not in visited:
                    queue.append((neighbour, depth + 1))

    result = Graph()
    for node in visited:
        result.add_node(node)
    for src, dst in graph.edges:
        if src in visited and dst in visited:
            result.add_edge(src, dst)
    return result
