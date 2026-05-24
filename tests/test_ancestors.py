"""Tests for depgraph.ancestors module."""

import pytest
from depgraph.graph import Graph, Node
from depgraph.ancestors import get_ancestors, get_descendants, get_neighbourhood


def _build_graph() -> Graph:
    """Build a simple diamond-shaped dependency graph.

    A -> B -> D
    A -> C -> D
    """
    g = Graph()
    a, b, c, d = Node("A"), Node("B"), Node("C"), Node("D")
    for n in (a, b, c, d):
        g.add_node(n)
    g.add_edge(a, b)
    g.add_edge(a, c)
    g.add_edge(b, d)
    g.add_edge(c, d)
    return g


def test_get_ancestors_of_leaf():
    g = _build_graph()
    result = get_ancestors(g, "D")
    assert result == {"a", "b", "c"}


def test_get_ancestors_of_mid_node():
    g = _build_graph()
    result = get_ancestors(g, "B")
    assert result == {"a"}


def test_get_ancestors_of_root_is_empty():
    g = _build_graph()
    result = get_ancestors(g, "A")
    assert result == set()


def test_get_ancestors_missing_node_returns_empty():
    g = _build_graph()
    assert get_ancestors(g, "Z") == set()


def test_get_ancestors_case_insensitive():
    g = _build_graph()
    assert get_ancestors(g, "d") == get_ancestors(g, "D")


def test_get_descendants_of_root():
    g = _build_graph()
    result = get_descendants(g, "A")
    assert result == {"b", "c", "d"}


def test_get_descendants_of_mid_node():
    g = _build_graph()
    result = get_descendants(g, "B")
    assert result == {"d"}


def test_get_descendants_of_leaf_is_empty():
    g = _build_graph()
    result = get_descendants(g, "D")
    assert result == set()


def test_get_descendants_missing_node_returns_empty():
    g = _build_graph()
    assert get_descendants(g, "Z") == set()


def test_get_descendants_case_insensitive():
    g = _build_graph()
    assert get_descendants(g, "a") == get_descendants(g, "A")


def test_get_neighbourhood_includes_self():
    g = _build_graph()
    result = get_neighbourhood(g, "B")
    assert "b" in result


def test_get_neighbourhood_full_for_mid_node():
    g = _build_graph()
    result = get_neighbourhood(g, "B")
    # ancestors of B: {a}, descendants of B: {d}, self: b
    assert result == {"a", "b", "d"}


def test_get_neighbourhood_missing_node_returns_empty():
    g = _build_graph()
    assert get_neighbourhood(g, "Z") == set()


def test_get_neighbourhood_root_has_no_ancestors():
    g = _build_graph()
    result = get_neighbourhood(g, "A")
    assert result == {"a", "b", "c", "d"}
