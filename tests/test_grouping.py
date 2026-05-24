"""Tests for depgraph.grouping."""

from depgraph.graph import Graph, Node
from depgraph.grouping import (
    group_by_depth,
    group_by_function,
    group_by_prefix,
    largest_group,
)


def _build_graph() -> Graph:
    """Build a simple A -> B -> C, A -> D graph."""
    g = Graph()
    a, b, c, d = Node("A"), Node("B"), Node("C"), Node("D")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_node(d)
    g.add_edge(a, b)
    g.add_edge(b, c)
    g.add_edge(a, d)
    return g


def test_group_by_prefix_separates_correctly():
    g = Graph()
    for name in ["django-rest", "django-filter", "flask-login", "requests"]:
        g.add_node(Node(name))
    groups = group_by_prefix(g, separator="-", max_parts=1)
    assert set(groups["django"]) == {Node("django-rest"), Node("django-filter")}
    assert groups["flask"] == [Node("flask-login")]
    assert "" in groups  # 'requests' has no separator


def test_group_by_prefix_no_separator_goes_to_empty_key():
    g = Graph()
    g.add_node(Node("requests"))
    g.add_node(Node("urllib3"))
    groups = group_by_prefix(g, separator="-", max_parts=1)
    assert Node("requests") in groups[""]
    assert Node("urllib3") in groups[""]


def test_group_by_function_uses_callable():
    g = _build_graph()
    groups = group_by_function(g, lambda n: "upper" if n.name.isupper() else "other")
    assert all(n.name.isupper() for n in groups.get("upper", []))


def test_group_by_depth_roots_at_zero():
    g = _build_graph()
    groups = group_by_depth(g)
    assert Node("A") in groups[0]


def test_group_by_depth_correct_levels():
    g = _build_graph()
    groups = group_by_depth(g)
    assert Node("B") in groups[1]
    assert Node("D") in groups[1]
    assert Node("C") in groups[2]


def test_group_by_depth_covers_all_nodes():
    g = _build_graph()
    groups = group_by_depth(g)
    all_grouped = [n for nodes in groups.values() for n in nodes]
    assert set(all_grouped) == set(g.nodes)


def test_group_by_depth_empty_graph():
    g = Graph()
    groups = group_by_depth(g)
    assert groups == {}


def test_largest_group_returns_correct_key():
    groups = {"a": [Node("x"), Node("y"), Node("z")], "b": [Node("w")]}
    assert largest_group(groups) == "a"


def test_largest_group_empty_returns_none():
    assert largest_group({}) is None
