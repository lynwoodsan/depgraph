"""Core graph data structures for dependency representation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set


@dataclass
class Node:
    """A single package node in the dependency graph."""

    name: str

    def __hash__(self) -> int:
        return hash(self.name.lower())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.name.lower() == other.name.lower()

    def __repr__(self) -> str:
        return f"Node({self.name!r})"


class DependencyGraph:
    """Directed graph of package dependencies."""

    def __init__(self) -> None:
        self._nodes: Dict[str, Node] = {}
        self._edges: Dict[str, Set[str]] = {}

    def add_node(self, name: str) -> Node:
        key = name.lower()
        if key not in self._nodes:
            self._nodes[key] = Node(name)
            self._edges[key] = set()
        return self._nodes[key]

    def add_edge(self, from_name: str, to_name: str) -> None:
        self.add_node(from_name)
        self.add_node(to_name)
        self._edges[from_name.lower()].add(to_name.lower())

    @property
    def nodes(self) -> List[Node]:
        return list(self._nodes.values())

    @property
    def edges(self) -> List[tuple[str, str]]:
        result = []
        for src, targets in self._edges.items():
            for tgt in targets:
                result.append((self._nodes[src].name, self._nodes[tgt].name))
        return result

    def dependencies_of(self, name: str) -> List[str]:
        key = name.lower()
        if key not in self._edges:
            return []
        return [self._nodes[t].name for t in self._edges[key]]

    def dependents_of(self, name: str) -> List[str]:
        key = name.lower()
        return [
            self._nodes[src].name
            for src, targets in self._edges.items()
            if key in targets
        ]

    def roots(self) -> List[str]:
        """Return nodes that are not depended upon by any other node."""
        all_targets: Set[str] = set()
        for targets in self._edges.values():
            all_targets |= targets
        return [
            node.name
            for key, node in self._nodes.items()
            if key not in all_targets
        ]

    def leaves(self) -> List[str]:
        """Return nodes that have no outgoing dependencies."""
        return [
            node.name
            for key, node in self._nodes.items()
            if not self._edges.get(key)
        ]

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, name: str) -> bool:
        return name.lower() in self._nodes
