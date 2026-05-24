"""Group graph nodes by a shared attribute or naming convention."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, List, Optional

from depgraph.graph import Graph, Node


def group_by_prefix(
    graph: Graph,
    separator: str = "-",
    max_parts: int = 1,
) -> Dict[str, List[Node]]:
    """Group nodes by the leading *max_parts* components of their name.

    For example, with separator='-' and max_parts=1, nodes named
    'django-rest-framework' and 'django-filter' both end up in group 'django'.
    Nodes with no separator are placed in group '' (empty string).
    """
    groups: Dict[str, List[Node]] = defaultdict(list)
    for node in graph.nodes:
        parts = node.name.split(separator)
        key = separator.join(parts[:max_parts]) if len(parts) > max_parts else ""
        groups[key].append(node)
    return dict(groups)


def group_by_function(
    graph: Graph,
    key_fn: Callable[[Node], str],
) -> Dict[str, List[Node]]:
    """Group nodes using an arbitrary callable that maps a Node to a string key."""
    groups: Dict[str, List[Node]] = defaultdict(list)
    for node in graph.nodes:
        groups[key_fn(node)].append(node)
    return dict(groups)


def group_by_depth(
    graph: Graph,
) -> Dict[int, List[Node]]:
    """Group nodes by their BFS depth from root nodes (nodes with no incoming edges).

    Root nodes are at depth 0.  Nodes unreachable from any root are placed at depth -1.
    """
    in_degree: Dict[Node, int] = {n: 0 for n in graph.nodes}
    for src, dst in graph.edges:
        in_degree[dst] = in_degree.get(dst, 0) + 1

    roots = [n for n, deg in in_degree.items() if deg == 0]

    depth_map: Dict[Node, int] = {}
    queue: List[tuple[int, Node]] = [(0, r) for r in roots]
    while queue:
        depth, node = queue.pop(0)
        if node in depth_map:
            continue
        depth_map[node] = depth
        for src, dst in graph.edges:
            if src == node and dst not in depth_map:
                queue.append((depth + 1, dst))

    groups: Dict[int, List[Node]] = defaultdict(list)
    for node in graph.nodes:
        groups[depth_map.get(node, -1)].append(node)
    return dict(groups)


def largest_group(
    groups: Dict[str, List[Node]],
) -> Optional[str]:
    """Return the key of the group with the most nodes, or None if groups is empty."""
    if not groups:
        return None
    return max(groups, key=lambda k: len(groups[k]))
