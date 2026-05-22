"""Tests for depgraph.svg_renderer."""

from __future__ import annotations

from depgraph.graph import DependencyGraph, Node
from depgraph.svg_renderer import _escape, render_svg


# ---------------------------------------------------------------------------
# Utility tests
# ---------------------------------------------------------------------------

def test_escape_ampersand():
    assert _escape("a&b") == "a&amp;b"


def test_escape_angle_brackets():
    assert _escape("<tag>") == "&lt;tag&gt;"


def test_escape_quotes():
    assert _escape('say "hi"') == "say &quot;hi&quot;"


def test_escape_plain():
    assert _escape("hello") == "hello"


# ---------------------------------------------------------------------------
# render_svg tests
# ---------------------------------------------------------------------------

def _simple_graph() -> DependencyGraph:
    g = DependencyGraph()
    flask = Node("flask", "3.0.0")
    werkzeug = Node("werkzeug", "3.0.1")
    g.add_node(flask)
    g.add_node(werkzeug)
    g.add_edge("flask", "werkzeug")
    return g


def test_render_svg_returns_string():
    g = _simple_graph()
    svg = render_svg(g)
    assert isinstance(svg, str)


def test_render_svg_contains_svg_tag():
    svg = render_svg(_simple_graph())
    assert svg.strip().startswith("<svg")
    assert "</svg>" in svg


def test_render_svg_contains_node_names():
    svg = render_svg(_simple_graph())
    assert "flask" in svg
    assert "werkzeug" in svg


def test_render_svg_contains_edge_line():
    svg = render_svg(_simple_graph())
    assert "<line" in svg


def test_render_svg_contains_circles():
    svg = render_svg(_simple_graph())
    assert svg.count("<circle") == 2


def test_render_svg_empty_graph():
    g = DependencyGraph()
    svg = render_svg(g)
    assert "<svg" in svg
    assert "<circle" not in svg
    assert "<line" not in svg


def test_render_svg_single_node():
    g = DependencyGraph()
    g.add_node(Node("solo", "0.1.0"))
    svg = render_svg(g)
    assert "solo" in svg
    assert "<circle" in svg
    assert "<line" not in svg


def test_render_svg_data_attributes():
    svg = render_svg(_simple_graph())
    assert 'data-package="flask"' in svg
    assert 'data-version="3.0.0"' in svg
