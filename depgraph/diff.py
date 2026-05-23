"""Compute the difference between two dependency graphs."""

from dataclasses import dataclass, field
from typing import Set, Tuple

from depgraph.graph import DependencyGraph, Node


@dataclass
class GraphDiff:
    """Result of comparing two dependency graphs."""

    added_nodes: Set[Node] = field(default_factory=set)
    removed_nodes: Set[Node] = field(default_factory=set)
    added_edges: Set[Tuple[Node, Node]] = field(default_factory=set)
    removed_edges: Set[Tuple[Node, Node]] = field(default_factory=set)

    @property
    def has_changes(self) -> bool:
        """Return True if there are any differences."""
        return bool(
            self.added_nodes
            or self.removed_nodes
            or self.added_edges
            or self.removed_edges
        )

    def summary(self) -> str:
        """Return a human-readable summary of changes."""
        lines = []
        for node in sorted(self.added_nodes, key=lambda n: n.name):
            lines.append(f"+ node: {node.name}")
        for node in sorted(self.removed_nodes, key=lambda n: n.name):
            lines.append(f"- node: {node.name}")
        for src, dst in sorted(self.added_edges, key=lambda e: (e[0].name, e[1].name)):
            lines.append(f"+ edge: {src.name} -> {dst.name}")
        for src, dst in sorted(self.removed_edges, key=lambda e: (e[0].name, e[1].name)):
            lines.append(f"- edge: {src.name} -> {dst.name}")
        return "\n".join(lines) if lines else "(no changes)"


def diff_graphs(old: DependencyGraph, new: DependencyGraph) -> GraphDiff:
    """Compare two dependency graphs and return their diff.

    Args:
        old: The baseline graph.
        new: The updated graph.

    Returns:
        A GraphDiff describing added/removed nodes and edges.
    """
    old_nodes = set(old.nodes)
    new_nodes = set(new.nodes)

    old_edges = set(old.edges)
    new_edges = set(new.edges)

    return GraphDiff(
        added_nodes=new_nodes - old_nodes,
        removed_nodes=old_nodes - new_nodes,
        added_edges=new_edges - old_edges,
        removed_edges=old_edges - new_edges,
    )
