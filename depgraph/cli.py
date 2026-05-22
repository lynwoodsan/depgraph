"""Command-line interface for depgraph."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from depgraph.resolver import resolve_package
from depgraph.graph import DependencyGraph
from depgraph.svg_renderer import render_svg
from depgraph.exporter import export_json, export_dot
from depgraph.filter import filter_by_depth, filter_by_packages


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
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
        type=Path,
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=None,
        metavar="N",
        help="Limit dependency tree to N levels deep.",
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=[],
        metavar="PKG",
        help="Packages to exclude from the graph.",
    )
    parser.add_argument(
        "--include",
        nargs="+",
        default=None,
        metavar="PKG",
        help="If given, only these packages (plus root) are shown.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:  # noqa: D401
    args = _parse_args(argv)

    graph = resolve_package(args.package)

    if args.depth is not None:
        try:
            graph = filter_by_depth(graph, args.package, max_depth=args.depth)
        except KeyError as exc:
            print(f"depgraph: error: {exc}", file=sys.stderr)
            return 1

    include_set = set(args.include) if args.include is not None else None
    exclude_set = set(args.exclude) if args.exclude else None
    if include_set is not None or exclude_set is not None:
        graph = filter_by_packages(graph, include=include_set, exclude=exclude_set)

    if args.format == "svg":
        output = render_svg(graph)
    elif args.format == "json":
        import json
        output = json.dumps(export_json(graph), indent=2)
    else:
        output = export_dot(graph)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
