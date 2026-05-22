"""Tests for depgraph.graph."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from depgraph.graph import DependencyGraph, Node, build_graph
from depgraph.resolver import Package


# ---------------------------------------------------------------------------
# Node tests
# ---------------------------------------------------------------------------

def test_node_hash_case_insensitive():
    assert hash(Node("Requests", "2.31.0")) == hash(Node("requests", "2.31.0"))


def test_node_equality_case_insensitive():
    assert Node("Flask", "3.0.0") == Node("flask", "3.0.0")


def test_node_inequality():
    assert Node("Flask", "3.0.0") != Node("Django", "4.2.0")


# ---------------------------------------------------------------------------
# DependencyGraph tests
# ---------------------------------------------------------------------------

def test_add_node():
    g = DependencyGraph()
    node = Node("requests", "2.31.0")
    g.add_node(node)
    assert "requests" in g.nodes
    assert g.edges["requests"] == []


def test_add_node_deduplicates():
    g = DependencyGraph()
    g.add_node(Node("requests", "2.31.0"))
    g.add_node(Node("Requests", "2.32.0"))  # duplicate, different case
    assert len(g.nodes) == 1


def test_add_edge():
    g = DependencyGraph()
    g.add_node(Node("flask", "3.0.0"))
    g.add_node(Node("werkzeug", "3.0.1"))
    g.add_edge("flask", "werkzeug")
    assert "werkzeug" in g.edges["flask"]


def test_add_edge_no_duplicate():
    g = DependencyGraph()
    g.add_node(Node("flask", "3.0.0"))
    g.add_edge("flask", "werkzeug")
    g.add_edge("flask", "werkzeug")
    assert g.edges["flask"].count("werkzeug") == 1


def test_get_dependencies():
    g = DependencyGraph()
    g.add_node(Node("flask", "3.0.0"))
    g.add_node(Node("werkzeug", "3.0.1"))
    g.add_edge("flask", "werkzeug")
    deps = g.get_dependencies("flask")
    assert len(deps) == 1
    assert deps[0].name == "werkzeug"


# ---------------------------------------------------------------------------
# build_graph tests
# ---------------------------------------------------------------------------

def _make_pkg(name: str, version: str, deps=None) -> Package:
    pkg = Package(name, version)
    pkg.dependencies = deps or []
    return pkg


def test_build_graph_single_package():
    root = _make_pkg("mylib", "1.0.0")
    with patch("depgraph.graph.resolve_package", return_value=root):
        graph = build_graph("mylib")
    assert "mylib" in graph.nodes


def test_build_graph_with_deps():
    werkzeug = _make_pkg("werkzeug", "3.0.1")
    flask = _make_pkg("flask", "3.0.0", deps=[werkzeug])

    def fake_resolve(name):
        return {"flask": flask, "werkzeug": werkzeug}.get(name.lower())

    with patch("depgraph.graph.resolve_package", side_effect=fake_resolve):
        graph = build_graph("flask")

    assert "flask" in graph.nodes
    assert "werkzeug" in graph.nodes
    assert "werkzeug" in graph.edges["flask"]


def test_build_graph_max_depth():
    c = _make_pkg("c", "1.0")
    b = _make_pkg("b", "1.0", deps=[c])
    a = _make_pkg("a", "1.0", deps=[b])

    def fake_resolve(name):
        return {"a": a, "b": b, "c": c}.get(name.lower())

    with patch("depgraph.graph.resolve_package", side_effect=fake_resolve):
        graph = build_graph("a", max_depth=1)

    assert "a" in graph.nodes
    assert "b" in graph.nodes
    assert "c" not in graph.nodes


def test_build_graph_unresolvable():
    with patch("depgraph.graph.resolve_package", return_value=None):
        graph = build_graph("nonexistent")
    assert graph.all_nodes() == []
