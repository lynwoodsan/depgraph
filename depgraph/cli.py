"""Command-line interface for depgraph."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from depgraph.graph import build_graph
from depgraph.svg_renderer import render_svg


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph",
        description="Visualize Python project dependency trees as interactive SVG graphs.",
    )
    parser.add_argument(
        "package",
        help="Root package name to visualise.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output SVG file path (default: <package>.svg).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        metavar="N",
        help="Maximum dependency depth to traverse.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    print(f"Resolving dependencies for '{args.package}'…")
    graph = build_graph(args.package, max_depth=args.max_depth)

    if not graph.all_nodes():
        print(
            f"Error: package '{args.package}' could not be resolved. "
            "Is it installed in the current environment?",
            file=sys.stderr,
        )
        return 1

    svg_content = render_svg(graph)

    output_path = Path(args.output) if args.output else Path(f"{args.package}.svg")
    output_path.write_text(svg_content, encoding="utf-8")
    print(f"SVG written to '{output_path}'.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
