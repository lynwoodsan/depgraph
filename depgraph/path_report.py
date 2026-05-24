"""Human-readable report generation for path analysis results."""

from __future__ import annotations

from typing import List

from depgraph.graph import Graph
from depgraph.path_analysis import PathStats, compute_path_stats


def _fmt_path(path: List[str]) -> str:
    return " -> ".join(path) if path else "(empty)"


def _fmt_row(label: str, value: str, width: int = 24) -> str:
    return f"{label:<{width}}: {value}"


def generate_path_report(graph: Graph, label: str = "") -> str:
    """Return a plain-text path analysis report for *graph*."""
    stats: PathStats = compute_path_stats(graph)
    lines: List[str] = []

    header = f"Path Analysis Report"
    if label:
        header += f" — {label}"
    lines.append(header)
    lines.append("=" * max(len(header), 40))

    lines.append(_fmt_row("Nodes", str(len(graph.nodes))))
    lines.append(_fmt_row("Edges", str(len(graph.edges))))
    lines.append(_fmt_row("Longest path length", str(stats.longest_path_length)))
    lines.append(_fmt_row("Longest path", _fmt_path(stats.longest_path)))

    lines.append("")
    lines.append("Bottlenecks (high path-through count):")
    if stats.bottlenecks:
        for name in stats.bottlenecks:
            cnt = stats.path_counts.get(name, 0)
            lines.append(f"  {name} (paths: {cnt})")
    else:
        lines.append("  (none)")

    lines.append("")
    lines.append("Path counts per node:")
    for name, cnt in sorted(stats.path_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {name:<20} {cnt}")

    return "\n".join(lines)
