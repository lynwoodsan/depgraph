"""Tests for depgraph.metrics."""

import pytest

from depgraph.graph import Graph, Node
from depgraph.metrics import (
    NodeMetrics,
    compute_node_metrics,
    most_depended_upon,
)


def _build_graph() -> Graph:
    """Build a simple diamond graph: A -> B, A -> C, B -> D, C -> D."""
    g = Graph()
    a, b, c, d = Node("A"), Node("B"), Node("C"), Node("D")
    for n in (a, b, c, d):
        g.add_node(n)
    g.add_edge(a, b)
    g.add_edge(a, c)
    g.add_edge(b, d)
    g.add_edge(c, d)
    return g


def test_compute_metrics_returns_all_nodes():
    g = _build_graph()
    metrics = compute_node_metrics(g)
    assert set(metrics.keys()) == {"A", "B", "C", "D"}


def test_root_node_detected():
    metrics = compute_node_metrics(_build_graph())
    assert metrics["A"].is_root is True
    assert metrics["B"].is_root is False


def test_leaf_node_detected():
    metrics = compute_node_metrics(_build_graph())
    assert metrics["D"].is_leaf is True
    assert metrics["A"].is_leaf is False


def test_in_degree():
    metrics = compute_node_metrics(_build_graph())
    assert metrics["D"].in_degree == 2
    assert metrics["A"].in_degree == 0


def test_out_degree():
    metrics = compute_node_metrics(_build_graph())
    assert metrics["A"].out_degree == 2
    assert metrics["D"].out_degree == 0


def test_transitive_deps_root():
    metrics = compute_node_metrics(_build_graph())
    # A can reach B, C, D
    assert metrics["A"].transitive_deps == 3


def test_transitive_deps_leaf():
    metrics = compute_node_metrics(_build_graph())
    assert metrics["D"].transitive_deps == 0


def test_transitive_dependents_leaf():
    metrics = compute_node_metrics(_build_graph())
    # D is depended upon by A, B, C
    assert metrics["D"].transitive_dependents == 3


def test_centrality_is_float():
    metrics = compute_node_metrics(_build_graph())
    for m in metrics.values():
        assert isinstance(m.centrality, float)


def test_most_depended_upon_order():
    metrics = compute_node_metrics(_build_graph())
    top = most_depended_upon(metrics, top=2)
    assert top[0].name == "D"
    assert len(top) == 2


def test_single_node_graph():
    g = Graph()
    g.add_node(Node("solo"))
    metrics = compute_node_metrics(g)
    m = metrics["solo"]
    assert m.is_root is True
    assert m.is_leaf is True
    assert m.centrality == 0.0


def test_most_depended_upon_respects_top():
    metrics = compute_node_metrics(_build_graph())
    assert len(most_depended_upon(metrics, top=1)) == 1
    assert len(most_depended_upon(metrics, top=10)) == 4
