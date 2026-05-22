"""Render a DependencyGraph as an interactive SVG string."""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from depgraph.graph import DependencyGraph, Node

# Layout constants
_NODE_RADIUS = 30
_WIDTH = 800
_HEIGHT = 600
_FONT_SIZE = 11


def _compute_positions(nodes: List[Node]) -> Dict[str, Tuple[float, float]]:
    """Place nodes evenly on a circle."""
    positions: Dict[str, Tuple[float, float]] = {}
    n = len(nodes)
    if n == 0:
        return positions
    cx, cy = _WIDTH / 2, _HEIGHT / 2
    radius = min(_WIDTH, _HEIGHT) / 2 - _NODE_RADIUS * 2
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n - math.pi / 2
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions[node.name.lower()] = (x, y)
    return positions


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_svg(graph: DependencyGraph) -> str:
    """Return an SVG string visualising the dependency graph."""
    nodes = graph.all_nodes()
    positions = _compute_positions(nodes)
    lines: List[str] = []

    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{_WIDTH}" height="{_HEIGHT}" '
        f'viewBox="0 0 {_WIDTH} {_HEIGHT}">'
    )
    lines.append(
        "<style>"
        "circle { fill: #4a90d9; stroke: #2c5f8a; stroke-width: 2; cursor: pointer; }"
        "circle:hover { fill: #e07b39; }"
        "text { fill: #fff; font-family: sans-serif; "
        f"font-size: {_FONT_SIZE}px; text-anchor: middle; dominant-baseline: middle; """
        "pointer-events: none; }"
        "line { stroke: #888; stroke-width: 1.5; marker-end: url(#arrow); }"
        "</style>"
    )
    # Arrow marker
    lines.append(
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" '
        'refX="6" refY="3" orient="auto">'
        '<path d="M0,0 L0,6 L9,3 z" fill="#888"/></marker></defs>'
    )

    # Draw edges
    for node in nodes:
        key = node.name.lower()
        x1, y1 = positions.get(key, (_WIDTH / 2, _HEIGHT / 2))
        for dep_key in graph.edges.get(key, []):
            if dep_key in positions:
                x2, y2 = positions[dep_key]
                lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')

    # Draw nodes
    for node in nodes:
        key = node.name.lower()
        x, y = positions.get(key, (_WIDTH / 2, _HEIGHT / 2))
        label = _escape(node.name)
        version = _escape(node.version)
        lines.append(
            f'<g class="node" data-package="{label}" data-version="{version}">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{_NODE_RADIUS}"/>'
            f'<text x="{x:.1f}" y="{y:.1f}">{label}</text>'
            f"</g>"
        )

    lines.append("</svg>")
    return "\n".join(lines)
