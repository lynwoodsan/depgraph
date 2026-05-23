"""Highlight specific nodes and their edges in a DependencyGraph."""

from __future__ import annotations

from typing import Iterable, Set, Tuple

from depgraph.graph import DependencyGraph, Node


def highlight_dependencies(
    graph: DependencyGraph,
    root: str,
    *,
    include_reverse: bool = False,
) -> Tuple[Set[str], Set[Tuple[str, str]]]:
    """Return the set of node names and edges reachable from *root*.

    Parameters
    ----------
    graph:
        The full dependency graph to search.
    root:
        Name of the package to start from (case-insensitive).
    include_reverse:
        When *True*, also walk edges in reverse (i.e. packages that depend on
        *root* are included in addition to packages that *root* depends on).

    Returns
    -------
    A tuple of ``(highlighted_nodes, highlighted_edges)`` where node names are
    normalised to lower-case and edges are ``(from_lower, to_lower)`` pairs.
    """
    root_lower = root.lower()

    # Build adjacency maps from the graph.
    forward: dict[str, set[str]] = {}
    reverse: dict[str, set[str]] = {}
    for node in graph.nodes:
        key = node.name.lower()
        forward.setdefault(key, set())
        reverse.setdefault(key, set())

    for src, dst in graph.edges:
        s, d = src.lower(), dst.lower()
        forward.setdefault(s, set()).add(d)
        reverse.setdefault(d, set()).add(s)

    def _bfs(start: str, adjacency: dict[str, set[str]]) -> set[str]:
        visited: set[str] = set()
        queue = [start]
        while queue:
            current = queue.pop()
            if current in visited:
                continue
            visited.add(current)
            queue.extend(adjacency.get(current, set()))
        return visited

    highlighted_nodes = _bfs(root_lower, forward)
    if include_reverse:
        highlighted_nodes |= _bfs(root_lower, reverse)

    highlighted_edges: set[tuple[str, str]] = set()
    for src, dst in graph.edges:
        s, d = src.lower(), dst.lower()
        if s in highlighted_nodes and d in highlighted_nodes:
            highlighted_edges.add((s, d))

    return highlighted_nodes, highlighted_edges


def node_classes(
    graph: DependencyGraph,
    highlighted_nodes: Iterable[str],
) -> dict[str, str]:
    """Map every node name to a CSS class string for SVG rendering.

    Nodes in *highlighted_nodes* receive class ``"node highlighted"``;
    all others receive ``"node dimmed"``.
    """
    lit: set[str] = {n.lower() for n in highlighted_nodes}
    result: dict[str, str] = {}
    for node in graph.nodes:
        key = node.name.lower()
        result[key] = "node highlighted" if key in lit else "node dimmed"
    return result
