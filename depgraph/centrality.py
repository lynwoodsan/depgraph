"""Centrality measures for dependency graphs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from depgraph.graph import Graph


@dataclass
class CentralityScores:
    """Centrality scores for all nodes in a graph."""

    degree: Dict[str, float]
    betweenness: Dict[str, float]
    closeness: Dict[str, float]

    def top_degree(self, n: int = 5) -> List[str]:
        """Return top-n nodes by degree centrality."""
        return sorted(self.degree, key=lambda k: self.degree[k], reverse=True)[:n]

    def top_betweenness(self, n: int = 5) -> List[str]:
        """Return top-n nodes by betweenness centrality."""
        return sorted(self.betweenness, key=lambda k: self.betweenness[k], reverse=True)[:n]

    def top_closeness(self, n: int = 5) -> List[str]:
        """Return top-n nodes by closeness centrality."""
        return sorted(self.closeness, key=lambda k: self.closeness[k], reverse=True)[:n]


def _all_pairs_shortest_paths(graph: Graph) -> Dict[str, Dict[str, int]]:
    """BFS-based all-pairs shortest path lengths (directed graph)."""
    nodes = [n.name for n in graph.nodes]
    dist: Dict[str, Dict[str, int]] = {}
    for source in nodes:
        visited: Dict[str, int] = {source: 0}
        queue = [source]
        while queue:
            current = queue.pop(0)
            for neighbour in [e.target.name for e in graph.edges if e.source.name == current]:
                if neighbour not in visited:
                    visited[neighbour] = visited[current] + 1
                    queue.append(neighbour)
        dist[source] = visited
    return dist


def compute_centrality(graph: Graph) -> CentralityScores:
    """Compute degree, betweenness, and closeness centrality for all nodes."""
    nodes = [n.name for n in graph.nodes]
    n = len(nodes)
    if n == 0:
        return CentralityScores(degree={}, betweenness={}, closeness={})

    # Degree centrality: (in_degree + out_degree) / (2 * (n - 1))
    in_deg: Dict[str, int] = {name: 0 for name in nodes}
    out_deg: Dict[str, int] = {name: 0 for name in nodes}
    for edge in graph.edges:
        out_deg[edge.source.name] = out_deg.get(edge.source.name, 0) + 1
        in_deg[edge.target.name] = in_deg.get(edge.target.name, 0) + 1

    denom = max(2 * (n - 1), 1)
    degree = {name: (in_deg[name] + out_deg[name]) / denom for name in nodes}

    dist = _all_pairs_shortest_paths(graph)

    # Closeness centrality: (n - 1) / sum of distances from node
    closeness: Dict[str, float] = {}
    for name in nodes:
        reachable = {k: v for k, v in dist[name].items() if k != name}
        total = sum(reachable.values())
        closeness[name] = (len(reachable) / total) if total > 0 else 0.0

    # Betweenness centrality: fraction of shortest paths passing through node
    between: Dict[str, float] = {name: 0.0 for name in nodes}
    for src in nodes:
        for tgt in nodes:
            if src == tgt:
                continue
            if tgt not in dist[src]:
                continue
            path_len = dist[src][tgt]
            for mid in nodes:
                if mid in (src, tgt):
                    continue
                if mid in dist[src] and tgt in dist[mid]:
                    if dist[src][mid] + dist[mid][tgt] == path_len:
                        between[mid] += 1.0

    max_between = max(between.values(), default=1.0) or 1.0
    betweenness = {name: v / max_between for name, v in between.items()}

    return CentralityScores(degree=degree, betweenness=betweenness, closeness=closeness)
