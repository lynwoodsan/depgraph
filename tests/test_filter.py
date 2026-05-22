"""Tests for depgraph.filter."""

from __future__ import annotations

import pytest

from depgraph.graph import DependencyGraph, Node
from depgraph.filter import filter_by_depth, filter_by_packages


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_chain_graph() -> DependencyGraph:
    """A -> B -> C -> D (linear chain)."""
    g = DependencyGraph()
    for name in ("A", "B", "C", "D"):
        g.add_node(name)
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("C", "D")
    return g


def _build_wide_graph() -> DependencyGraph:
    """Root depends on X and Y; X depends on Z."""
    g = DependencyGraph()
    for name in ("Root", "X", "Y", "Z"):
        g.add_node(name)
    g.add_edge("Root", "X")
    g.add_edge("Root", "Y")
    g.add_edge("X", "Z")
    return g


# ---------------------------------------------------------------------------
# filter_by_depth
# ---------------------------------------------------------------------------

def test_filter_by_depth_zero():
    g = _build_chain_graph()
    result = filter_by_depth(g, "A", max_depth=0)
    assert {n.name for n in result.nodes} == {"A"}
    assert list(result.edges) == []


def test_filter_by_depth_one():
    g = _build_chain_graph()
    result = filter_by_depth(g, "A", max_depth=1)
    assert {n.name for n in result.nodes} == {"A", "B"}


def test_filter_by_depth_full():
    g = _build_chain_graph()
    result = filter_by_depth(g, "A", max_depth=10)
    assert {n.name for n in result.nodes} == {"A", "B", "C", "D"}


def test_filter_by_depth_wide_depth1():
    g = _build_wide_graph()
    result = filter_by_depth(g, "Root", max_depth=1)
    assert {n.name for n in result.nodes} == {"Root", "X", "Y"}
    assert Node("Z") not in result.nodes


def test_filter_by_depth_negative_raises():
    g = _build_chain_graph()
    with pytest.raises(ValueError):
        filter_by_depth(g, "A", max_depth=-1)


def test_filter_by_depth_unknown_root_raises():
    g = _build_chain_graph()
    with pytest.raises(KeyError):
        filter_by_depth(g, "NotHere", max_depth=1)


# ---------------------------------------------------------------------------
# filter_by_packages
# ---------------------------------------------------------------------------

def test_filter_by_packages_include():
    g = _build_wide_graph()
    result = filter_by_packages(g, include={"Root", "X", "Z"})
    assert {n.name for n in result.nodes} == {"Root", "X", "Z"}
    assert Node("Y") not in result.nodes


def test_filter_by_packages_exclude():
    g = _build_wide_graph()
    result = filter_by_packages(g, exclude={"Z"})
    assert Node("Z") not in result.nodes
    assert {n.name for n in result.nodes} == {"Root", "X", "Y"}


def test_filter_by_packages_include_case_insensitive():
    g = _build_wide_graph()
    result = filter_by_packages(g, include={"root", "x"})
    assert {n.name for n in result.nodes} == {"Root", "X"}


def test_filter_by_packages_edges_pruned():
    g = _build_wide_graph()
    result = filter_by_packages(g, exclude={"X"})
    # Edge Root->X should be gone; Root->Y should remain
    edge_pairs = {(src.name, dst.name) for src, dst in result.edges}
    assert ("Root", "X") not in edge_pairs
    assert ("Root", "Y") in edge_pairs


def test_filter_by_packages_empty_include_returns_empty():
    g = _build_wide_graph()
    result = filter_by_packages(g, include=set())
    assert len(result.nodes) == 0
