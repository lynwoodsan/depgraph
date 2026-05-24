"""Generate a plain-text impact analysis report."""

from __future__ import annotations

from depgraph.graph import Graph, Node
from depgraph.impact import ImpactResult, analyse_impact, most_impactful


def _fmt_row(label: str, value: str, width: int = 28) -> str:
    return f"  {label:<{width}} {value}"


def generate_impact_report(
    graph: Graph,
    changed_package: str,
    *,
    label: str = "",
    top_n: int = 5,
) -> str:
    """Return a human-readable impact report for *changed_package*.

    Parameters
    ----------
    graph:
        The dependency graph to analyse.
    changed_package:
        The package assumed to have changed.
    label:
        Optional report title suffix.
    top_n:
        Number of most-impactful nodes to include in the summary table.
    """
    result: ImpactResult = analyse_impact(graph, changed_package)
    title = f"Impact Report — {changed_package}"
    if label:
        title += f" ({label})"

    lines: list[str] = [
        title,
        "=" * len(title),
        "",
        _fmt_row("Changed package:", changed_package),
        _fmt_row("Affected nodes:", str(result.count)),
        _fmt_row("Affected edges:", str(len(result.affected_edges))),
        "",
    ]

    if result.affected_nodes:
        lines.append("  Affected packages (by distance):")
        sorted_nodes = sorted(
            result.depth_map.items(), key=lambda kv: (kv[1], kv[0].name)
        )
        for node, depth in sorted_nodes:
            marker = " *" if node.name.lower() == changed_package.lower() else ""
            lines.append(f"    [{depth}] {node.name}{marker}")
    else:
        lines.append("  No packages affected (package not found in graph).")

    lines += [
        "",
        f"  Top {top_n} most impactful packages overall:",
    ]
    ranking = most_impactful(graph, top_n=top_n)
    for rank, (node, score) in enumerate(ranking, start=1):
        lines.append(f"    {rank:>2}. {node.name:<20} impact score: {score}")

    lines.append("")
    return "\n".join(lines)
