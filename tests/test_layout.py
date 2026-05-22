"""Tests for depgraph.layout module."""

from depgraph.graph import DependencyGraph
from depgraph.layout import LayoutConfig, _build_levels, canvas_size, compute_layout


def _chain_graph() -> DependencyGraph:
    """A -> B -> C"""
    g = DependencyGraph()
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    return g


def _wide_graph() -> DependencyGraph:
    """A -> B, A -> C, A -> D"""
    g = DependencyGraph()
    g.add_node("A")
    for dep in ("B", "C", "D"):
        g.add_node(dep)
        g.add_edge("A", dep)
    return g


def test_build_levels_chain():
    levels = _build_levels(_chain_graph())
    assert levels["A"] == 0
    assert levels["B"] == 1
    assert levels["C"] == 2


def test_build_levels_wide():
    levels = _build_levels(_wide_graph())
    assert levels["A"] == 0
    assert levels["B"] == 1
    assert levels["C"] == 1
    assert levels["D"] == 1


def test_compute_layout_returns_all_nodes():
    g = _chain_graph()
    positions = compute_layout(g)
    assert set(positions.keys()) == {"A", "B", "C"}


def test_compute_layout_x_increases_with_depth():
    positions = compute_layout(_chain_graph())
    assert positions["A"][0] < positions["B"][0] < positions["C"][0]


def test_compute_layout_wide_same_x():
    positions = compute_layout(_wide_graph())
    xs = {positions[n][0] for n in ("B", "C", "D")}
    assert len(xs) == 1, "All depth-1 nodes should share the same x coordinate"


def test_compute_layout_custom_config():
    cfg = LayoutConfig(h_spacing=300.0, v_spacing=150.0, margin=20.0)
    positions = compute_layout(_chain_graph(), config=cfg)
    # A is at depth 0, B at depth 1 — x difference should equal h_spacing
    assert abs(positions["B"][0] - positions["A"][0] - 300.0) < 1e-6


def test_canvas_size_empty():
    cfg = LayoutConfig(margin=50.0)
    w, h = canvas_size({}, config=cfg)
    assert w == 100.0
    assert h == 100.0


def test_canvas_size_nonzero():
    positions = compute_layout(_chain_graph())
    w, h = canvas_size(positions)
    assert w > 0
    assert h > 0


def test_isolated_node_assigned_level_zero():
    g = DependencyGraph()
    g.add_node("Alone")
    levels = _build_levels(g)
    assert levels["Alone"] == 0
