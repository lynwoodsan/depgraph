"""Integration tests: clustering interacts correctly with graph + stats."""

from __future__ import annotations

from depgraph.graph import Graph
from depgraph.clustering import cluster_by_connectivity, cluster_by_prefix
from depgraph.stats import compute_stats


def _build_tree() -> Graph:
    """Two-level tree: root -> a, root -> b, a -> c, b -> d."""
    g = Graph()
    for name in ("root", "a", "b", "c", "d"):
        g.add_node(name)
    g.add_edge("root", "a")
    g.add_edge("root", "b")
    g.add_edge("a", "c")
    g.add_edge("b", "d")
    return g


def test_single_component_node_count_matches_stats():
    g = _build_tree()
    stats = compute_stats(g)
    clusters = cluster_by_connectivity(g)
    assert len(clusters) == 1
    assert len(clusters[0].nodes) == stats.node_count


def test_prefix_cluster_union_equals_all_nodes():
    g = _build_tree()
    result = cluster_by_prefix(g, sep=".")
    # No dots → every node is its own prefix group
    all_clustered = set()
    for c in result.values():
        all_clustered |= set(c.nodes)
    all_nodes = {n.name for n in g.nodes}
    assert all_clustered == all_nodes


def test_two_isolated_subgraphs_two_components():
    g = Graph()
    # Component 1
    g.add_node("p1")
    g.add_node("p2")
    g.add_edge("p1", "p2")
    # Component 2
    g.add_node("q1")
    g.add_node("q2")
    g.add_edge("q1", "q2")

    clusters = cluster_by_connectivity(g)
    assert len(clusters) == 2
    names = {frozenset(c.nodes) for c in clusters}
    assert frozenset({"p1", "p2"}) in names
    assert frozenset({"q1", "q2"}) in names


def test_cluster_names_are_unique():
    g = _build_tree()
    clusters = cluster_by_connectivity(g)
    cluster_names = [c.name for c in clusters]
    assert len(cluster_names) == len(set(cluster_names))
