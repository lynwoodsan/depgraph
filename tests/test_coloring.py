"""Tests for depgraph.coloring."""

from depgraph.graph import Graph, Node
from depgraph.coloring import (
    ColorMap,
    color_by_role,
    color_by_prefix,
    color_by_function,
    _ROOT_COLOR,
    _LEAF_COLOR,
    _DEFAULT_COLOR,
)


def _build_graph() -> Graph:
    """root -> mid -> leaf"""
    g = Graph()
    root = Node("root")
    mid = Node("mid")
    leaf = Node("leaf")
    g.add_node(root)
    g.add_node(mid)
    g.add_node(leaf)
    g.add_edge(root, mid)
    g.add_edge(mid, leaf)
    return g


def test_color_map_get_returns_default_for_missing():
    cm = ColorMap()
    node = Node("unknown")
    assert cm.get(node) == _DEFAULT_COLOR


def test_color_map_get_case_insensitive():
    cm = ColorMap(colors={"foo": "#123456"})
    assert cm.get(Node("FOO")) == "#123456"
    assert cm.get(Node("foo")) == "#123456"


def test_color_by_role_root_is_green():
    g = _build_graph()
    cm = color_by_role(g)
    assert cm.get(Node("root")) == _ROOT_COLOR


def test_color_by_role_leaf_is_red():
    g = _build_graph()
    cm = color_by_role(g)
    assert cm.get(Node("leaf")) == _LEAF_COLOR


def test_color_by_role_mid_is_default():
    g = _build_graph()
    cm = color_by_role(g)
    assert cm.get(Node("mid")) == _DEFAULT_COLOR


def test_color_by_role_all_nodes_covered():
    g = _build_graph()
    cm = color_by_role(g)
    for node in g.nodes:
        assert cm.get(node) != _DEFAULT_COLOR or node.name == "mid"


def test_color_by_prefix_same_prefix_same_color():
    g = Graph()
    for name in ["django-core", "django-auth", "django-rest"]:
        g.add_node(Node(name))
    cm = color_by_prefix(g)
    colors = [cm.get(Node(n)) for n in ["django-core", "django-auth", "django-rest"]]
    assert colors[0] == colors[1] == colors[2]


def test_color_by_prefix_different_prefix_different_color():
    g = Graph()
    g.add_node(Node("django-core"))
    g.add_node(Node("flask-core"))
    cm = color_by_prefix(g)
    assert cm.get(Node("django-core")) != cm.get(Node("flask-core"))


def test_color_by_prefix_no_separator_uses_full_name():
    g = Graph()
    g.add_node(Node("requests"))
    g.add_node(Node("urllib3"))
    cm = color_by_prefix(g, separator="-")
    # Both have no '-', so each is its own prefix — different colors
    assert cm.get(Node("requests")) != cm.get(Node("urllib3"))


def test_color_by_function_applies_callable():
    g = _build_graph()
    cm = color_by_function(g, lambda n: "#ffffff" if n.name == "root" else "#000000")
    assert cm.get(Node("root")) == "#ffffff"
    assert cm.get(Node("mid")) == "#000000"
    assert cm.get(Node("leaf")) == "#000000"


def test_color_by_function_covers_all_nodes():
    g = _build_graph()
    cm = color_by_function(g, lambda _n: "#aabbcc")
    for node in g.nodes:
        assert cm.get(node) == "#aabbcc"
