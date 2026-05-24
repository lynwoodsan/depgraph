"""Tests for depgraph.weight."""

from __future__ import annotations

import pytest

from depgraph.graph import Graph, Node
from depgraph.weight import (
    WeightedGraph,
    heaviest_nodes,
    weight_by_function,
    weight_by_out_degree,
    weight_by_reachability,
)


def _build_graph() -> Graph:
    """Build a simple diamond: A -> B, A -> C, B -> D, C -> D."""
    g = Graph()
    a, b, c, d = Node("A"), Node("B"), Node("C"), Node("D")
    for n in (a, b, c, d):
        g.add_node(n)
    g.add_edge(a, b)
    g.add_edge(a, c)
    g.add_edge(b, d)
    g.add_edge(c, d)
    return g


def test_weight_by_out_degree_root_has_highest():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    assert wg.node_weight("A") == 2.0


def test_weight_by_out_degree_leaf_is_zero():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    assert wg.node_weight("D") == 0.0


def test_weight_by_out_degree_mid_nodes():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    assert wg.node_weight("B") == 1.0
    assert wg.node_weight("C") == 1.0


def test_weight_by_reachability_root_reaches_all():
    g = _build_graph()
    wg = weight_by_reachability(g)
    # A can reach B, C, D
    assert wg.node_weight("A") == 3.0


def test_weight_by_reachability_leaf_reaches_none():
    g = _build_graph()
    wg = weight_by_reachability(g)
    assert wg.node_weight("D") == 0.0


def test_weight_by_function_node_fn():
    g = _build_graph()
    wg = weight_by_function(g, node_fn=lambda n: 42.0)
    for node in g.nodes:
        assert wg.node_weight(node.name) == 42.0


def test_weight_by_function_edge_fn():
    g = _build_graph()
    wg = weight_by_function(g, edge_fn=lambda s, d: 7.0)
    for src, dst in g.edges:
        assert wg.edge_weight(src.name, dst.name) == 7.0


def test_default_node_weight_is_one():
    g = _build_graph()
    wg = WeightedGraph(graph=g)
    assert wg.node_weight("unknown") == 1.0


def test_default_edge_weight_is_one():
    g = _build_graph()
    wg = WeightedGraph(graph=g)
    assert wg.edge_weight("x", "y") == 1.0


def test_heaviest_nodes_ordering():
    g = _build_graph()
    wg = weight_by_reachability(g)
    top = heaviest_nodes(wg, top_n=2)
    assert top[0][0] == "a"  # stored lowercase
    assert top[0][1] >= top[1][1]


def test_heaviest_nodes_top_n_respected():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    top = heaviest_nodes(wg, top_n=2)
    assert len(top) == 2


def test_weight_case_insensitive_lookup():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    assert wg.node_weight("a") == wg.node_weight("A")
