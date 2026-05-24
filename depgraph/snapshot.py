"""Snapshot support: save and compare graph states over time."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from depgraph.graph import DependencyGraph
from depgraph.cached_resolver import _graph_to_dict, _dict_to_graph


@dataclass
class Snapshot:
    label: str
    timestamp: str
    graph_data: dict

    @classmethod
    def capture(cls, graph: DependencyGraph, label: str = "") -> "Snapshot":
        ts = datetime.now(timezone.utc).isoformat()
        return cls(label=label, timestamp=ts, graph_data=_graph_to_dict(graph))

    def restore(self) -> DependencyGraph:
        return _dict_to_graph(self.graph_data)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "graph": self.graph_data,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            label=data.get("label", ""),
            timestamp=data["timestamp"],
            graph_data=data["graph"],
        )


def save_snapshot(snapshot: Snapshot, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return Snapshot.from_dict(data)


def list_snapshots(directory: str) -> List[str]:
    """Return sorted list of .json snapshot files in *directory*."""
    if not os.path.isdir(directory):
        return []
    files = [
        os.path.join(directory, f)
        for f in sorted(os.listdir(directory))
        if f.endswith(".json")
    ]
    return files
