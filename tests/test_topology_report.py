"""Tests for depgraph.topology_report."""

from depgraph.graph import Graph, Node
from depgraph.topology_report import generate_topology_report


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _chain_graph() -> Graph:
    g = Graph()
    a, b, c = Node("alpha"), Node("beta"), Node("gamma")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_edge(a, b)
    g.add_edge(b, c)
    return g


def _empty_graph() -> Graph:
    return Graph()


def _cyclic_graph() -> Graph:
    g = Graph()
    x, y = Node("x"), Node("y")
    g.add_node(x)
    g.add_node(y)
    g.add_edge(x, y)
    g.add_edge(y, x)
    return g


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_report_contains_header():
    report = generate_topology_report(_chain_graph())
    assert "Topological Report" in report


def test_report_with_label():
    report = generate_topology_report(_chain_graph(), label="my-project")
    assert "my-project" in report


def test_report_node_count():
    report = generate_topology_report(_chain_graph())
    assert "Nodes : 3" in report


def test_report_edge_count():
    report = generate_topology_report(_chain_graph())
    assert "Edges : 2" in report


def test_report_layer_count():
    report = generate_topology_report(_chain_graph())
    assert "Layers: 3" in report


def test_report_contains_layer_assignment_header():
    report = generate_topology_report(_chain_graph())
    assert "Layer assignment:" in report


def test_report_layer_zero_contains_alpha():
    report = generate_topology_report(_chain_graph())
    assert "Layer  0: alpha" in report


def test_report_contains_topological_order_header():
    report = generate_topology_report(_chain_graph())
    assert "Topological order:" in report


def test_report_order_arrow_notation():
    report = generate_topology_report(_chain_graph())
    assert "->" in report


def test_report_cycle_warning():
    report = generate_topology_report(_cyclic_graph())
    assert "cycle detected" in report


def test_report_empty_graph_no_crash():
    report = generate_topology_report(_empty_graph())
    assert "Topological Report" in report


def test_report_empty_graph_none_order():
    report = generate_topology_report(_empty_graph())
    assert "(none)" in report
