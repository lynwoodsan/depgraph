"""Compute statistics and metrics for a dependency graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from depgraph.graph import Graph


@dataclass
class GraphStats:
    node_count: int = 0
    edge_count: int = 0
    max_depth: int = 0
    root_nodes: List[str] = field(default_factory=list)
    leaf_nodes: List[str] = field(default_factory=list)
    most_depended_on: List[tuple] = field(default_factory=list)  # (name, in_degree)


def _in_degrees(graph: Graph) -> Dict[str, int]:
    """Return a mapping of node name -> number of incoming edges."""
    counts: Dict[str, int] = {n.name.lower(): 0 for n in graph.nodes}
    for src, dst in graph.edges:
        counts[dst.name.lower()] = counts.get(dst.name.lower(), 0) + 1
    return counts


def _out_degrees(graph: Graph) -> Dict[str, int]:
    """Return a mapping of node name -> number of outgoing edges."""
    counts: Dict[str, int] = {n.name.lower(): 0 for n in graph.nodes}
    for src, dst in graph.edges:
        counts[src.name.lower()] = counts.get(src.name.lower(), 0) + 1
    return counts


def _max_depth(graph: Graph, roots: List[str]) -> int:
    """BFS from each root to find the longest shortest path depth."""
    if not roots:
        return 0
    adjacency: Dict[str, List[str]] = {n.name.lower(): [] for n in graph.nodes}
    for src, dst in graph.edges:
        adjacency[src.name.lower()].append(dst.name.lower())

    max_d = 0
    for root in roots:
        visited = {root: 0}
        queue = [root]
        while queue:
            current = queue.pop(0)
            for neighbour in adjacency.get(current, []):
                if neighbour not in visited:
                    visited[neighbour] = visited[current] + 1
                    if visited[neighbour] > max_d:
                        max_d = visited[neighbour]
                    queue.append(neighbour)
    return max_d


def compute_stats(graph: Graph, top_n: int = 5) -> GraphStats:
    """Compute and return statistics for *graph*."""
    in_deg = _in_degrees(graph)
    out_deg = _out_degrees(graph)

    root_nodes = [n.name for n in graph.nodes if in_deg.get(n.name.lower(), 0) == 0]
    leaf_nodes = [n.name for n in graph.nodes if out_deg.get(n.name.lower(), 0) == 0]

    sorted_by_indegree = sorted(
        ((name, deg) for name, deg in in_deg.items() if deg > 0),
        key=lambda x: x[1],
        reverse=True,
    )
    most_depended_on = sorted_by_indegree[:top_n]

    depth = _max_depth(graph, [r.lower() for r in root_nodes])

    return GraphStats(
        node_count=len(graph.nodes),
        edge_count=len(graph.edges),
        max_depth=depth,
        root_nodes=sorted(root_nodes),
        leaf_nodes=sorted(leaf_nodes),
        most_depended_on=most_depended_on,
    )
