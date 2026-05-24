"""Compute structural similarity between two dependency graphs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Set, Tuple

from depgraph.graph import Graph


@dataclass
class SimilarityResult:
    """Holds similarity scores between two graphs."""
    node_jaccard: float
    edge_jaccard: float
    common_nodes: Set[str]
    common_edges: Set[Tuple[str, str]]

    @property
    def overall(self) -> float:
        """Simple average of node and edge Jaccard scores."""
        return (self.node_jaccard + self.edge_jaccard) / 2.0


def _node_names(graph: Graph) -> Set[str]:
    return {n.name.lower() for n in graph.nodes}


def _edge_pairs(graph: Graph) -> Set[Tuple[str, str]]:
    return {
        (src.name.lower(), dst.name.lower())
        for src, dst in graph.edges
    }


def _jaccard(a: set, b: set) -> float:
    """Return Jaccard similarity coefficient for two sets."""
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def compute_similarity(g1: Graph, g2: Graph) -> SimilarityResult:
    """Compute structural similarity between *g1* and *g2*.

    Returns a :class:`SimilarityResult` with per-dimension Jaccard scores
    and the sets of shared nodes / edges.
    """
    nodes1 = _node_names(g1)
    nodes2 = _node_names(g2)
    edges1 = _edge_pairs(g1)
    edges2 = _edge_pairs(g2)

    return SimilarityResult(
        node_jaccard=_jaccard(nodes1, nodes2),
        edge_jaccard=_jaccard(edges1, edges2),
        common_nodes=nodes1 & nodes2,
        common_edges=edges1 & edges2,
    )


def most_similar(target: Graph, candidates: list[Graph]) -> Graph | None:
    """Return the graph from *candidates* most similar to *target*.

    Returns ``None`` when *candidates* is empty.
    """
    if not candidates:
        return None
    return max(candidates, key=lambda g: compute_similarity(target, g).overall)
