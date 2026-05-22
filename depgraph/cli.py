"""Command-line interface for depgraph."""

from __future__ import annotations

import argparse
import sys

from depgraph.resolver import resolve_package
from depgraph.graph import DependencyGraph, Node
from depgraph.svg_renderer import render_svg
from depgraph.exporter import export_json, export_dot


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph",
        description="Visualize Python project dependency trees.",
    )
    parser.add_argument("package", help="Root package name to inspect.")
    parser.add_argument(
        "--format",
        choices=["svg", "json", "dot"],
        default="svg",
        help="Output format (default: svg).",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Write output to FILE instead of stdout.",
        metavar="FILE",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=None,
        help="Maximum dependency depth to traverse.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:  # noqa: D401
    """Entry point for the depgraph CLI."""
    args = _parse_args(argv)

    packages = resolve_package(args.package, max_depth=args.depth)

    graph = DependencyGraph()
    for pkg in packages:
        graph.add_node(Node(pkg.name))
    for pkg in packages:
        for dep in pkg.dependencies:
            src = Node(pkg.name)
            dst = Node(dep)
            if dst in graph.nodes:
                graph.add_edge(src, dst)

    if args.format == "svg":
        output = render_svg(graph)
    elif args.format == "json":
        output = export_json(graph)
    else:
        output = export_dot(graph)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
    else:
        sys.stdout.write(output)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
