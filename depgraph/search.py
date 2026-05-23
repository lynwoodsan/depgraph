"""Search utilities for finding nodes and paths in a DependencyGraph."""

from __future__ import annotations

from collections import deque
from typing import List, Optional

from depgraph.graph import DependencyGraph, Node


def find_node(graph: DependencyGraph, name: str) -> Optional[Node]:
    """Return the Node whose name matches *name* (case-insensitive), or None."""
    key = name.lower()
    for node in graph.nodes:
        if node.name.lower() == key:
            return node
    return None


def find_by_prefix(graph: DependencyGraph, prefix: str) -> List[Node]:
    """Return all nodes whose names start with *prefix* (case-insensitive)."""
    key = prefix.lower()
    return [n for n in graph.nodes if n.name.lower().startswith(key)]


def shortest_path(
    graph: DependencyGraph, source: str, target: str
) -> Optional[List[Node]]:
    """Return the shortest directed path from *source* to *target* node names.

    Returns a list of Node objects from source to target (inclusive), or
    ``None`` if no path exists or either node is absent.
    """
    src = find_node(graph, source)
    tgt = find_node(graph, target)
    if src is None or tgt is None:
        return None
    if src == tgt:
        return [src]

    # BFS over directed edges
    queue: deque[Node] = deque([src])
    came_from: dict[Node, Optional[Node]] = {src: None}

    while queue:
        current = queue.popleft()
        for neighbour in graph.neighbors(current):
            if neighbour not in came_from:
                came_from[neighbour] = current
                if neighbour == tgt:
                    # Reconstruct path
                    path: List[Node] = []
                    node: Optional[Node] = tgt
                    while node is not None:
                        path.append(node)
                        node = came_from[node]
                    path.reverse()
                    return path
                queue.append(neighbour)
    return None


def all_paths(
    graph: DependencyGraph, source: str, target: str
) -> List[List[Node]]:
    """Return all simple directed paths from *source* to *target*."""
    src = find_node(graph, source)
    tgt = find_node(graph, target)
    if src is None or tgt is None:
        return []

    results: List[List[Node]] = []

    def dfs(current: Node, path: List[Node], visited: set) -> None:
        if current == tgt:
            results.append(list(path))
            return
        for neighbour in graph.neighbors(current):
            if neighbour not in visited:
                visited.add(neighbour)
                path.append(neighbour)
                dfs(neighbour, path, visited)
                path.pop()
                visited.discard(neighbour)

    dfs(src, [src], {src})
    return results
