"""Tests for depgraph.stats."""

from __future__ import annotations

import pytest

from depgraph.graph import Graph, Node
from depgraph.stats import GraphStats, compute_stats, _in_degrees, _out_degrees


def _build_graph() -> Graph:
    """Build a small diamond-shaped graph: A -> B, A -> C, B -> D, C -> D."""
    g = Graph()
    a, b, c, d = Node("A"), Node("B"), Node("C"), Node("D")
    for n in (a, b, c, d):
        g.add_node(n)
    g.add_edge(a, b)
    g.add_edge(a, c)
    g.add_edge(b, d)
    g.add_edge(c, d)
    return g


def test_compute_stats_node_count():
    g = _build_graph()
    stats = compute_stats(g)
    assert stats.node_count == 4


def test_compute_stats_edge_count():
    g = _build_graph()
    stats = compute_stats(g)
    assert stats.edge_count == 4


def test_compute_stats_root_nodes():
    g = _build_graph()
    stats = compute_stats(g)
    assert stats.root_nodes == ["A"]


def test_compute_stats_leaf_nodes():
    g = _build_graph()
    stats = compute_stats(g)
    assert stats.leaf_nodes == ["D"]


def test_compute_stats_max_depth():
    g = _build_graph()
    stats = compute_stats(g)
    # A -> B -> D  or  A -> C -> D  — depth 2
    assert stats.max_depth == 2


def test_compute_stats_most_depended_on():
    g = _build_graph()
    stats = compute_stats(g)
    # D has in-degree 2, B and C have in-degree 1
    names = [name for name, _ in stats.most_depended_on]
    assert names[0] == "d"  # stored lower-case from dict key


def test_in_degrees():
    g = _build_graph()
    in_deg = _in_degrees(g)
    assert in_deg["a"] == 0
    assert in_deg["d"] == 2


def test_out_degrees():
    g = _build_graph()
    out_deg = _out_degrees(g)
    assert out_deg["a"] == 2
    assert out_deg["d"] == 0


def test_empty_graph():
    g = Graph()
    stats = compute_stats(g)
    assert stats.node_count == 0
    assert stats.edge_count == 0
    assert stats.max_depth == 0
    assert stats.root_nodes == []
    assert stats.leaf_nodes == []


def test_single_node_graph():
    g = Graph()
    g.add_node(Node("solo"))
    stats = compute_stats(g)
    assert stats.node_count == 1
    assert stats.edge_count == 0
    assert stats.root_nodes == ["solo"]
    assert stats.leaf_nodes == ["solo"]
    assert stats.max_depth == 0


def test_top_n_limits_most_depended_on():
    g = _build_graph()
    stats = compute_stats(g, top_n=1)
    assert len(stats.most_depended_on) == 1
