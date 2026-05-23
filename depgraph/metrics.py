"""Compute per-node metrics for a dependency graph."""

from dataclasses import dataclass, field
from typing import Dict, List

from depgraph.graph import Graph, Node


@dataclass
class NodeMetrics:
    name: str
    in_degree: int = 0
    out_degree: int = 0
    transitive_deps: int = 0
    transitive_dependents: int = 0
    is_root: bool = False
    is_leaf: bool = False
    centrality: float = 0.0


def _reachable(graph: "Graph", start: Node, reverse: bool = False) -> int:
    """Count nodes reachable from *start* (excluding itself)."""
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        for src, dst in graph.edges:
            neighbour = dst if not reverse else src
            other = src if not reverse else dst
            if other == node and neighbour not in visited and neighbour != start:
                visited.add(neighbour)
                stack.append(neighbour)
    return len(visited)


def compute_node_metrics(graph: "Graph") -> Dict[str, NodeMetrics]:
    """Return a mapping of node name -> NodeMetrics for every node."""
    in_deg: Dict[str, int] = {n.name: 0 for n in graph.nodes}
    out_deg: Dict[str, int] = {n.name: 0 for n in graph.nodes}

    for src, dst in graph.edges:
        out_deg[src.name] = out_deg.get(src.name, 0) + 1
        in_deg[dst.name] = in_deg.get(dst.name, 0) + 1

    total = len(graph.nodes)
    result: Dict[str, NodeMetrics] = {}

    for node in graph.nodes:
        td = _reachable(graph, node, reverse=False)
        tdep = _reachable(graph, node, reverse=True)
        centrality = (td + tdep) / (2 * (total - 1)) if total > 1 else 0.0
        result[node.name] = NodeMetrics(
            name=node.name,
            in_degree=in_deg.get(node.name, 0),
            out_degree=out_deg.get(node.name, 0),
            transitive_deps=td,
            transitive_dependents=tdep,
            is_root=in_deg.get(node.name, 0) == 0,
            is_leaf=out_deg.get(node.name, 0) == 0,
            centrality=round(centrality, 4),
        )

    return result


def most_depended_upon(metrics: Dict[str, NodeMetrics], top: int = 5) -> List[NodeMetrics]:
    """Return the *top* nodes sorted by number of transitive dependents."""
    ranked = sorted(metrics.values(), key=lambda m: m.transitive_dependents, reverse=True)
    return ranked[:top]
