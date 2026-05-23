"""Caching wrapper around resolver.resolve_package."""

from pathlib import Path
from typing import Optional

from depgraph.resolver import resolve_package
from depgraph.graph import DependencyGraph
from depgraph.exporter import export_json
from depgraph.cache import load_cached, save_cached


def _graph_to_dict(graph: DependencyGraph) -> dict:
    """Serialise a DependencyGraph to a plain dict via export_json."""
    return export_json(graph)


def _dict_to_graph(data: dict) -> DependencyGraph:
    """Reconstruct a DependencyGraph from the dict produced by export_json."""
    graph = DependencyGraph()
    for node_info in data.get("nodes", []):
        graph.add_node(node_info["name"])
    for edge in data.get("edges", []):
        graph.add_edge(edge["from"], edge["to"])
    return graph


def resolve_with_cache(
    package_name: str,
    *,
    use_cache: bool = True,
    cache_dir: Optional[Path] = None,
) -> DependencyGraph:
    """Resolve *package_name* and cache the result.

    Parameters
    ----------
    package_name:
        The top-level package to resolve.
    use_cache:
        When *False* the cache is bypassed entirely (resolve + no write).
    cache_dir:
        Override the default cache directory.
    """
    if use_cache:
        cached = load_cached(package_name, cache_dir=cache_dir)
        if cached is not None:
            return _dict_to_graph(cached)

    graph = resolve_package(package_name)

    if use_cache:
        save_cached(package_name, _graph_to_dict(graph), cache_dir=cache_dir)

    return graph
