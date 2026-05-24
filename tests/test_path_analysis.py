"""Tests for depgraph.path_analysis."""

import pytest
from depgraph.graph import Graph, Node
from depgraph.path_analysis import (
    find_longest_path,
    count_paths_through,
    find_bottlenecks,
    compute_path_stats,
)


def _chain_graph() -> Graph:
    """A -> B -> C -> D"""
    g = Graph()
    for name in ("A", "B", "C", "D"):
        g.add_node(Node(name))
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("C", "D")
    return g


def _diamond_graph() -> Graph:
    """A -> B, A -> C, B -> D, C -> D"""
    g = Graph()
    for name in ("A", "B", "C", "D"):
        g.add_node(Node(name))
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")
    g.add_edge("C", "D")
    return g


def _single_node_graph() -> Graph:
    g = Graph()
    g.add_node(Node("solo"))
    return g


def test_find_longest_path_chain():
    path = find_longest_path(_chain_graph())
    assert len(path) == 4
    assert path[0] == "A"
    assert path[-1] == "D"


def test_find_longest_path_diamond():
    path = find_longest_path(_diamond_graph())
    assert len(path) == 3
    assert path[0] == "A"
    assert path[-1] == "D"


def test_find_longest_path_single_node():
    path = find_longest_path(_single_node_graph())
    assert path == ["solo"]


def test_count_paths_through_chain():
    counts = count_paths_through(_chain_graph())
    # In a chain every node appears in exactly one path
    assert counts["A"] == 1
    assert counts["D"] == 1


def test_count_paths_through_diamond():
    counts = count_paths_through(_diamond_graph())
    # A appears in both paths (A->B->D and A->C->D)
    assert counts["A"] == 2
    # D is a leaf, appears in both paths too
    assert counts["D"] == 2
    # B and C each appear in one path
    assert counts["B"] == 1
    assert counts["C"] == 1


def test_find_bottlenecks_diamond():
    bottlenecks = find_bottlenecks(_diamond_graph(), threshold=1)
    # A and D each appear in 2 paths, B and C in 1
    assert "A" in bottlenecks
    assert "D" in bottlenecks
    assert "B" not in bottlenecks


def test_find_bottlenecks_empty_graph():
    g = Graph()
    assert find_bottlenecks(g) == []


def test_compute_path_stats_returns_pathstats():
    stats = compute_path_stats(_chain_graph())
    assert stats.longest_path_length == 4
    assert len(stats.path_counts) == 4
    assert isinstance(stats.bottlenecks, list)


def test_compute_path_stats_single_node():
    stats = compute_path_stats(_single_node_graph())
    assert stats.longest_path == ["solo"]
    assert stats.longest_path_length == 1
