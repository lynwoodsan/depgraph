"""Integration tests combining path_analysis with other depgraph modules."""

from depgraph.graph import Graph, Node
from depgraph.path_analysis import compute_path_stats, find_bottlenecks
from depgraph.stats import compute_stats
from depgraph.search import shortest_path
from depgraph.metrics import compute_node_metrics


def _build_tree() -> Graph:
    """        root
             /    \\
            a      b
           / \\
          c   d
    """
    g = Graph()
    for name in ("root", "a", "b", "c", "d"):
        g.add_node(Node(name))
    g.add_edge("root", "a")
    g.add_edge("root", "b")
    g.add_edge("a", "c")
    g.add_edge("a", "d")
    return g


def test_longest_path_length_consistent_with_max_depth():
    g = _build_tree()
    stats = compute_path_stats(g)
    graph_stats = compute_stats(g)
    # longest path should span max_depth + 1 nodes
    assert stats.longest_path_length == graph_stats.max_depth + 1


def test_bottleneck_matches_high_in_degree_node():
    g = _build_tree()
    # 'a' has 2 outgoing children; root has 2 too — both appear in multiple paths
    bottlenecks = find_bottlenecks(g, threshold=1)
    assert "root" in bottlenecks


def test_longest_path_nodes_are_connected():
    """Every consecutive pair in the longest path must be a graph edge."""
    g = _build_tree()
    stats = compute_path_stats(g)
    path = stats.longest_path
    edge_set = {(s.lower(), d.lower()) for (s, d) in g.edges}
    for i in range(len(path) - 1):
        assert (path[i].lower(), path[i + 1].lower()) in edge_set


def test_path_counts_sum_matches_expected():
    g = _build_tree()
    counts = compute_path_stats(g).path_counts
    # root appears in all 3 leaf-paths (root->a->c, root->a->d, root->b)
    assert counts["root"] == 3
    # b is a leaf with one path through it
    assert counts["b"] == 1


def test_compute_metrics_and_path_stats_agree_on_roots():
    g = _build_tree()
    metrics = compute_node_metrics(g)
    path_stats = compute_path_stats(g)
    root_metrics = [m for m in metrics if m.is_root]
    # root nodes should appear in the most paths
    max_count = max(path_stats.path_counts.values())
    for rm in root_metrics:
        assert path_stats.path_counts[rm.name] == max_count
