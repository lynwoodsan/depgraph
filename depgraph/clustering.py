"""Cluster graph nodes using simple community-detection heuristics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set

from depgraph.graph import Graph, Node


@dataclass
class Cluster:
    """A named group of nodes that form a logical community."""

    name: str
    nodes: FrozenSet[str] = field(default_factory=frozenset)

    def __len__(self) -> int:  # pragma: no cover
        return len(self.nodes)

    def __contains__(self, item: str) -> bool:
        return item.lower() in {n.lower() for n in self.nodes}


def _neighbours(graph: Graph, name: str) -> Set[str]:
    """Return all directly connected node names (both directions)."""
    result: Set[str] = set()
    for src, dst in graph.edges:
        if src.lower() == name.lower():
            result.add(dst)
        if dst.lower() == name.lower():
            result.add(src)
    return result


def cluster_by_connectivity(graph: Graph) -> List[Cluster]:
    """Partition the graph into connected components (undirected view)."""
    visited: Set[str] = set()
    components: List[Set[str]] = []

    all_names = [n.name for n in graph.nodes]

    for name in all_names:
        key = name.lower()
        if key in visited:
            continue
        component: Set[str] = set()
        queue = [name]
        while queue:
            current = queue.pop()
            ck = current.lower()
            if ck in visited:
                continue
            visited.add(ck)
            component.add(current)
            for nb in _neighbours(graph, current):
                if nb.lower() not in visited:
                    queue.append(nb)
        components.append(component)

    return [
        Cluster(name=f"cluster_{i}", nodes=frozenset(comp))
        for i, comp in enumerate(components)
    ]


def cluster_by_prefix(graph: Graph, sep: str = ".") -> Dict[str, Cluster]:
    """Group nodes by the first segment of their name split on *sep*."""
    groups: Dict[str, Set[str]] = {}
    for node in graph.nodes:
        prefix = node.name.split(sep)[0]
        groups.setdefault(prefix, set()).add(node.name)
    return {
        prefix: Cluster(name=prefix, nodes=frozenset(members))
        for prefix, members in groups.items()
    }


def largest_cluster(clusters: List[Cluster]) -> Cluster | None:
    """Return the cluster with the most nodes, or *None* for an empty list."""
    if not clusters:
        return None
    return max(clusters, key=lambda c: len(c.nodes))
