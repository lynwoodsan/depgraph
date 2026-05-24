"""Edge and node weighting utilities for depgraph."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Optional, Tuple

from depgraph.graph import Graph, Node
from depgraph.metrics import _reachable


@dataclass
class WeightedGraph:
    """A graph decorated with numeric weights on nodes and edges."""

    graph: Graph
    node_weights: Dict[str, float] = field(default_factory=dict)
    edge_weights: Dict[Tuple[str, str], float] = field(default_factory=dict)

    def node_weight(self, name: str) -> float:
        return self.node_weights.get(name.lower(), 1.0)

    def edge_weight(self, src: str, dst: str) -> float:
        return self.edge_weights.get((src.lower(), dst.lower()), 1.0)


def weight_by_out_degree(graph: Graph) -> WeightedGraph:
    """Assign each node a weight equal to its out-degree (number of deps)."""
    weights: Dict[str, float] = {}
    for node in graph.nodes:
        weights[node.name.lower()] = float(len(graph.edges_from(node)))
    return WeightedGraph(graph=graph, node_weights=weights)


def weight_by_reachability(graph: Graph) -> WeightedGraph:
    """Assign each node a weight equal to the number of nodes it can reach."""
    weights: Dict[str, float] = {}
    for node in graph.nodes:
        reachable = _reachable(graph, node)
        weights[node.name.lower()] = float(len(reachable))
    return WeightedGraph(graph=graph, node_weights=weights)


def weight_by_function(
    graph: Graph,
    node_fn: Optional[Callable[[Node], float]] = None,
    edge_fn: Optional[Callable[[Node, Node], float]] = None,
) -> WeightedGraph:
    """Assign weights using caller-supplied functions."""
    node_weights: Dict[str, float] = {}
    edge_weights: Dict[Tuple[str, str], float] = {}

    for node in graph.nodes:
        if node_fn is not None:
            node_weights[node.name.lower()] = node_fn(node)

    for src, dst in graph.edges:
        if edge_fn is not None:
            edge_weights[(src.name.lower(), dst.name.lower())] = edge_fn(src, dst)

    return WeightedGraph(graph=graph, node_weights=node_weights, edge_weights=edge_weights)


def heaviest_nodes(wg: WeightedGraph, top_n: int = 5) -> list[Tuple[str, float]]:
    """Return the *top_n* nodes sorted by descending weight."""
    ranked = sorted(
        ((name, w) for name, w in wg.node_weights.items()),
        key=lambda t: t[1],
        reverse=True,
    )
    return ranked[:top_n]
