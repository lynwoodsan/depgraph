"""Ancestor and descendant traversal utilities for dependency graphs."""

from __future__ import annotations
from typing import Set
from depgraph.graph import Graph, Node


def get_ancestors(graph: Graph, node_name: str) -> Set[str]:
    """Return the set of all ancestor node names (nodes that depend on *node_name*).

    Performs a reverse BFS from the given node.
    """
    target = _find(graph, node_name)
    if target is None:
        return set()

    # Build reverse adjacency: child -> set of parents
    reverse: dict[str, set[str]] = {n.name.lower(): set() for n in graph.nodes}
    for src, dst in graph.edges:
        reverse.setdefault(dst.name.lower(), set()).add(src.name.lower())
        reverse.setdefault(src.name.lower(), set())  # ensure key exists

    visited: Set[str] = set()
    queue = [target.name.lower()]
    while queue:
        current = queue.pop()
        for parent in reverse.get(current, set()):
            if parent not in visited:
                visited.add(parent)
                queue.append(parent)
    return visited


def get_descendants(graph: Graph, node_name: str) -> Set[str]:
    """Return the set of all descendant node names (nodes that *node_name* depends on).

    Performs a forward BFS from the given node.
    """
    target = _find(graph, node_name)
    if target is None:
        return set()

    # Build forward adjacency
    forward: dict[str, set[str]] = {n.name.lower(): set() for n in graph.nodes}
    for src, dst in graph.edges:
        forward.setdefault(src.name.lower(), set()).add(dst.name.lower())

    visited: Set[str] = set()
    queue = [target.name.lower()]
    while queue:
        current = queue.pop()
        for child in forward.get(current, set()):
            if child not in visited:
                visited.add(child)
                queue.append(child)
    return visited


def get_neighbourhood(graph: Graph, node_name: str) -> Set[str]:
    """Return ancestors ∪ descendants ∪ {node_name} (the full neighbourhood)."""
    target = _find(graph, node_name)
    if target is None:
        return set()
    return (
        get_ancestors(graph, node_name)
        | get_descendants(graph, node_name)
        | {target.name.lower()}
    )


def _find(graph: Graph, name: str) -> Node | None:
    key = name.lower()
    for node in graph.nodes:
        if node.name.lower() == key:
            return node
    return None
