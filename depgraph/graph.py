"""Core graph data structures for depgraph."""

from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple


class Node:
    """Represents a single package in the dependency graph."""

    def __init__(self, name: str, version: str = "") -> None:
        self.name = name
        self.version = version

    # ------------------------------------------------------------------
    # Identity is case-insensitive on name (PEP 503 normalisation).
    # ------------------------------------------------------------------

    def __hash__(self) -> int:
        return hash(self.name.lower())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Node):
            return self.name.lower() == other.name.lower()
        return NotImplemented

    def __repr__(self) -> str:  # pragma: no cover
        if self.version:
            return f"Node({self.name!r}, {self.version!r})"
        return f"Node({self.name!r})"


class DependencyGraph:
    """Directed graph of package dependencies."""

    def __init__(self) -> None:
        self._nodes: Set[Node] = set()
        # adjacency list: node -> set of direct dependencies
        self._edges: Dict[Node, Set[Node]] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_node(self, node: Node) -> None:
        """Add *node* to the graph (idempotent)."""
        if node not in self._nodes:
            self._nodes.add(node)
            self._edges.setdefault(node, set())

    def add_edge(self, src: Node, dst: Node) -> None:
        """Add a directed edge *src* -> *dst*, adding nodes if absent."""
        self.add_node(src)
        self.add_node(dst)
        self._edges[src].add(dst)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def nodes(self) -> Set[Node]:
        return set(self._nodes)

    @property
    def edges(self) -> List[Tuple[Node, Node]]:
        result: List[Tuple[Node, Node]] = []
        for src, dsts in self._edges.items():
            for dst in dsts:
                result.append((src, dst))
        return result

    def neighbors(self, node: Node) -> Set[Node]:
        """Return the direct successors of *node*."""
        return set(self._edges.get(node, set()))

    def has_node(self, node: Node) -> bool:
        return node in self._nodes

    def has_edge(self, src: Node, dst: Node) -> bool:
        return dst in self._edges.get(src, set())

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._nodes)

    def __iter__(self) -> Iterator[Node]:
        return iter(self._nodes)

    def __repr__(self) -> str:  # pragma: no cover
        return f"DependencyGraph(nodes={len(self._nodes)}, edges={len(self.edges)})"
