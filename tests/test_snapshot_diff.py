"""Tests for depgraph.snapshot_diff."""

import pytest

from depgraph.graph import DependencyGraph, Node
from depgraph.snapshot import Snapshot
from depgraph.snapshot_diff import compare_snapshots, SnapshotComparison


def _graph_abc() -> DependencyGraph:
    g = DependencyGraph()
    a, b, c = Node("A"), Node("B"), Node("C")
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_edge(a, b)
    g.add_edge(b, c)
    return g


def _graph_ab() -> DependencyGraph:
    g = DependencyGraph()
    a, b = Node("A"), Node("B")
    g.add_node(a)
    g.add_node(b)
    g.add_edge(a, b)
    return g


def test_compare_identical_snapshots_no_changes():
    g = _graph_abc()
    s1 = Snapshot.capture(g, label="v1")
    s2 = Snapshot.capture(g, label="v2")
    cmp = compare_snapshots(s1, s2)
    assert not cmp.has_changes()


def test_compare_detects_added_node():
    s1 = Snapshot.capture(_graph_ab(), label="before")
    s2 = Snapshot.capture(_graph_abc(), label="after")
    cmp = compare_snapshots(s1, s2)
    assert cmp.has_changes()
    assert "C" in {n.name for n in cmp.diff.added_nodes}


def test_compare_detects_removed_node():
    s1 = Snapshot.capture(_graph_abc(), label="before")
    s2 = Snapshot.capture(_graph_ab(), label="after")
    cmp = compare_snapshots(s1, s2)
    assert cmp.has_changes()
    assert "C" in {n.name for n in cmp.diff.removed_nodes}


def test_comparison_labels_and_timestamps():
    s1 = Snapshot.capture(_graph_ab(), label="snap-a")
    s2 = Snapshot.capture(_graph_abc(), label="snap-b")
    cmp = compare_snapshots(s1, s2)
    assert cmp.label_before == "snap-a"
    assert cmp.label_after == "snap-b"
    assert cmp.timestamp_before == s1.timestamp
    assert cmp.timestamp_after == s2.timestamp


def test_summary_contains_labels():
    s1 = Snapshot.capture(_graph_ab(), label="old")
    s2 = Snapshot.capture(_graph_abc(), label="new")
    cmp = compare_snapshots(s1, s2)
    summary = cmp.summary()
    assert "old" in summary
    assert "new" in summary


def test_compare_added_edge():
    g1 = _graph_ab()
    g2 = _graph_ab()
    a = Node("A")
    b = Node("B")
    c = Node("C")
    g2.add_node(c)
    g2.add_edge(a, c)
    s1 = Snapshot.capture(g1, label="e1")
    s2 = Snapshot.capture(g2, label="e2")
    cmp = compare_snapshots(s1, s2)
    assert cmp.has_changes()
