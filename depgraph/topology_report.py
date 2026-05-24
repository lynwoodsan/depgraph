"""Plain-text report for topological ordering results."""

from __future__ import annotations

from depgraph.graph import Graph
from depgraph.topology import TopologicalOrder, topological_sort


_HEADER = "Topological Report"
_SEP = "-" * 40


def _fmt_layer_row(layer: int, nodes: list[str]) -> str:
    node_str = ", ".join(sorted(nodes))
    return f"  Layer {layer:>2}: {node_str}"


def generate_topology_report(
    graph: Graph,
    label: str = "",
) -> str:
    """Return a human-readable topology report for *graph*.

    Parameters
    ----------
    graph:
        The dependency graph to analyse.
    label:
        Optional title suffix shown in the header.
    """
    topo: TopologicalOrder = topological_sort(graph)

    title = _HEADER if not label else f"{_HEADER}: {label}"
    lines: list[str] = [title, _SEP]

    node_count = len(graph.nodes)
    edge_count = len(graph.edges)
    lines.append(f"Nodes : {node_count}")
    lines.append(f"Edges : {edge_count}")
    lines.append(f"Layers: {len(topo.layers)}")

    if topo.has_cycle:
        lines.append("WARNING: cycle detected — order is incomplete")

    lines.append(_SEP)
    lines.append("Layer assignment:")

    for layer_idx in sorted(topo.layers.keys()):
        lines.append(_fmt_layer_row(layer_idx, topo.layers[layer_idx]))

    lines.append(_SEP)
    lines.append("Topological order:")
    lines.append("  " + " -> ".join(topo.order) if topo.order else "  (none)")

    return "\n".join(lines)
