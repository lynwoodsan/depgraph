"""Build a dependency graph from resolved packages."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from depgraph.resolver import Package, resolve_package


@dataclass
class Node:
    """A node in the dependency graph representing a single package."""

    name: str
    version: str
    extras: List[str] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.name.lower())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.name.lower() == other.name.lower()

    def __repr__(self) -> str:  # pragma: no cover
        return f"Node({self.name!r}, {self.version!r})"


@dataclass
class DependencyGraph:
    """Directed graph of package dependencies."""

    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: Dict[str, List[str]] = field(default_factory=dict)

    def add_node(self, node: Node) -> None:
        key = node.name.lower()
        if key not in self.nodes:
            self.nodes[key] = node
            self.edges[key] = []

    def add_edge(self, from_name: str, to_name: str) -> None:
        key = from_name.lower()
        if key not in self.edges:
            self.edges[key] = []
        if to_name.lower() not in self.edges[key]:
            self.edges[key].append(to_name.lower())

    def get_dependencies(self, name: str) -> List[Node]:
        key = name.lower()
        return [self.nodes[dep] for dep in self.edges.get(key, []) if dep in self.nodes]

    def all_nodes(self) -> List[Node]:
        return list(self.nodes.values())


def build_graph(
    root_package: str,
    max_depth: Optional[int] = None,
    _visited: Optional[Set[str]] = None,
    _depth: int = 0,
) -> DependencyGraph:
    """Recursively resolve dependencies and build a DependencyGraph."""
    if _visited is None:
        _visited = set()

    graph = DependencyGraph()
    _build_recursive(root_package, graph, _visited, _depth, max_depth)
    return graph


def _build_recursive(
    package_name: str,
    graph: DependencyGraph,
    visited: Set[str],
    depth: int,
    max_depth: Optional[int],
) -> None:
    key = package_name.lower()
    if key in visited:
        return
    if max_depth is not None and depth > max_depth:
        return

    visited.add(key)
    pkg: Optional[Package] = resolve_package(package_name)
    if pkg is None:
        return

    node = Node(name=pkg.name, version=pkg.version)
    graph.add_node(node)

    for dep in pkg.dependencies:
        graph.add_edge(pkg.name, dep.name)
        _build_recursive(dep.name, graph, visited, depth + 1, max_depth)
        dep_node = Node(name=dep.name, version=dep.version)
        graph.add_node(dep_node)
