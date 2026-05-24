"""Tests for depgraph.snapshot."""

import json
import os
import pytest

from depgraph.graph import DependencyGraph, Node
from depgraph.snapshot import (
    Snapshot,
    save_snapshot,
    load_snapshot,
    list_snapshots,
)


def _build_graph() -> DependencyGraph:
    g = DependencyGraph()
    a, b, c = Node("A"), Node("B"), Node("C")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_edge(a, b)
    g.add_edge(b, c)
    return g


def test_capture_creates_snapshot():
    g = _build_graph()
    snap = Snapshot.capture(g, label="v1")
    assert snap.label == "v1"
    assert snap.timestamp
    assert "nodes" in snap.graph_data


def test_restore_roundtrip():
    g = _build_graph()
    snap = Snapshot.capture(g, label="test")
    g2 = snap.restore()
    assert {n.name for n in g2.nodes} == {"A", "B", "C"}


def test_to_dict_and_from_dict():
    g = _build_graph()
    snap = Snapshot.capture(g, label="round")
    d = snap.to_dict()
    snap2 = Snapshot.from_dict(d)
    assert snap2.label == snap.label
    assert snap2.timestamp == snap.timestamp


def test_save_and_load_snapshot(tmp_path):
    g = _build_graph()
    snap = Snapshot.capture(g, label="persist")
    path = str(tmp_path / "snap.json")
    save_snapshot(snap, path)
    assert os.path.exists(path)
    loaded = load_snapshot(path)
    assert loaded.label == "persist"
    g2 = loaded.restore()
    assert len(list(g2.nodes)) == 3


def test_list_snapshots_empty(tmp_path):
    assert list_snapshots(str(tmp_path)) == []


def test_list_snapshots_returns_json_files(tmp_path):
    g = _build_graph()
    for name in ("a.json", "b.json", "c.txt"):
        path = str(tmp_path / name)
        if name.endswith(".json"):
            save_snapshot(Snapshot.capture(g, label=name), path)
        else:
            open(path, "w").close()
    result = list_snapshots(str(tmp_path))
    assert len(result) == 2
    assert all(r.endswith(".json") for r in result)


def test_list_snapshots_nonexistent_dir():
    assert list_snapshots("/nonexistent/path/xyz") == []


def test_snapshot_label_defaults_to_empty():
    g = _build_graph()
    snap = Snapshot.capture(g)
    assert snap.label == ""
