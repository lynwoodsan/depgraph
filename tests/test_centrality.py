"""Tests for depgraph.centrality."""
from __future__ import annotations

import pytest

from depgraph.graph import Graph
from depgraph.centrality import compute_centrality, CentralityScores


def _chain_graph() -> Graph:
    """A -> B -> C -> D"""
    g = Graph()
    for name in ("A", "B", "C", "D"):
        g.add_node(name)
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("C", "D")
    return g


def _diamond_graph() -> Graph:
    """A -> B, A -> C, B -> D, C -> D"""
    g = Graph()
    for name in ("A", "B", "C", "D"):
        g.add_node(name)
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")
    g.add_edge("C", "D")
    return g


def test_empty_graph_returns_empty_scores():
    g = Graph()
    scores = compute_centrality(g)
    assert scores.degree == {}
    assert scores.betweenness == {}
    assert scores.closeness == {}


def test_returns_centrality_scores_instance():
    g = _chain_graph()
    scores = compute_centrality(g)
    assert isinstance(scores, CentralityScores)


def test_all_nodes_present_in_degree():
    g = _chain_graph()
    scores = compute_centrality(g)
    node_names = {n.name for n in g.nodes}
    assert set(scores.degree.keys()) == node_names


def test_all_nodes_present_in_betweenness():
    g = _chain_graph()
    scores = compute_centrality(g)
    node_names = {n.name for n in g.nodes}
    assert set(scores.betweenness.keys()) == node_names


def test_all_nodes_present_in_closeness():
    g = _chain_graph()
    scores = compute_centrality(g)
    node_names = {n.name for n in g.nodes}
    assert set(scores.closeness.keys()) == node_names


def test_degree_values_between_zero_and_one():
    g = _chain_graph()
    scores = compute_centrality(g)
    for v in scores.degree.values():
        assert 0.0 <= v <= 1.0


def test_betweenness_values_between_zero_and_one():
    g = _chain_graph()
    scores = compute_centrality(g)
    for v in scores.betweenness.values():
        assert 0.0 <= v <= 1.0


def test_closeness_values_non_negative():
    g = _chain_graph()
    scores = compute_centrality(g)
    for v in scores.closeness.values():
        assert v >= 0.0


def test_chain_middle_nodes_have_higher_betweenness():
    g = _chain_graph()
    scores = compute_centrality(g)
    # B and C sit between endpoints; A and D do not
    assert scores.betweenness["B"] > scores.betweenness["A"]
    assert scores.betweenness["C"] > scores.betweenness["D"]


def test_diamond_root_has_high_degree():
    g = _diamond_graph()
    scores = compute_centrality(g)
    # A has 2 outgoing edges; D has 2 incoming edges
    assert scores.degree["A"] > scores.degree["B"]
    assert scores.degree["D"] > scores.degree["B"]


def test_top_degree_returns_correct_count():
    g = _chain_graph()
    scores = compute_centrality(g)
    top = scores.top_degree(n=2)
    assert len(top) == 2


def test_top_betweenness_returns_correct_count():
    g = _chain_graph()
    scores = compute_centrality(g)
    top = scores.top_betweenness(n=3)
    assert len(top) == 3


def test_top_closeness_returns_correct_count():
    g = _diamond_graph()
    scores = compute_centrality(g)
    top = scores.top_closeness(n=2)
    assert len(top) == 2


def test_single_node_graph():
    g = Graph()
    g.add_node("X")
    scores = compute_centrality(g)
    assert scores.degree["X"] == 0.0
    assert scores.betweenness["X"] == 0.0
    assert scores.closeness["X"] == 0.0
