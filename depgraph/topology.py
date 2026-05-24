"""Topological ordering and layer assignment for dependency graphs."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from depgraph.graph import Graph


@dataclass
class TopologicalOrder:
    """Result of a topological sort over a dependency graph."""

    order: List[str] = field(default_factory=list)
    layers: Dict[int, List[str]] = field(default_factory=dict)
    has_cycle: bool = False

    def layer_of(self, name: str) -> Optional[int]:
        """Return the layer index for *name*, or None if not found."""
        for layer_idx, nodes in self.layers.items():
            for n in nodes:
                if n.lower() == name.lower():
                    return layer_idx
        return None


def topological_sort(graph: Graph) -> TopologicalOrder:
    """Kahn's algorithm — returns a TopologicalOrder.

    If the graph contains a cycle ``has_cycle`` is set to True and
    ``order`` will contain only the nodes that *could* be ordered.
    """
    node_names = [n.name for n in graph.nodes]
    in_deg: Dict[str, int] = {n: 0 for n in node_names}

    for src, dst in graph.edges:
        if dst.name in in_deg:
            in_deg[dst.name] += 1

    queue: deque[str] = deque(
        name for name, deg in in_deg.items() if deg == 0
    )
    order: List[str] = []

    while queue:
        name = queue.popleft()
        order.append(name)
        for src, dst in graph.edges:
            if src.name == name:
                in_deg[dst.name] -= 1
                if in_deg[dst.name] == 0:
                    queue.append(dst.name)

    has_cycle = len(order) != len(node_names)

    # Build layers via longest-path assignment
    layers: Dict[str, int] = {}
    for name in order:
        # layer = max(layer of predecessors) + 1
        preds = [src.name for src, dst in graph.edges if dst.name == name]
        if not preds:
            layers[name] = 0
        else:
            layers[name] = max(layers.get(p, 0) for p in preds) + 1

    layer_map: Dict[int, List[str]] = {}
    for name, idx in layers.items():
        layer_map.setdefault(idx, []).append(name)

    return TopologicalOrder(order=order, layers=layer_map, has_cycle=has_cycle)


def layer_count(topo: TopologicalOrder) -> int:
    """Return the total number of distinct layers."""
    return len(topo.layers)


def nodes_in_layer(topo: TopologicalOrder, layer: int) -> List[str]:
    """Return node names assigned to *layer* (empty list if none)."""
    return list(topo.layers.get(layer, []))
