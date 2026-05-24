"""Tests for depgraph.path_report."""

from depgraph.graph import Graph, Node
from depgraph.path_report import generate_path_report


def _chain_graph() -> Graph:
    g = Graph()
    for name in ("A", "B", "C"):
        g.add_node(Node(name))
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    return g


def _empty_graph() -> Graph:
    return Graph()


def test_report_contains_header():
    report = generate_path_report(_chain_graph())
    assert "Path Analysis Report" in report


def test_report_with_label():
    report = generate_path_report(_chain_graph(), label="my-project")
    assert "my-project" in report


def test_report_contains_longest_path():
    report = generate_path_report(_chain_graph())
    assert "A -> B -> C" in report


def test_report_contains_node_count():
    report = generate_path_report(_chain_graph())
    assert "3" in report


def test_report_contains_edge_count():
    report = generate_path_report(_chain_graph())
    assert "2" in report


def test_report_bottlenecks_section_present():
    report = generate_path_report(_chain_graph())
    assert "Bottlenecks" in report


def test_report_path_counts_section_present():
    report = generate_path_report(_chain_graph())
    assert "Path counts per node" in report


def test_report_empty_graph_no_crash():
    report = generate_path_report(_empty_graph())
    assert "Path Analysis Report" in report
    assert "(none)" in report


def test_report_is_string():
    report = generate_path_report(_chain_graph())
    assert isinstance(report, str)
