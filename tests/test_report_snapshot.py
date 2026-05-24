"""Integration: snapshot round-trip through save/load then diff."""

import os
import pytest

from depgraph.graph import DependencyGraph, Node
from depgraph.snapshot import Snapshot, save_snapshot, load_snapshot
from depgraph.snapshot_diff import compare_snapshots


def _make_graph(names, edges=None):
    g = DependencyGraph()
    nodes = {n: Node(n) for n in names}
    for node in nodes.values():
        g.add_node(node)
    for src, dst in (edges or []):
        g.add_edge(nodes[src], nodes[dst])
    return g


def test_full_snapshot_lifecycle(tmp_path):
    g1 = _make_graph(["X", "Y"], [("X", "Y")])
    g2 = _make_graph(["X", "Y", "Z"], [("X", "Y"), ("Y", "Z")])

    p1 = str(tmp_path / "snap1.json")
    p2 = str(tmp_path / "snap2.json")

    save_snapshot(Snapshot.capture(g1, label="first"), p1)
    save_snapshot(Snapshot.capture(g2, label="second"), p2)

    s1 = load_snapshot(p1)
    s2 = load_snapshot(p2)

    cmp = compare_snapshots(s1, s2)
    assert cmp.has_changes()
    assert "Z" in {n.name for n in cmp.diff.added_nodes}


def test_snapshot_persisted_label_survives_reload(tmp_path):
    g = _make_graph(["A"])
    path = str(tmp_path / "labeled.json")
    save_snapshot(Snapshot.capture(g, label="my-label"), path)
    loaded = load_snapshot(path)
    assert loaded.label == "my-label"


def test_no_changes_after_reload(tmp_path):
    g = _make_graph(["P", "Q"], [("P", "Q")])
    path = str(tmp_path / "same.json")
    snap = Snapshot.capture(g, label="stable")
    save_snapshot(snap, path)
    reloaded = load_snapshot(path)
    cmp = compare_snapshots(snap, reloaded)
    assert not cmp.has_changes()
