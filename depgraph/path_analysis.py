"""Path analysis utilities: critical paths, bottlenecks, and path statistics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from depgraph.graph import Graph, Node


@dataclass
class PathStats:
    """Statistics about paths through the graph."""

    longest_path: List[str] = field(default_factory=list)
    longest_path_length: int = 0
    bottlenecks: List[str] = field(default_factory=list)
    path_counts: Dict[str, int] = field(default_factory=dict)


def _all_paths_from(graph: Graph, start: str, visited: frozenset) -> List[List[str]]:
    """Return all simple paths starting from *start*."""
    neighbours = [
        dst for (src, dst) in graph.edges if src.lower() == start.lower()
    ]
    if not neighbours:
        return [[start]]
    paths: List[List[str]] = []
    for nb in neighbours:
        if nb.lower() in visited:
            continue
        sub = _all_paths_from(graph, nb, visited | {nb.lower()})
        for p in sub:
            paths.append([start] + p)
    return paths if paths else [[start]]


def find_longest_path(graph: Graph) -> List[str]:
    """Return the longest simple path (by node count) in *graph*."""
    roots = {
        n.name for n in graph.nodes
        if not any(dst.lower() == n.name.lower() for (_, dst) in graph.edges)
    }
    if not roots:
        roots = {n.name for n in graph.nodes}
    best: List[str] = []
    for root in roots:
        for path in _all_paths_from(graph, root, frozenset({root.lower()})):
            if len(path) > len(best):
                best = path
    return best


def count_paths_through(graph: Graph) -> Dict[str, int]:
    """Count how many distinct source-to-leaf paths pass through each node."""
    roots = {
        n.name for n in graph.nodes
        if not any(dst.lower() == n.name.lower() for (_, dst) in graph.edges)
    }
    if not roots:
        roots = {n.name for n in graph.nodes}
    counts: Dict[str, int] = {n.name: 0 for n in graph.nodes}
    for root in roots:
        for path in _all_paths_from(graph, root, frozenset({root.lower()})):
            for node_name in path:
                if node_name in counts:
                    counts[node_name] += 1
    return counts


def find_bottlenecks(graph: Graph, threshold: Optional[int] = None) -> List[str]:
    """Return nodes that appear in many paths (above *threshold*)."""
    counts = count_paths_through(graph)
    if not counts:
        return []
    if threshold is None:
        threshold = max(counts.values()) // 2 if counts else 0
    return sorted(
        (name for name, cnt in counts.items() if cnt > threshold),
        key=lambda n: counts[n],
        reverse=True,
    )


def compute_path_stats(graph: Graph) -> PathStats:
    """Compute a full PathStats summary for *graph*."""
    longest = find_longest_path(graph)
    counts = count_paths_through(graph)
    bottlenecks = find_bottlenecks(graph)
    return PathStats(
        longest_path=longest,
        longest_path_length=len(longest),
        bottlenecks=bottlenecks,
        path_counts=counts,
    )
