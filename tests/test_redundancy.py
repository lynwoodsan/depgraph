"""Tests for depgraph.redundancy."""

import pytest

from depgraph.graph import Graph, Node
from depgraph.redundancy import (
    RedundancyReport,
    find_redundant_edges,
    most_redundant_sources,
)


def _build_graph(*edges: tuple) -> Graph:
    g = Graph()
    nodes: set = set()
    for src_name, dst_name in edges:
        src = Node(src_name)
        dst = Node(dst_name)
        nodes.add(src)
        nodes.add(dst)
        g.add_node(src)
        g.add_node(dst)
        g.add_edge(src, dst)
    return g


# A -> B -> C  and  A -> C  (A->C is redundant)
@pytest.fixture()
def diamond_graph() -> Graph:
    return _build_graph(("A", "B"), ("B", "C"), ("A", "C"))


# A -> B -> C  (no redundancy)
@pytest.fixture()
def chain_graph() -> Graph:
    return _build_graph(("A", "B"), ("B", "C"))


def test_no_redundancy_in_chain(chain_graph):
    report = find_redundant_edges(chain_graph)
    assert report.count == 0


def test_redundant_edge_detected(diamond_graph):
    report = find_redundant_edges(diamond_graph)
    assert report.count == 1


def test_redundant_edge_is_ac(diamond_graph):
    report = find_redundant_edges(diamond_graph)
    src_names = {s.name for s, _ in report.redundant_edges}
    dst_names = {d.name for _, d in report.redundant_edges}
    assert "A" in src_names
    assert "C" in dst_names


def test_total_edges_counted(diamond_graph):
    report = find_redundant_edges(diamond_graph)
    assert report.total_edges == 3


def test_ratio_correct(diamond_graph):
    report = find_redundant_edges(diamond_graph)
    assert abs(report.ratio - 1 / 3) < 1e-9


def test_ratio_zero_for_chain(chain_graph):
    report = find_redundant_edges(chain_graph)
    assert report.ratio == 0.0


def test_empty_graph_no_redundancy():
    g = Graph()
    report = find_redundant_edges(g)
    assert report.count == 0
    assert report.total_edges == 0
    assert report.ratio == 0.0


def test_most_redundant_sources(diamond_graph):
    report = find_redundant_edges(diamond_graph)
    top = most_redundant_sources(report, top_n=3)
    assert len(top) == 1
    node, cnt = top[0]
    assert node.name == "A"
    assert cnt == 1


def test_most_redundant_sources_empty():
    report = RedundancyReport(redundant_edges=[], total_edges=0)
    assert most_redundant_sources(report) == []


def test_double_redundancy():
    # A -> B -> C -> D,  A -> C (redundant),  A -> D (redundant)
    g = _build_graph(("A", "B"), ("B", "C"), ("C", "D"), ("A", "C"), ("A", "D"))
    report = find_redundant_edges(g)
    assert report.count == 2
