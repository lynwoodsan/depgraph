"""Tests for depgraph.diff."""

import pytest

from depgraph.graph import DependencyGraph, Node
from depgraph.diff import GraphDiff, diff_graphs


def _make_graph(*edges):
    """Build a DependencyGraph from (src_name, dst_name) tuples."""
    g = DependencyGraph()
    for src_name, dst_name in edges:
        src = Node(src_name)
        dst = Node(dst_name)
        g.add_node(src)
        g.add_node(dst)
        g.add_edge(src, dst)
    return g


def test_diff_identical_graphs_no_changes():
    g1 = _make_graph(("A", "B"), ("B", "C"))
    g2 = _make_graph(("A", "B"), ("B", "C"))
    result = diff_graphs(g1, g2)
    assert not result.has_changes


def test_diff_added_node():
    g1 = _make_graph(("A", "B"))
    g2 = _make_graph(("A", "B"), ("A", "C"))
    result = diff_graphs(g1, g2)
    assert Node("C") in result.added_nodes
    assert not result.removed_nodes


def test_diff_removed_node():
    g1 = _make_graph(("A", "B"), ("A", "C"))
    g2 = _make_graph(("A", "B"))
    result = diff_graphs(g1, g2)
    assert Node("C") in result.removed_nodes
    assert not result.added_nodes


def test_diff_added_edge():
    g1 = _make_graph(("A", "B"))
    g2 = _make_graph(("A", "B"), ("B", "C"))
    result = diff_graphs(g1, g2)
    assert (Node("B"), Node("C")) in result.added_edges
    assert not result.removed_edges


def test_diff_removed_edge():
    g1 = _make_graph(("A", "B"), ("B", "C"))
    g2 = _make_graph(("A", "B"))
    result = diff_graphs(g1, g2)
    assert (Node("B"), Node("C")) in result.removed_edges
    assert not result.added_edges


def test_diff_empty_graphs():
    g1 = DependencyGraph()
    g2 = DependencyGraph()
    result = diff_graphs(g1, g2)
    assert not result.has_changes


def test_diff_from_empty():
    g1 = DependencyGraph()
    g2 = _make_graph(("A", "B"))
    result = diff_graphs(g1, g2)
    assert Node("A") in result.added_nodes
    assert Node("B") in result.added_nodes
    assert (Node("A"), Node("B")) in result.added_edges


def test_diff_to_empty():
    g1 = _make_graph(("A", "B"))
    g2 = DependencyGraph()
    result = diff_graphs(g1, g2)
    assert Node("A") in result.removed_nodes
    assert Node("B") in result.removed_nodes


def test_summary_no_changes():
    g = _make_graph(("A", "B"))
    result = diff_graphs(g, g)
    assert result.summary() == "(no changes)"


def test_summary_contains_added_and_removed():
    g1 = _make_graph(("A", "B"))
    g2 = _make_graph(("A", "C"))
    result = diff_graphs(g1, g2)
    summary = result.summary()
    assert "+ node" in summary or "- node" in summary or "edge" in summary
    assert result.has_changes
