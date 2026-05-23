"""Tests for depgraph.highlight."""

from __future__ import annotations

import pytest

from depgraph.graph import DependencyGraph
from depgraph.highlight import highlight_dependencies, node_classes


def _build_graph() -> DependencyGraph:
    """Build a small graph: A -> B -> C, A -> D."""
    g = DependencyGraph()
    for name in ("A", "B", "C", "D"):
        g.add_node(name)
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("A", "D")
    return g


def test_highlight_root_includes_all_forward_deps():
    g = _build_graph()
    nodes, edges = highlight_dependencies(g, "A")
    assert "a" in nodes
    assert "b" in nodes
    assert "c" in nodes
    assert "d" in nodes


def test_highlight_leaf_only_includes_itself():
    g = _build_graph()
    nodes, edges = highlight_dependencies(g, "C")
    assert nodes == {"c"}
    assert edges == set()


def test_highlight_mid_node_forward():
    g = _build_graph()
    nodes, edges = highlight_dependencies(g, "B")
    assert "b" in nodes
    assert "c" in nodes
    assert "a" not in nodes
    assert "d" not in nodes


def test_highlight_edges_are_subset_of_graph_edges():
    g = _build_graph()
    nodes, edges = highlight_dependencies(g, "A")
    all_edges = {(s.lower(), d.lower()) for s, d in g.edges}
    assert edges.issubset(all_edges)


def test_highlight_with_reverse_includes_parents():
    g = _build_graph()
    nodes, edges = highlight_dependencies(g, "B", include_reverse=True)
    # Forward: B, C; Reverse: A (which also pulls D via forward from A)
    assert "a" in nodes
    assert "b" in nodes
    assert "c" in nodes


def test_highlight_case_insensitive():
    g = _build_graph()
    nodes1, _ = highlight_dependencies(g, "a")
    nodes2, _ = highlight_dependencies(g, "A")
    assert nodes1 == nodes2


def test_highlight_unknown_root_returns_empty():
    g = _build_graph()
    nodes, edges = highlight_dependencies(g, "Z")
    # Z is not in the graph so BFS starts from an unknown key
    assert "a" not in nodes
    assert "b" not in nodes


def test_node_classes_highlighted_vs_dimmed():
    g = _build_graph()
    nodes, _ = highlight_dependencies(g, "B")
    classes = node_classes(g, nodes)
    assert classes["b"] == "node highlighted"
    assert classes["c"] == "node highlighted"
    assert classes["a"] == "node dimmed"
    assert classes["d"] == "node dimmed"


def test_node_classes_all_highlighted():
    g = _build_graph()
    nodes, _ = highlight_dependencies(g, "A")
    classes = node_classes(g, nodes)
    assert all(v == "node highlighted" for v in classes.values())


def test_node_classes_covers_all_nodes():
    g = _build_graph()
    nodes, _ = highlight_dependencies(g, "B")
    classes = node_classes(g, nodes)
    graph_names = {n.name.lower() for n in g.nodes}
    assert set(classes.keys()) == graph_names
