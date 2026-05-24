"""Impact analysis: given a changed node, find everything affected downstream."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, List, Set

from depgraph.graph import Graph, Node


@dataclass(frozen=True)
class ImpactResult:
    """Result of an impact analysis for a single changed node."""

    root: Node
    affected_nodes: FrozenSet[Node]
    affected_edges: FrozenSet[tuple]
    depth_map: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def count(self) -> int:
        return len(self.affected_nodes)


def _bfs_reverse(graph: Graph, start: Node) -> dict[Node, int]:
    """BFS over reversed edges (dependents of *start*), returning depth map."""
    visited: dict[Node, int] = {start: 0}
    queue: list[tuple[Node, int]] = [(start, 0)]

    # Build reverse adjacency once
    reverse: dict[Node, list[Node]] = {n: [] for n in graph.nodes}
    for src, dst in graph.edges:
        reverse[dst].append(src)

    while queue:
        current, depth = queue.pop(0)
        for neighbour in reverse.get(current, []):
            if neighbour not in visited:
                visited[neighbour] = depth + 1
                queue.append((neighbour, depth + 1))

    return visited


def analyse_impact(graph: Graph, changed_package: str) -> ImpactResult:
    """Return every node/edge that would be affected if *changed_package* changed.

    A node is *affected* when it (transitively) depends on *changed_package*,
    i.e. there is a directed path from that node to *changed_package*.
    """
    target = next(
        (n for n in graph.nodes if n.name.lower() == changed_package.lower()), None
    )
    if target is None:
        return ImpactResult(
            root=Node(changed_package),
            affected_nodes=frozenset(),
            affected_edges=frozenset(),
            depth_map={},
        )

    depth_map = _bfs_reverse(graph, target)
    affected_nodes: FrozenSet[Node] = frozenset(depth_map.keys())

    affected_edges: Set[tuple] = set()
    for src, dst in graph.edges:
        if src in affected_nodes and dst in affected_nodes:
            affected_edges.add((src, dst))

    return ImpactResult(
        root=target,
        affected_nodes=affected_nodes,
        affected_edges=frozenset(affected_edges),
        depth_map=depth_map,
    )


def most_impactful(graph: Graph, top_n: int = 5) -> List[tuple[Node, int]]:
    """Rank nodes by how many others would be impacted if they changed."""
    scores: list[tuple[Node, int]] = []
    for node in graph.nodes:
        result = analyse_impact(graph, node.name)
        # Subtract 1 so the node itself is not counted as an impact on itself
        scores.append((node, result.count - 1))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]
