"""Cycle detection utilities for dependency graphs."""

from typing import List, Optional
from depgraph.graph import Graph, Node


def find_cycles(graph: Graph) -> List[List[Node]]:
    """Return a list of cycles found in the graph.

    Each cycle is represented as a list of nodes forming a closed path.
    If no cycles exist, returns an empty list.
    """
    visited = set()
    rec_stack = set()
    cycles: List[List[Node]] = []

    def dfs(node: Node, path: List[Node]) -> None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                dfs(neighbor, path)
            elif neighbor in rec_stack:
                # Found a cycle; extract it from the current path
                cycle_start = path.index(neighbor)
                cycles.append(list(path[cycle_start:]))

        path.pop()
        rec_stack.discard(node)

    for node in graph.nodes:
        if node not in visited:
            dfs(node, [])

    return cycles


def has_cycle(graph: Graph) -> bool:
    """Return True if the graph contains at least one cycle."""
    return len(find_cycles(graph)) > 0


def find_cycle_nodes(graph: Graph) -> List[Node]:
    """Return a flat, deduplicated list of all nodes involved in any cycle."""
    involved: List[Node] = []
    seen = set()
    for cycle in find_cycles(graph):
        for node in cycle:
            if node not in seen:
                seen.add(node)
                involved.append(node)
    return involved


def shortest_cycle(graph: Graph) -> Optional[List[Node]]:
    """Return the shortest cycle found, or None if the graph is acyclic."""
    cycles = find_cycles(graph)
    if not cycles:
        return None
    return min(cycles, key=len)
