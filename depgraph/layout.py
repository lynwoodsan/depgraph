"""Layout engine for positioning nodes in a dependency graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from depgraph.graph import DependencyGraph


@dataclass
class LayoutConfig:
    """Configuration for graph layout."""

    h_spacing: float = 200.0
    v_spacing: float = 100.0
    margin: float = 60.0
    node_width: float = 140.0
    node_height: float = 40.0


def _build_levels(graph: DependencyGraph) -> Dict[str, int]:
    """Assign each node a depth level using BFS from roots."""
    roots = graph.roots()
    levels: Dict[str, int] = {}
    queue = [(r, 0) for r in sorted(roots)]
    while queue:
        name, depth = queue.pop(0)
        if name in levels:
            continue
        levels[name] = depth
        for dep in sorted(graph.dependencies_of(name)):
            if dep not in levels:
                queue.append((dep, depth + 1))
    # Catch any nodes not reachable from roots
    for node in graph.nodes:
        if node.name not in levels:
            levels[node.name] = 0
    return levels


def compute_layout(
    graph: DependencyGraph,
    config: LayoutConfig | None = None,
) -> Dict[str, Tuple[float, float]]:
    """Return a mapping of node name -> (x, y) centre coordinates."""
    if config is None:
        config = LayoutConfig()

    levels = _build_levels(graph)
    # Group nodes by level
    by_level: Dict[int, List[str]] = {}
    for name, lvl in sorted(levels.items()):
        by_level.setdefault(lvl, []).append(name)

    positions: Dict[str, Tuple[float, float]] = {}
    for lvl, names in sorted(by_level.items()):
        x = config.margin + lvl * config.h_spacing
        total_height = len(names) * config.v_spacing
        start_y = config.margin + total_height / 2 - config.v_spacing / 2
        for i, name in enumerate(sorted(names)):
            y = start_y + i * config.v_spacing
            positions[name] = (x, y)

    return positions


def canvas_size(
    positions: Dict[str, Tuple[float, float]],
    config: LayoutConfig | None = None,
) -> Tuple[float, float]:
    """Return (width, height) required to fit all positioned nodes."""
    if config is None:
        config = LayoutConfig()
    if not positions:
        return (config.margin * 2, config.margin * 2)
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    width = max(xs) + config.node_width + config.margin
    height = max(ys) + config.node_height + config.margin
    return (width, height)
