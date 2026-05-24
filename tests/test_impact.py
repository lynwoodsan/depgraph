"""Tests for depgraph.impact — impact analysis module."""

from __future__ import annotations

import pytest

from depgraph.graph import Graph, Node
from depgraph.impact import ImpactResult, analyse_impact, most_impactful


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_graph() -> Graph:
    """Build a simple diamond-shaped dependency graph.

    A -> B -> D
    A -> C -> D
    """
    g = Graph()
    for name in ("A", "B", "C", "D"):
        g.add_node(Node(name))
    g.add_edge(Node("A"), Node("B"))
    g.add_edge(Node("A"), Node("C"))
    g.add_edge(Node("B"), Node("D"))
    g.add_edge(Node("C"), Node("D"))
    return g


# ---------------------------------------------------------------------------
# analyse_impact
# ---------------------------------------------------------------------------

def test_impact_missing_node_returns_empty():
    g = _build_graph()
    result = analyse_impact(g, "nonexistent")
    assert result.count == 0
    assert result.affected_nodes == frozenset()
    assert result.affected_edges == frozenset()


def test_impact_leaf_node_affects_only_itself():
    g = _build_graph()
    result = analyse_impact(g, "A")
    # A has no dependents (nothing points to A), so only A itself
    assert Node("A") in result.affected_nodes
    assert result.count == 1


def test_impact_root_node_affects_all():
    """D is depended upon by B and C which are depended upon by A."""
    g = _build_graph()
    result = analyse_impact(g, "D")
    expected = {Node("A"), Node("B"), Node("C"), Node("D")}
    assert result.affected_nodes == frozenset(expected)


def test_impact_mid_node():
    g = _build_graph()
    result = analyse_impact(g, "B")
    # A depends on B, so A and B are affected
    assert Node("A") in result.affected_nodes
    assert Node("B") in result.affected_nodes
    assert Node("C") not in result.affected_nodes
    assert Node("D") not in result.affected_nodes


def test_impact_case_insensitive_lookup():
    g = _build_graph()
    result_lower = analyse_impact(g, "d")
    result_upper = analyse_impact(g, "D")
    assert result_lower.affected_nodes == result_upper.affected_nodes


def test_impact_affected_edges_subset_of_graph_edges():
    g = _build_graph()
    result = analyse_impact(g, "D")
    graph_edge_set = set(g.edges)
    for edge in result.affected_edges:
        assert edge in graph_edge_set


def test_impact_depth_map_root_is_zero():
    g = _build_graph()
    result = analyse_impact(g, "D")
    assert result.depth_map[Node("D")] == 0


def test_impact_depth_map_direct_dependents_are_one():
    g = _build_graph()
    result = analyse_impact(g, "D")
    assert result.depth_map[Node("B")] == 1
    assert result.depth_map[Node("C")] == 1


# ---------------------------------------------------------------------------
# most_impactful
# ---------------------------------------------------------------------------

def test_most_impactful_returns_correct_count():
    g = _build_graph()
    ranking = most_impactful(g, top_n=2)
    assert len(ranking) == 2


def test_most_impactful_d_is_first():
    """D is depended on by B, C, and A — highest impact."""
    g = _build_graph()
    ranking = most_impactful(g, top_n=4)
    top_node, top_score = ranking[0]
    assert top_node == Node("D")
    assert top_score == 3  # A, B, C all affected (excluding D itself)


def test_most_impactful_a_is_last():
    g = _build_graph()
    ranking = most_impactful(g, top_n=4)
    last_node, last_score = ranking[-1]
    assert last_node == Node("A")
    assert last_score == 0
