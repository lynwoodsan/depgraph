"""Generate a human-readable text report from graph metrics."""

from typing import Dict, Optional

from depgraph.graph import Graph
from depgraph.metrics import NodeMetrics, compute_node_metrics, most_depended_upon


_HEADER = "Dependency Graph Report"
_SEP = "-" * 40


def _fmt_row(m: NodeMetrics) -> str:
    flags = []
    if m.is_root:
        flags.append("root")
    if m.is_leaf:
        flags.append("leaf")
    flag_str = f" [{', '.join(flags)}]" if flags else ""
    return (
        f"  {m.name:<20} in={m.in_degree}  out={m.out_degree}"
        f"  trans_deps={m.transitive_deps}"
        f"  trans_dep_on={m.transitive_dependents}"
        f"  centrality={m.centrality:.4f}{flag_str}"
    )


def generate_report(
    graph: Graph,
    top: int = 5,
    title: Optional[str] = None,
) -> str:
    """Return a formatted text report for *graph*."""
    metrics: Dict[str, NodeMetrics] = compute_node_metrics(graph)
    lines = []

    lines.append(_HEADER if title is None else title)
    lines.append(_SEP)
    lines.append(f"Nodes : {len(graph.nodes)}")
    lines.append(f"Edges : {len(graph.edges)}")
    lines.append("")

    roots = [m for m in metrics.values() if m.is_root]
    leaves = [m for m in metrics.values() if m.is_leaf]
    lines.append(f"Root nodes  ({len(roots)}): {', '.join(m.name for m in roots) or 'none'}")
    lines.append(f"Leaf nodes  ({len(leaves)}): {', '.join(m.name for m in leaves) or 'none'}")
    lines.append("")

    lines.append("All nodes:")
    for m in sorted(metrics.values(), key=lambda x: x.name):
        lines.append(_fmt_row(m))
    lines.append("")

    lines.append(f"Top {top} most depended-upon:")
    for rank, m in enumerate(most_depended_upon(metrics, top=top), start=1):
        lines.append(f"  {rank}. {m.name} (transitive dependents: {m.transitive_dependents})")

    return "\n".join(lines)
