"""Tests for depgraph.search."""

import pytest

from depgraph.graph import DependencyGraph, Node
from depgraph.search import all_paths, find_by_prefix, find_node, shortest_path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_graph() -> DependencyGraph:
    """Build a simple graph:  A -> B -> D
                               A -> C -> D
    """
    g = DependencyGraph()
    a, b, c, d = Node("A"), Node("B"), Node("C"), Node("D")
    for n in (a, b, c, d):
        g.add_node(n)
    g.add_edge(a, b)
    g.add_edge(a, c)
    g.add_edge(b, d)
    g.add_edge(c, d)
    return g


# ---------------------------------------------------------------------------
# find_node
# ---------------------------------------------------------------------------

def test_find_node_exact(  ):
    g = _build_graph()
    node = find_node(g, "B")
    assert node is not None
    assert node.name == "B"


def test_find_node_case_insensitive():
    g = _build_graph()
    assert find_node(g, "b") == find_node(g, "B")


def test_find_node_missing_returns_none():
    g = _build_graph()
    assert find_node(g, "Z") is None


# ---------------------------------------------------------------------------
# find_by_prefix
# ---------------------------------------------------------------------------

def test_find_by_prefix_matches():
    g = DependencyGraph()
    for name in ("requests", "requests-mock", "flask"):
        g.add_node(Node(name))
    results = find_by_prefix(g, "requests")
    names = {n.name for n in results}
    assert names == {"requests", "requests-mock"}


def test_find_by_prefix_case_insensitive():
    g = _build_graph()
    assert find_by_prefix(g, "a") == find_by_prefix(g, "A")


def test_find_by_prefix_no_match():
    g = _build_graph()
    assert find_by_prefix(g, "xyz") == []


# ---------------------------------------------------------------------------
# shortest_path
# ---------------------------------------------------------------------------

def test_shortest_path_direct():
    g = _build_graph()
    path = shortest_path(g, "A", "B")
    assert path is not None
    assert [n.name for n in path] == ["A", "B"]


def test_shortest_path_two_hops():
    g = _build_graph()
    path = shortest_path(g, "A", "D")
    assert path is not None
    # Length should be 3 (A -> B|C -> D)
    assert len(path) == 3
    assert path[0].name == "A"
    assert path[-1].name == "D"


def test_shortest_path_same_node():
    g = _build_graph()
    path = shortest_path(g, "A", "A")
    assert path == [Node("A")]


def test_shortest_path_no_route():
    g = _build_graph()
    # D has no outgoing edges, so D -> A should be None
    assert shortest_path(g, "D", "A") is None


def test_shortest_path_missing_node():
    g = _build_graph()
    assert shortest_path(g, "A", "Z") is None


# ---------------------------------------------------------------------------
# all_paths
# ---------------------------------------------------------------------------

def test_all_paths_count():
    g = _build_graph()
    paths = all_paths(g, "A", "D")
    # Two paths: A->B->D and A->C->D
    assert len(paths) == 2


def test_all_paths_each_starts_and_ends_correctly():
    g = _build_graph()
    for path in all_paths(g, "A", "D"):
        assert path[0].name == "A"
        assert path[-1].name == "D"


def test_all_paths_no_route():
    g = _build_graph()
    assert all_paths(g, "D", "A") == []


def test_all_paths_missing_node():
    g = _build_graph()
    assert all_paths(g, "A", "Z") == []
