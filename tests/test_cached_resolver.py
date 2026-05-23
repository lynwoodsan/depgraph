"""Tests for depgraph.cached_resolver."""

import pytest
from unittest.mock import patch, MagicMock

from depgraph.graph import DependencyGraph
from depgraph.cached_resolver import (
    _graph_to_dict,
    _dict_to_graph,
    resolve_with_cache,
)


def _simple_graph():
    g = DependencyGraph()
    g.add_node("requests")
    g.add_node("urllib3")
    g.add_edge("requests", "urllib3")
    return g


# --- serialisation round-trip ---

def test_graph_to_dict_has_keys():
    d = _graph_to_dict(_simple_graph())
    assert "nodes" in d
    assert "edges" in d


def test_dict_to_graph_nodes():
    d = _graph_to_dict(_simple_graph())
    g = _dict_to_graph(d)
    names = {n.name.lower() for n in g.nodes}
    assert "requests" in names
    assert "urllib3" in names


def test_dict_to_graph_edges():
    d = _graph_to_dict(_simple_graph())
    g = _dict_to_graph(d)
    edge_pairs = {(e[0].name.lower(), e[1].name.lower()) for e in g.edges}
    assert ("requests", "urllib3") in edge_pairs


def test_roundtrip_empty_graph():
    g = DependencyGraph()
    d = _graph_to_dict(g)
    g2 = _dict_to_graph(d)
    assert len(list(g2.nodes)) == 0


# --- resolve_with_cache ---

def test_cache_miss_calls_resolver(tmp_path):
    fake_graph = _simple_graph()
    with patch("depgraph.cached_resolver.resolve_package", return_value=fake_graph) as mock_resolve:
        result = resolve_with_cache("requests", cache_dir=tmp_path)
    mock_resolve.assert_called_once_with("requests")
    names = {n.name.lower() for n in result.nodes}
    assert "requests" in names


def test_cache_hit_skips_resolver(tmp_path):
    fake_graph = _simple_graph()
    # Populate cache first
    with patch("depgraph.cached_resolver.resolve_package", return_value=fake_graph):
        resolve_with_cache("requests", cache_dir=tmp_path)

    with patch("depgraph.cached_resolver.resolve_package") as mock_resolve:
        result = resolve_with_cache("requests", cache_dir=tmp_path)
    mock_resolve.assert_not_called()
    names = {n.name.lower() for n in result.nodes}
    assert "requests" in names


def test_use_cache_false_always_resolves(tmp_path):
    fake_graph = _simple_graph()
    with patch("depgraph.cached_resolver.resolve_package", return_value=fake_graph) as mock_resolve:
        resolve_with_cache("requests", use_cache=False, cache_dir=tmp_path)
        resolve_with_cache("requests", use_cache=False, cache_dir=tmp_path)
    assert mock_resolve.call_count == 2


def test_use_cache_false_does_not_write(tmp_path):
    fake_graph = _simple_graph()
    with patch("depgraph.cached_resolver.resolve_package", return_value=fake_graph):
        resolve_with_cache("requests", use_cache=False, cache_dir=tmp_path)
    assert not any(tmp_path.iterdir())
