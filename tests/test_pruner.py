"""Tests for depgraph.pruner."""

from __future__ import annotations

import pytest

from depgraph.graph import Graph, Node
from depgraph.pruner import prune_orphans, prune_transitive_edges, prune_by_depth


def _build_graph(*edges: tuple[str, str]) -> Graph:
    g = Graph()
    for src_name, dst_name in edges:
        src, dst = Node(src_name), Node(dst_name)
        g.add_node(src)
        g.add_node(dst)
        g.add_edge(src, dst)
    return g


def _add_orphan(graph: Graph, name: str) -> Node:
    node = Node(name)
    graph.add_node(node)
    return node


# ---------------------------------------------------------------------------
# prune_orphans
# ---------------------------------------------------------------------------

def test_prune_orphans_removes_isolated_node():
    g = _build_graph(("A", "B"))
    _add_orphan(g, "Orphan")
    result = prune_orphans(g)
    names = {n.name for n in result.nodes}
    assert "Orphan" not in names
    assert "A" in names and "B" in names


def test_prune_orphans_keeps_connected_nodes():
    g = _build_graph(("A", "B"), ("B", "C"))
    result = prune_orphans(g)
    assert len(result.nodes) == 3


def test_prune_orphans_empty_graph():
    g = Graph()
    result = prune_orphans(g)
    assert len(result.nodes) == 0


def test_prune_orphans_all_orphans():
    g = Graph()
    _add_orphan(g, "X")
    _add_orphan(g, "Y")
    result = prune_orphans(g)
    assert len(result.nodes) == 0


# ---------------------------------------------------------------------------
# prune_transitive_edges
# ---------------------------------------------------------------------------

def test_prune_transitive_removes_redundant_edge():
    # A -> B -> C and also A -> C (redundant)
    g = _build_graph(("A", "B"), ("B", "C"), ("A", "C"))
    result = prune_transitive_edges(g)
    edge_pairs = {(s.name, d.name) for s, d in result.edges}
    assert ("A", "C") not in edge_pairs
    assert ("A", "B") in edge_pairs
    assert ("B", "C") in edge_pairs


def test_prune_transitive_keeps_non_redundant_edges():
    g = _build_graph(("A", "B"), ("B", "C"))
    result = prune_transitive_edges(g)
    assert len(list(result.edges)) == 2


def test_prune_transitive_preserves_nodes():
    g = _build_graph(("A", "B"), ("B", "C"), ("A", "C"))
    result = prune_transitive_edges(g)
    assert {n.name for n in result.nodes} == {"A", "B", "C"}


# ---------------------------------------------------------------------------
# prune_by_depth
# ---------------------------------------------------------------------------

def test_prune_by_depth_zero_returns_root_only():
    g = _build_graph(("A", "B"), ("B", "C"))
    root = Node("A")
    result = prune_by_depth(g, root, max_depth=0)
    assert {n.name for n in result.nodes} == {"A"}
    assert len(list(result.edges)) == 0


def test_prune_by_depth_one():
    g = _build_graph(("A", "B"), ("B", "C"))
    root = Node("A")
    result = prune_by_depth(g, root, max_depth=1)
    assert {n.name for n in result.nodes} == {"A", "B"}


def test_prune_by_depth_full_chain():
    g = _build_graph(("A", "B"), ("B", "C"), ("C", "D"))
    root = Node("A")
    result = prune_by_depth(g, root, max_depth=10)
    assert {n.name for n in result.nodes} == {"A", "B", "C", "D"}


def test_prune_by_depth_negative_raises():
    g = _build_graph(("A", "B"))
    with pytest.raises(ValueError):
        prune_by_depth(g, Node("A"), max_depth=-1)
