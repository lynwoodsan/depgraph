"""Simple on-disk cache for resolved dependency graphs."""

import json
import hashlib
import os
from pathlib import Path
from typing import Optional

_DEFAULT_CACHE_DIR = Path.home() / ".cache" / "depgraph"


def _cache_key(package_name: str, extras: Optional[tuple] = None) -> str:
    """Generate a stable cache key for a package + extras combination."""
    raw = package_name.lower()
    if extras:
        raw += "|" + ",".join(sorted(e.lower() for e in extras))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _cache_path(key: str, cache_dir: Path) -> Path:
    return cache_dir / f"{key}.json"


def load_cached(package_name: str, cache_dir: Optional[Path] = None) -> Optional[dict]:
    """Load a cached graph dict, or return None if not found / stale."""
    cache_dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
    path = _cache_path(_cache_key(package_name), cache_dir)
    if not path.exists():
        return None
    try:
        with path.open() as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def save_cached(package_name: str, data: dict, cache_dir: Optional[Path] = None) -> None:
    """Persist a graph dict to the cache directory."""
    cache_dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = _cache_path(_cache_key(package_name), cache_dir)
    with path.open("w") as fh:
        json.dump(data, fh, indent=2)


def invalidate(package_name: str, cache_dir: Optional[Path] = None) -> bool:
    """Remove a cached entry. Returns True if something was deleted."""
    cache_dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
    path = _cache_path(_cache_key(package_name), cache_dir)
    if path.exists():
        path.unlink()
        return True
    return False


def clear_all(cache_dir: Optional[Path] = None) -> int:
    """Remove all cached entries. Returns the number of files removed."""
    cache_dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
    if not cache_dir.exists():
        return 0
    removed = 0
    for entry in cache_dir.glob("*.json"):
        entry.unlink()
        removed += 1
    return removed
