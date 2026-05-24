"""Integration tests combining ancestors and subgraph extraction."""

from depgraph.graph import Graph, Node
from depgraph.ancestors import get_ancestors, get_descendants
from depgraph.subgraph import extract_subgraph


def _build_tree() -> Graph:
    """Root -> (X, Y); X -> (P, Q); Y -> Q"""
    g = Graph()
    root, x, y, p, q = (
        Node("root"), Node("X"), Node("Y"), Node("P"), Node("Q")
    )
    for n in (root, x, y, p, q):
        g.add_node(n)
    g.add_edge(root, x)
    g.add_edge(root, y)
    g.add_edge(x, p)
    g.add_edge(x, q)
    g.add_edge(y, q)
    return g


def test_subgraph_nodes_match_neighbourhood():
    g = _build_tree()
    sub = extract_subgraph(g, "X")
    sub_names = {n.name.lower() for n in sub.nodes}
    ancestors = get_ancestors(g, "X")
    descendants = get_descendants(g, "X")
    expected = ancestors | descendants | {"x"}
    assert sub_names == expected


def test_subgraph_ancestors_only_via_depth():
    g = _build_tree()
    # depth=1 upward from Q should include X, Y, root (within 1 hop from Q)
    sub = extract_subgraph(g, "Q", depth=1)
    names = {n.name.lower() for n in sub.nodes}
    # Q's direct parents are X and Y
    assert "x" in names
    assert "y" in names
    assert "q" in names


def test_descendants_consistent_with_subgraph():
    g = _build_tree()
    desc = get_descendants(g, "root")
    sub = extract_subgraph(g, "root")
    sub_names = {n.name.lower() for n in sub.nodes} - {"root"}
    # all descendants should appear in the subgraph
    assert desc.issubset(sub_names)


def test_empty_graph_returns_empty_subgraph():
    g = Graph()
    sub = extract_subgraph(g, "anything")
    assert len(sub.nodes) == 0
    assert len(sub.edges) == 0
