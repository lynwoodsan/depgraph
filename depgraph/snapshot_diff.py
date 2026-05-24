"""Compare two snapshots and report structural changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set, Tuple

from depgraph.snapshot import Snapshot
from depgraph.diff import diff_graphs, GraphDiff


@dataclass
class SnapshotComparison:
    label_before: str
    label_after: str
    timestamp_before: str
    timestamp_after: str
    diff: GraphDiff

    def summary(self) -> str:
        lines = [
            f"Snapshot comparison: '{self.label_before}' -> '{self.label_after}'",
            f"  Before : {self.timestamp_before}",
            f"  After  : {self.timestamp_after}",
            self.diff.summary(),
        ]
        return "\n".join(lines)

    def has_changes(self) -> bool:
        return self.diff.has_changes()


def compare_snapshots(before: Snapshot, after: Snapshot) -> SnapshotComparison:
    """Diff two snapshots and return a SnapshotComparison."""
    g_before = before.restore()
    g_after = after.restore()
    diff = diff_graphs(g_before, g_after)
    return SnapshotComparison(
        label_before=before.label,
        label_after=after.label,
        timestamp_before=before.timestamp,
        timestamp_after=after.timestamp,
        diff=diff,
    )
