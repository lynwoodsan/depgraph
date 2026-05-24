"""Tests for depgraph.similarity."""

import pytest

from depgraph.graph import Graph
from depgraph.similarity import (
    SimilarityResult,
    compute_similarity,
    most_similar,
    _jaccard,
)


def _build_graph(*nodes, edges=()):
    g = Graph()
    for name in nodes:
        g.add_node(name)
    for src, dst in edges:
        g.add_edge(src, dst)
    return g


# --- _jaccard ---

def test_jaccard_identical_sets():
    assert _jaccard({1, 2, 3}, {1, 2, 3}) == 1.0


def test_jaccard_disjoint_sets():
    assert _jaccard({1, 2}, {3, 4}) == 0.0


def test_jaccard_partial_overlap():
    result = _jaccard({1, 2, 3}, {2, 3, 4})
    assert abs(result - 0.5) < 1e-9


def test_jaccard_both_empty():
    assert _jaccard(set(), set()) == 1.0


# --- compute_similarity ---

def test_identical_graphs_score_one():
    g = _build_graph("a", "b", "c", edges=[("a", "b"), ("b", "c")])
    result = compute_similarity(g, g)
    assert result.node_jaccard == 1.0
    assert result.edge_jaccard == 1.0
    assert result.overall == 1.0


def test_disjoint_graphs_score_zero():
    g1 = _build_graph("a", "b", edges=[("a", "b")])
    g2 = _build_graph("x", "y", edges=[("x", "y")])
    result = compute_similarity(g1, g2)
    assert result.node_jaccard == 0.0
    assert result.edge_jaccard == 0.0


def test_common_nodes_populated():
    g1 = _build_graph("a", "b", "c")
    g2 = _build_graph("b", "c", "d")
    result = compute_similarity(g1, g2)
    assert result.common_nodes == {"b", "c"}


def test_common_edges_populated():
    g1 = _build_graph("a", "b", "c", edges=[("a", "b"), ("b", "c")])
    g2 = _build_graph("a", "b", "c", edges=[("b", "c"), ("a", "c")])
    result = compute_similarity(g1, g2)
    assert result.common_edges == {("b", "c")}


def test_node_comparison_is_case_insensitive():
    g1 = _build_graph("Flask", "Requests")
    g2 = _build_graph("flask", "requests")
    result = compute_similarity(g1, g2)
    assert result.node_jaccard == 1.0


def test_empty_graphs_are_fully_similar():
    result = compute_similarity(Graph(), Graph())
    assert result.overall == 1.0


# --- most_similar ---

def test_most_similar_returns_closest():
    target = _build_graph("a", "b", "c", edges=[("a", "b"), ("b", "c")])
    close = _build_graph("a", "b", "c", edges=[("a", "b"), ("b", "c")])
    far = _build_graph("x", "y")
    assert most_similar(target, [far, close]) is close


def test_most_similar_empty_candidates_returns_none():
    g = _build_graph("a")
    assert most_similar(g, []) is None
