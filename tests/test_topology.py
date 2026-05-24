"""Tests for depgraph.topology."""

from depgraph.graph import Graph, Node
from depgraph.topology import (
    TopologicalOrder,
    layer_count,
    nodes_in_layer,
    topological_sort,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _chain_graph() -> Graph:
    """a -> b -> c"""
    g = Graph()
    a, b, c = Node("a"), Node("b"), Node("c")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_edge(a, b)
    g.add_edge(b, c)
    return g


def _diamond_graph() -> Graph:
    """a -> b, a -> c, b -> d, c -> d"""
    g = Graph()
    a, b, c, d = Node("a"), Node("b"), Node("c"), Node("d")
    for n in (a, b, c, d):
        g.add_node(n)
    g.add_edge(a, b)
    g.add_edge(a, c)
    g.add_edge(b, d)
    g.add_edge(c, d)
    return g


def _cyclic_graph() -> Graph:
    """a -> b -> c -> a"""
    g = Graph()
    a, b, c = Node("a"), Node("b"), Node("c")
    for n in (a, b, c):
        g.add_node(n)
    g.add_edge(a, b)
    g.add_edge(b, c)
    g.add_edge(c, a)
    return g


# ---------------------------------------------------------------------------
# topological_sort
# ---------------------------------------------------------------------------

def test_chain_order_length():
    topo = topological_sort(_chain_graph())
    assert len(topo.order) == 3


def test_chain_order_respects_dependencies():
    topo = topological_sort(_chain_graph())
    assert topo.order.index("a") < topo.order.index("b")
    assert topo.order.index("b") < topo.order.index("c")


def test_chain_no_cycle():
    topo = topological_sort(_chain_graph())
    assert topo.has_cycle is False


def test_diamond_order_a_first():
    topo = topological_sort(_diamond_graph())
    assert topo.order[0] == "a"


def test_diamond_d_last():
    topo = topological_sort(_diamond_graph())
    assert topo.order[-1] == "d"


def test_cyclic_has_cycle_flag():
    topo = topological_sort(_cyclic_graph())
    assert topo.has_cycle is True


def test_cyclic_partial_order_is_empty():
    topo = topological_sort(_cyclic_graph())
    # No node has in-degree 0 in a pure cycle
    assert len(topo.order) == 0


# ---------------------------------------------------------------------------
# layers
# ---------------------------------------------------------------------------

def test_chain_layer_count():
    topo = topological_sort(_chain_graph())
    assert layer_count(topo) == 3


def test_chain_a_in_layer_0():
    topo = topological_sort(_chain_graph())
    assert topo.layer_of("a") == 0


def test_chain_b_in_layer_1():
    topo = topological_sort(_chain_graph())
    assert topo.layer_of("b") == 1


def test_chain_c_in_layer_2():
    topo = topological_sort(_chain_graph())
    assert topo.layer_of("c") == 2


def test_diamond_d_in_deepest_layer():
    topo = topological_sort(_diamond_graph())
    max_layer = max(topo.layers.keys())
    assert "d" in topo.layers[max_layer]


def test_nodes_in_layer_returns_list():
    topo = topological_sort(_chain_graph())
    assert nodes_in_layer(topo, 0) == ["a"]


def test_nodes_in_missing_layer_returns_empty():
    topo = topological_sort(_chain_graph())
    assert nodes_in_layer(topo, 99) == []


def test_layer_of_case_insensitive():
    topo = topological_sort(_chain_graph())
    assert topo.layer_of("A") == 0
