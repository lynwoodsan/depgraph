"""Tests for depgraph.cycles module."""

import pytest
from depgraph.graph import Graph, Node
from depgraph.cycles import find_cycles, has_cycle, find_cycle_nodes, shortest_cycle


def _linear_graph() -> Graph:
    """A -> B -> C (no cycle)."""
    g = Graph()
    a, b, c = Node("A"), Node("B"), Node("C")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_edge(a, b)
    g.add_edge(b, c)
    return g


def _cyclic_graph() -> Graph:
    """A -> B -> C -> A (simple cycle)."""
    g = Graph()
    a, b, c = Node("A"), Node("B"), Node("C")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_edge(a, b)
    g.add_edge(b, c)
    g.add_edge(c, a)
    return g


def _self_loop_graph() -> Graph:
    """A -> A (self-loop)."""
    g = Graph()
    a = Node("A")
    g.add_node(a)
    g.add_edge(a, a)
    return g


def _two_cycle_graph() -> Graph:
    """A->B->A and C->D->C (two independent cycles)."""
    g = Graph()
    a, b, c, d = Node("A"), Node("B"), Node("C"), Node("D")
    for n in (a, b, c, d):
        g.add_node(n)
    g.add_edge(a, b)
    g.add_edge(b, a)
    g.add_edge(c, d)
    g.add_edge(d, c)
    return g


def test_has_cycle_false_for_linear():
    assert has_cycle(_linear_graph()) is False


def test_has_cycle_true_for_cyclic():
    assert has_cycle(_cyclic_graph()) is True


def test_has_cycle_true_for_self_loop():
    assert has_cycle(_self_loop_graph()) is True


def test_find_cycles_empty_for_linear():
    assert find_cycles(_linear_graph()) == []


def test_find_cycles_returns_cycle_nodes():
    cycles = find_cycles(_cyclic_graph())
    assert len(cycles) >= 1
    flat = {n.name.upper() for cycle in cycles for n in cycle}
    assert flat == {"A", "B", "C"}


def test_find_cycle_nodes_deduplicates():
    nodes = find_cycle_nodes(_two_cycle_graph())
    names = {n.name.upper() for n in nodes}
    assert names == {"A", "B", "C", "D"}


def test_find_cycle_nodes_empty_for_acyclic():
    assert find_cycle_nodes(_linear_graph()) == []


def test_shortest_cycle_none_for_acyclic():
    assert shortest_cycle(_linear_graph()) is None


def test_shortest_cycle_returns_list():
    result = shortest_cycle(_cyclic_graph())
    assert isinstance(result, list)
    assert len(result) > 0


def test_shortest_cycle_is_minimal():
    g = _two_cycle_graph()
    result = shortest_cycle(g)
    assert result is not None
    assert len(result) <= 2
