"""Tests for depgraph.exporter (JSON and DOT export)."""

import json

import pytest

from depgraph.graph import DependencyGraph, Node
from depgraph.exporter import export_json, export_dot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_graph() -> DependencyGraph:
    g = DependencyGraph()
    a = Node("packageA")
    b = Node("packageB")
    c = Node("packageC")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_edge(a, b)
    g.add_edge(a, c)
    return g


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def test_export_json_structure():
    g = _build_graph()
    result = json.loads(export_json(g))
    assert "nodes" in result
    assert "edges" in result


def test_export_json_nodes():
    g = _build_graph()
    result = json.loads(export_json(g))
    assert sorted(result["nodes"]) == ["packageA", "packageB", "packageC"]


def test_export_json_edges():
    g = _build_graph()
    result = json.loads(export_json(g))
    assert ["packageA", "packageB"] in result["edges"]
    assert ["packageA", "packageC"] in result["edges"]
    assert len(result["edges"]) == 2


def test_export_json_empty_graph():
    g = DependencyGraph()
    result = json.loads(export_json(g))
    assert result == {"nodes": [], "edges": []}


def test_export_json_is_valid_json():
    g = _build_graph()
    raw = export_json(g)
    parsed = json.loads(raw)  # must not raise
    assert isinstance(parsed, dict)


# ---------------------------------------------------------------------------
# DOT export
# ---------------------------------------------------------------------------

def test_export_dot_contains_digraph():
    g = _build_graph()
    dot = export_dot(g)
    assert dot.startswith('digraph')


def test_export_dot_contains_nodes():
    g = _build_graph()
    dot = export_dot(g)
    assert '"packageA"' in dot
    assert '"packageB"' in dot
    assert '"packageC"' in dot


def test_export_dot_contains_edges():
    g = _build_graph()
    dot = export_dot(g)
    assert '"packageA" -> "packageB"' in dot
    assert '"packageA" -> "packageC"' in dot


def test_export_dot_custom_graph_name():
    g = _build_graph()
    dot = export_dot(g, graph_name="mygraph")
    assert 'digraph "mygraph"' in dot


def test_export_dot_empty_graph():
    g = DependencyGraph()
    dot = export_dot(g)
    assert 'digraph' in dot
    assert '->' not in dot


def test_export_dot_ends_with_brace():
    g = _build_graph()
    dot = export_dot(g)
    assert dot.strip().endswith("}")
