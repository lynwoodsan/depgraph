"""Detect redundant (transitive) edges in a dependency graph.

An edge A -> C is redundant if there is another path from A to C
that goes through at least one intermediate node.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set, Tuple

from depgraph.graph import Graph, Node


@dataclass
class RedundancyReport:
    """Results of a redundancy analysis."""

    redundant_edges: List[Tuple[Node, Node]] = field(default_factory=list)
    total_edges: int = 0

    @property
    def count(self) -> int:
        return len(self.redundant_edges)

    @property
    def ratio(self) -> float:
        """Fraction of edges that are redundant (0.0 – 1.0)."""
        if self.total_edges == 0:
            return 0.0
        return self.count / self.total_edges


def _reachable_without_direct(graph: Graph, src: Node, dst: Node) -> bool:
    """Return True if *dst* is reachable from *src* without the direct edge."""
    neighbours = graph.edges.get(src, set())
    # BFS / DFS through all neighbours except dst (only as a direct step)
    visited: Set[Node] = set()
    stack = [n for n in neighbours if n != dst]
    while stack:
        current = stack.pop()
        if current == dst:
            return True
        if current in visited:
            continue
        visited.add(current)
        stack.extend(graph.edges.get(current, set()))
    return False


def find_redundant_edges(graph: Graph) -> RedundancyReport:
    """Identify all edges that are made redundant by a longer path."""
    redundant: List[Tuple[Node, Node]] = []
    total = sum(len(targets) for targets in graph.edges.values())

    for src, targets in graph.edges.items():
        for dst in targets:
            if _reachable_without_direct(graph, src, dst):
                redundant.append((src, dst))

    return RedundancyReport(redundant_edges=redundant, total_edges=total)


def most_redundant_sources(report: RedundancyReport, top_n: int = 5) -> List[Tuple[Node, int]]:
    """Return the *top_n* nodes with the most outgoing redundant edges."""
    counts: dict[Node, int] = {}
    for src, _ in report.redundant_edges:
        counts[src] = counts.get(src, 0) + 1
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]
