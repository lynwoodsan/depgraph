"""Tests for depgraph.weight_report."""

from __future__ import annotations

from depgraph.graph import Graph, Node
from depgraph.weight import weight_by_out_degree, weight_by_reachability
from depgraph.weight_report import generate_weight_report


def _build_graph() -> Graph:
    g = Graph()
    a, b, c = Node("alpha"), Node("beta"), Node("gamma")
    for n in (a, b, c):
        g.add_node(n)
    g.add_edge(a, b)
    g.add_edge(a, c)
    g.add_edge(b, c)
    return g


def test_report_contains_header():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    report = generate_weight_report(wg)
    assert "Weight Report" in report


def test_report_with_custom_label():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    report = generate_weight_report(wg, label="My Custom Label")
    assert "My Custom Label" in report


def test_report_contains_node_count():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    report = generate_weight_report(wg)
    assert "Total nodes : 3" in report


def test_report_contains_edge_count():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    report = generate_weight_report(wg)
    assert "Total edges : 3" in report


def test_report_lists_nodes():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    report = generate_weight_report(wg)
    assert "alpha" in report


def test_report_top_n_limits_rows():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    report = generate_weight_report(wg, top_n=1)
    # Only the heaviest node should appear in ranked rows
    lines = [l for l in report.splitlines() if l.startswith("1 ") or l.startswith("2 ")]
    assert len(lines) == 1


def test_report_rank_column_present():
    g = _build_graph()
    wg = weight_by_reachability(g)
    report = generate_weight_report(wg)
    assert "Rank" in report


def test_report_weight_column_present():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    report = generate_weight_report(wg)
    assert "Weight" in report


def test_report_separator_line():
    g = _build_graph()
    wg = weight_by_out_degree(g)
    report = generate_weight_report(wg)
    assert "---" in report
