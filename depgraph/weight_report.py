"""Generate a plain-text report from a WeightedGraph."""

from __future__ import annotations

from depgraph.weight import WeightedGraph, heaviest_nodes


def _fmt_row(rank: int, name: str, weight: float, width: int = 30) -> str:
    return f"{rank:<4} {name:<{width}} {weight:.2f}"


def generate_weight_report(
    wg: WeightedGraph,
    label: str = "",
    top_n: int = 10,
) -> str:
    """Return a formatted weight report string.

    Parameters
    ----------
    wg:
        The weighted graph to report on.
    label:
        Optional title shown at the top of the report.
    top_n:
        How many nodes to list.
    """
    lines: list[str] = []

    title = label if label else "Weight Report"
    lines.append(title)
    lines.append("=" * len(title))
    lines.append(f"Total nodes : {len(wg.graph.nodes)}")
    lines.append(f"Total edges : {len(wg.graph.edges)}")
    lines.append("")
    lines.append(f"{'Rank':<4} {'Node':<30} {'Weight'}")
    lines.append("-" * 44)

    for rank, (name, weight) in enumerate(heaviest_nodes(wg, top_n=top_n), start=1):
        lines.append(_fmt_row(rank, name, weight))

    lines.append("")
    return "\n".join(lines)
