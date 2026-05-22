"""Filter utilities for pruning dependency graphs."""

from __future__ import annotations

from typing import Optional, Set

from depgraph.graph import DependencyGraph, Node


def filter_by_depth(
    graph: DependencyGraph,
    root: str,
    max_depth: int,
) -> DependencyGraph:
    """Return a new graph containing only nodes reachable from *root*
    within *max_depth* hops.

    Parameters
    ----------
    graph:
        Source dependency graph.
    root:
        Name of the root package to start traversal from.
    max_depth:
        Maximum number of edges to follow (inclusive). 0 returns only the
        root node; 1 returns the root and its direct dependencies, etc.
    """
    if max_depth < 0:
        raise ValueError("max_depth must be >= 0")

    root_node = Node(root)
    if root_node not in graph.nodes:
        raise KeyError(f"Package {root!r} not found in graph")

    visited: Set[Node] = set()
    frontier = {root_node}
    depth = 0

    while frontier and depth <= max_depth:
        visited |= frontier
        if depth == max_depth:
            break
        next_frontier: Set[Node] = set()
        for node in frontier:
            for neighbour in graph.dependencies_of(node.name):
                if neighbour not in visited:
                    next_frontier.add(neighbour)
        frontier = next_frontier
        depth += 1

    new_graph = DependencyGraph()
    for node in visited:
        new_graph.add_node(node.name)
    for node in visited:
        for dep in graph.dependencies_of(node.name):
            if dep in visited:
                new_graph.add_edge(node.name, dep.name)

    return new_graph


def filter_by_packages(
    graph: DependencyGraph,
    include: Optional[Set[str]] = None,
    exclude: Optional[Set[str]] = None,
) -> DependencyGraph:
    """Return a new graph keeping only *include* packages (if given) and
    removing *exclude* packages (if given).  Edges whose source or target
    has been removed are also dropped.
    """
    keep: Set[Node] = set()
    for node in graph.nodes:
        if include is not None and node.name.lower() not in {n.lower() for n in include}:
            continue
        if exclude is not None and node.name.lower() in {n.lower() for n in exclude}:
            continue
        keep.add(node)

    new_graph = DependencyGraph()
    for node in keep:
        new_graph.add_node(node.name)
    for node in keep:
        for dep in graph.dependencies_of(node.name):
            if dep in keep:
                new_graph.add_edge(node.name, dep.name)

    return new_graph
