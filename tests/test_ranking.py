"""Tests for depgraph.ranking."""

import pytest

from depgraph.graph import Graph
from depgraph.ranking import (
    RankedNode,
    rank_by_in_degree,
    rank_by_out_degree,
    rank_by_combined,
    top_n,
)


def _build_graph() -> Graph:
    """Build a simple graph: A -> B -> D, A -> C -> D, B -> C."""
    g = Graph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    g.add_edge("B", "D")
    g.add_edge("C", "D")
    g.add_edge("B", "C")
    return g


def test_rank_by_in_degree_returns_all_nodes():
    g = _build_graph()
    result = rank_by_in_degree(g)
    assert len(result) == 4


def test_rank_by_in_degree_d_is_first():
    g = _build_graph()
    result = rank_by_in_degree(g)
    # D is pointed to by B and C => in-degree 2
    assert result[0].name == "D"
    assert result[0].score == 2.0


def test_rank_by_in_degree_a_is_last():
    g = _build_graph()
    result = rank_by_in_degree(g)
    # A has no incoming edges
    last = result[-1]
    assert last.name == "A"
    assert last.score == 0.0


def test_rank_by_in_degree_ranks_are_sequential():
    g = _build_graph()
    result = rank_by_in_degree(g)
    ranks = [r.rank for r in result]
    assert ranks == list(range(1, len(result) + 1))


def test_rank_by_out_degree_a_is_first():
    g = _build_graph()
    result = rank_by_out_degree(g)
    # A points to B and C => out-degree 2
    assert result[0].name == "A"
    assert result[0].score == 2.0


def test_rank_by_out_degree_d_is_last():
    g = _build_graph()
    result = rank_by_out_degree(g)
    last = result[-1]
    assert last.name == "D"
    assert last.score == 0.0


def test_rank_by_combined_returns_all_nodes():
    g = _build_graph()
    result = rank_by_combined(g)
    assert len(result) == 4


def test_rank_by_combined_scores_non_negative():
    g = _build_graph()
    result = rank_by_combined(g)
    for r in result:
        assert r.score >= 0.0


def test_rank_by_combined_custom_weights():
    g = _build_graph()
    result = rank_by_combined(g, in_weight=1.0, out_weight=0.0)
    # With only in-degree weight, D should still be first
    assert result[0].name == "D"


def test_top_n_returns_correct_count():
    g = _build_graph()
    ranked = rank_by_in_degree(g)
    top = top_n(ranked, 2)
    assert len(top) == 2


def test_top_n_preserves_order():
    g = _build_graph()
    ranked = rank_by_in_degree(g)
    top = top_n(ranked, 3)
    scores = [r.score for r in top]
    assert scores == sorted(scores, reverse=True)


def test_top_n_larger_than_list():
    g = _build_graph()
    ranked = rank_by_in_degree(g)
    top = top_n(ranked, 100)
    assert len(top) == len(ranked)
