"""Tests for depgraph.clustering."""

from __future__ import annotations

import pytest

from depgraph.graph import Graph
from depgraph.clustering import (
    Cluster,
    cluster_by_connectivity,
    cluster_by_prefix,
    largest_cluster,
)


def _build_two_component_graph() -> Graph:
    """A -> B -> C  and  D -> E (two separate components)."""
    g = Graph()
    for name in ("A", "B", "C", "D", "E"):
        g.add_node(name)
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("D", "E")
    return g


def _build_prefix_graph() -> Graph:
    """Nodes: django.orm, django.views, flask.app, flask.cli, requests."""
    g = Graph()
    for name in ("django.orm", "django.views", "flask.app", "flask.cli", "requests"):
        g.add_node(name)
    return g


# ── cluster_by_connectivity ──────────────────────────────────────────────────

def test_connectivity_two_components_found():
    g = _build_two_component_graph()
    clusters = cluster_by_connectivity(g)
    assert len(clusters) == 2


def test_connectivity_all_nodes_covered():
    g = _build_two_component_graph()
    clusters = cluster_by_connectivity(g)
    covered = set()
    for c in clusters:
        covered |= set(c.nodes)
    assert covered == {"A", "B", "C", "D", "E"}


def test_connectivity_single_component():
    g = Graph()
    for name in ("X", "Y", "Z"):
        g.add_node(name)
    g.add_edge("X", "Y")
    g.add_edge("Y", "Z")
    clusters = cluster_by_connectivity(g)
    assert len(clusters) == 1
    assert frozenset({"X", "Y", "Z"}) == clusters[0].nodes


def test_connectivity_empty_graph():
    g = Graph()
    clusters = cluster_by_connectivity(g)
    assert clusters == []


def test_connectivity_isolated_nodes_each_own_cluster():
    g = Graph()
    for name in ("A", "B", "C"):
        g.add_node(name)
    clusters = cluster_by_connectivity(g)
    assert len(clusters) == 3


# ── cluster_by_prefix ────────────────────────────────────────────────────────

def test_prefix_groups_django_together():
    g = _build_prefix_graph()
    result = cluster_by_prefix(g)
    assert "django" in result
    assert result["django"].nodes == frozenset({"django.orm", "django.views"})


def test_prefix_groups_flask_together():
    g = _build_prefix_graph()
    result = cluster_by_prefix(g)
    assert result["flask"].nodes == frozenset({"flask.app", "flask.cli"})


def test_prefix_no_separator_whole_name_is_key():
    g = Graph()
    g.add_node("requests")
    result = cluster_by_prefix(g)
    assert "requests" in result
    assert "requests" in result["requests"].nodes


def test_prefix_custom_separator():
    g = Graph()
    for name in ("a-b", "a-c", "d-e"):
        g.add_node(name)
    result = cluster_by_prefix(g, sep="-")
    assert len(result) == 2
    assert result["a"].nodes == frozenset({"a-b", "a-c"})


# ── largest_cluster ──────────────────────────────────────────────────────────

def test_largest_cluster_returns_biggest():
    clusters = [
        Cluster("small", frozenset({"x"})),
        Cluster("big", frozenset({"a", "b", "c"})),
        Cluster("mid", frozenset({"p", "q"})),
    ]
    assert largest_cluster(clusters).name == "big"


def test_largest_cluster_empty_list_returns_none():
    assert largest_cluster([]) is None


def test_cluster_contains_case_insensitive():
    c = Cluster("test", frozenset({"Django"}))
    assert "django" in c
    assert "DJANGO" in c
