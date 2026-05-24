"""Rank nodes in a dependency graph by various importance criteria."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from depgraph.graph import Graph


@dataclass
class RankedNode:
    name: str
    score: float
    rank: int = field(default=0)


def _in_degree(graph: Graph) -> Dict[str, int]:
    counts: Dict[str, int] = {n.name: 0 for n in graph.nodes}
    for src, dst in graph.edges:
        counts[dst.name] = counts.get(dst.name, 0) + 1
    return counts


def _out_degree(graph: Graph) -> Dict[str, int]:
    counts: Dict[str, int] = {n.name: 0 for n in graph.nodes}
    for src, dst in graph.edges:
        counts[src.name] = counts.get(src.name, 0) + 1
    return counts


def rank_by_in_degree(graph: Graph) -> List[RankedNode]:
    """Rank nodes by how many other nodes depend on them (most depended-upon first)."""
    degrees = _in_degree(graph)
    scored = [
        RankedNode(name=name, score=float(deg))
        for name, deg in degrees.items()
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    for i, r in enumerate(scored, start=1):
        r.rank = i
    return scored


def rank_by_out_degree(graph: Graph) -> List[RankedNode]:
    """Rank nodes by how many dependencies they have (most dependencies first)."""
    degrees = _out_degree(graph)
    scored = [
        RankedNode(name=name, score=float(deg))
        for name, deg in degrees.items()
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    for i, r in enumerate(scored, start=1):
        r.rank = i
    return scored


def rank_by_combined(graph: Graph, in_weight: float = 0.7, out_weight: float = 0.3) -> List[RankedNode]:
    """Rank nodes by a weighted combination of in-degree and out-degree."""
    in_deg = _in_degree(graph)
    out_deg = _out_degree(graph)
    names = {n.name for n in graph.nodes}
    scored = [
        RankedNode(
            name=name,
            score=in_weight * in_deg.get(name, 0) + out_weight * out_deg.get(name, 0),
        )
        for name in names
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    for i, r in enumerate(scored, start=1):
        r.rank = i
    return scored


def top_n(ranked: List[RankedNode], n: int) -> List[RankedNode]:
    """Return the top-n ranked nodes."""
    return ranked[:n]
