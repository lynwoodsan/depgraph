"""Assign display colors to graph nodes based on various strategies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from depgraph.graph import Graph, Node

# Palette used for prefix / group based coloring
_DEFAULT_PALETTE: List[str] = [
    "#4e79a7",
    "#f28e2b",
    "#e15759",
    "#76b7b2",
    "#59a14f",
    "#edc948",
    "#b07aa1",
    "#ff9da7",
    "#9c755f",
    "#bab0ac",
]

_ROOT_COLOR = "#2ca02c"
_LEAF_COLOR = "#d62728"
_DEFAULT_COLOR = "#aec7e8"


@dataclass
class ColorMap:
    """Mapping from node name to hex color string."""

    colors: Dict[str, str] = field(default_factory=dict)

    def get(self, node: Node, default: str = _DEFAULT_COLOR) -> str:
        return self.colors.get(node.name.lower(), default)


def color_by_role(graph: Graph) -> ColorMap:
    """Color root nodes green, leaf nodes red, and all others the default blue."""
    in_deg: Dict[str, int] = {n.name.lower(): 0 for n in graph.nodes}
    for _src, dst in graph.edges:
        in_deg[dst.name.lower()] = in_deg.get(dst.name.lower(), 0) + 1

    out_deg: Dict[str, int] = {n.name.lower(): 0 for n in graph.nodes}
    for src, _dst in graph.edges:
        out_deg[src.name.lower()] = out_deg.get(src.name.lower(), 0) + 1

    colors: Dict[str, str] = {}
    for node in graph.nodes:
        key = node.name.lower()
        if in_deg.get(key, 0) == 0:
            colors[key] = _ROOT_COLOR
        elif out_deg.get(key, 0) == 0:
            colors[key] = _LEAF_COLOR
        else:
            colors[key] = _DEFAULT_COLOR
    return ColorMap(colors=colors)


def color_by_prefix(
    graph: Graph,
    separator: str = "-",
    palette: Optional[List[str]] = None,
) -> ColorMap:
    """Assign a consistent color per top-level name prefix."""
    if palette is None:
        palette = _DEFAULT_PALETTE
    prefix_index: Dict[str, int] = {}
    colors: Dict[str, str] = {}
    for node in graph.nodes:
        prefix = node.name.split(separator)[0].lower()
        if prefix not in prefix_index:
            prefix_index[prefix] = len(prefix_index) % len(palette)
        colors[node.name.lower()] = palette[prefix_index[prefix]]
    return ColorMap(colors=colors)


def color_by_function(
    graph: Graph,
    func: Callable[[Node], str],
) -> ColorMap:
    """Assign colors using an arbitrary callable *func(node) -> hex color*."""
    return ColorMap(colors={n.name.lower(): func(n) for n in graph.nodes})
