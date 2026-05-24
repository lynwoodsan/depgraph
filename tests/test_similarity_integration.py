"""Integration tests combining similarity with diff and stats."""

from depgraph.graph import Graph
from depgraph.similarity import compute_similarity
from depgraph.diff import diff_graphs
from depgraph.stats import compute_stats


def _build(nodes, edges=()):
    g = Graph()
    for n in nodes:
        g.add_node(n)
    for s, d in edges:
        g.add_edge(s, d)
    return g


def test_identical_graphs_have_no_diff_and_full_similarity():
    g = _build(["a", "b", "c"], [("a", "b"), ("b", "c")])
    diff = diff_graphs(g, g)
    sim = compute_similarity(g, g)
    assert not diff.has_changes()
    assert sim.overall == 1.0


def test_added_node_lowers_similarity():
    g1 = _build(["a", "b"], [("a", "b")])
    g2 = _build(["a", "b", "c"], [("a", "b"), ("b", "c")])
    sim = compute_similarity(g1, g2)
    diff = diff_graphs(g1, g2)
    assert sim.node_jaccard < 1.0
    assert "c" in diff.added_nodes


def test_similarity_consistent_with_stats_node_count():
    """Graphs with same node count but different names should have lower similarity."""
    g1 = _build(["a", "b", "c"])
    g2 = _build(["a", "b", "d"])
    sim = compute_similarity(g1, g2)
    s1 = compute_stats(g1)
    s2 = compute_stats(g2)
    assert s1.node_count == s2.node_count
    # Two of three nodes overlap → Jaccard = 2/4 = 0.5
    assert abs(sim.node_jaccard - 0.5) < 1e-9


def test_common_nodes_subset_of_both_graphs():
    g1 = _build(["a", "b", "c"])
    g2 = _build(["b", "c", "d"])
    sim = compute_similarity(g1, g2)
    names1 = {n.name.lower() for n in g1.nodes}
    names2 = {n.name.lower() for n in g2.nodes}
    assert sim.common_nodes <= names1
    assert sim.common_nodes <= names2
