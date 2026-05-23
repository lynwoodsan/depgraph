"""Tests for depgraph.cache."""

import json
import pytest
from pathlib import Path

from depgraph.cache import (
    _cache_key,
    load_cached,
    save_cached,
    invalidate,
    clear_all,
)


@pytest.fixture()
def tmp_cache(tmp_path):
    return tmp_path / "cache"


# --- _cache_key ---

def test_cache_key_is_stable():
    assert _cache_key("requests") == _cache_key("requests")


def test_cache_key_case_insensitive():
    assert _cache_key("Requests") == _cache_key("requests")


def test_cache_key_differs_by_package():
    assert _cache_key("requests") != _cache_key("flask")


def test_cache_key_length():
    assert len(_cache_key("anything")) == 16


# --- round-trip ---

def test_save_and_load(tmp_cache):
    data = {"nodes": ["requests"], "edges": []}
    save_cached("requests", data, cache_dir=tmp_cache)
    result = load_cached("requests", cache_dir=tmp_cache)
    assert result == data


def test_load_missing_returns_none(tmp_cache):
    assert load_cached("nonexistent", cache_dir=tmp_cache) is None


def test_load_corrupt_returns_none(tmp_cache):
    tmp_cache.mkdir(parents=True, exist_ok=True)
    key = _cache_key("broken")
    (tmp_cache / f"{key}.json").write_text("not json")
    assert load_cached("broken", cache_dir=tmp_cache) is None


# --- invalidate ---

def test_invalidate_existing(tmp_cache):
    save_cached("flask", {"nodes": [], "edges": []}, cache_dir=tmp_cache)
    removed = invalidate("flask", cache_dir=tmp_cache)
    assert removed is True
    assert load_cached("flask", cache_dir=tmp_cache) is None


def test_invalidate_missing(tmp_cache):
    assert invalidate("ghost", cache_dir=tmp_cache) is False


# --- clear_all ---

def test_clear_all(tmp_cache):
    for pkg in ("a", "b", "c"):
        save_cached(pkg, {}, cache_dir=tmp_cache)
    removed = clear_all(cache_dir=tmp_cache)
    assert removed == 3


def test_clear_all_empty_dir(tmp_cache):
    assert clear_all(cache_dir=tmp_cache) == 0


def test_clear_all_nonexistent_dir(tmp_path):
    assert clear_all(cache_dir=tmp_path / "no_such_dir") == 0
