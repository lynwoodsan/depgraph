"""Tests for depgraph.subgraph module."""

import pytest
from depgraph.graph import Graph, Node
from depgraph.subgraph import extract_subgraph


def _chain_graph() -> Graph:
    """A -> B -> C -> D"""
    g = Graph()
    nodes = [Node(n) for n in "ABCD"]
    for n in nodes:
        g.add_node(n)
    for i in range(len(nodes) - 1):
        g.add_edge(nodes[i], nodes[i + 1])
    return g


def _diamond_graph() -> Graph:
    """A -> B -> D, A -> C -> D"""
    g = Graph()
    a, b, c, d = Node("A"), Node("B"), Node("C"), Node("D")
    for n in (a, b, c, d):
        g.add_node(n)
    g.add_edge(a, b)
    g.add_edge(a, c)
    g.add_edge(b, d)
    g.add_edge(c, d)
    return g


def test_extract_subgraph_missing_node_returns_empty():
    g = _chain_graph()
    sub = extract_subgraph(g, "Z")
    assert len(sub.nodes) == 0


def test_extract_subgraph_unlimited_includes_all_reachable():
    g = _chain_graph()
    sub = extract_subgraph(g, "B")
    names = {n.name.lower() for n in sub.nodes}
    assert names == {"a", "b", "c", "d"}


def test_extract_subgraph_depth_zero_only_centre():
    g = _chain_graph()
    sub = extract_subgraph(g, "B", depth=0)
    assert len(sub.nodes) == 1
    assert list(sub.nodes)[0].name.lower() == "b"


def test_extract_subgraph_depth_one():
    g = _chain_graph()
    sub = extract_subgraph(g, "B", depth=1)
    names = {n.name.lower() for n in sub.nodes}
    assert names == {"a", "b", "c"}


def test_extract_subgraph_edges_are_subset():
    g = _diamond_graph()
    sub = extract_subgraph(g, "B")
    for edge in sub.edges:
        assert edge in g.edges


def test_extract_subgraph_diamond_unlimited():
    g = _diamond_graph()
    sub = extract_subgraph(g, "B")
    names = {n.name.lower() for n in sub.nodes}
    assert names == {"a", "b", "c", "d"}


def test_extract_subgraph_case_insensitive():
    g = _chain_graph()
    sub_upper = extract_subgraph(g, "B", depth=1)
    sub_lower = extract_subgraph(g, "b", depth=1)
    assert {n.name.lower() for n in sub_upper.nodes} == {
        n.name.lower() for n in sub_lower.nodes
    }


def test_extract_subgraph_no_extra_edges():
    g = _chain_graph()
    # depth=1 from B: only A-B and B-C edges should appear
    sub = extract_subgraph(g, "B", depth=1)
    assert len(sub.edges) == 2
