"""Export dependency graphs to various formats (JSON, DOT/Graphviz)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from depgraph.graph import DependencyGraph


def export_json(graph: "DependencyGraph") -> str:
    """Serialize a DependencyGraph to a JSON string.

    Returns a JSON object with ``nodes`` (list of name strings) and
    ``edges`` (list of ``[source, target]`` pairs).
    """
    nodes = sorted(node.name for node in graph.nodes)
    edges = [
        [src.name, dst.name]
        for src, dst in sorted(
            graph.edges, key=lambda e: (e[0].name.lower(), e[1].name.lower())
        )
    ]
    return json.dumps({"nodes": nodes, "edges": edges}, indent=2)


def export_dot(graph: "DependencyGraph", graph_name: str = "dependencies") -> str:
    """Serialize a DependencyGraph to a Graphviz DOT string."""
    lines = [f'digraph "{graph_name}" {{', "    rankdir=LR;"]

    for node in sorted(graph.nodes, key=lambda n: n.name.lower()):
        escaped = node.name.replace('"', '\\"')
        lines.append(f'    "{escaped}";')

    for src, dst in sorted(
        graph.edges, key=lambda e: (e[0].name.lower(), e[1].name.lower())
    ):
        src_escaped = src.name.replace('"', '\\"')
        dst_escaped = dst.name.replace('"', '\\"')
        lines.append(f'    "{src_escaped}" -> "{dst_escaped}";')

    lines.append("}")
    return "\n".join(lines) + "\n"


def export_csv(graph: "DependencyGraph") -> str:
    """Serialize a DependencyGraph to a CSV string.

    Each row represents a directed edge in the format ``source,target``.
    The output includes a header row and edges sorted alphabetically.
    """
    lines = ["source,target"]
    for src, dst in sorted(
        graph.edges, key=lambda e: (e[0].name.lower(), e[1].name.lower())
    ):
        lines.append(f"{src.name},{dst.name}")
    return "\n".join(lines) + "\n"
