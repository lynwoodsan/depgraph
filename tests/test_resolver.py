"""Tests for depgraph.resolver."""

import importlib.metadata as meta
from unittest.mock import MagicMock, patch

import pytest

from depgraph.resolver import (
    Package,
    _parse_requirement_name,
    build_dependency_tree,
    resolve_package,
)


# ---------------------------------------------------------------------------
# _parse_requirement_name
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "req, expected",
    [
        ("requests>=2.0", "requests"),
        ("Flask==2.3.1", "Flask"),
        ("numpy", "numpy"),
        ("Pillow[jpeg]>=9", "Pillow"),
        ('pytest; python_version>="3.8"', "pytest"),
        ("scipy !=1.0", "scipy"),
    ],
)
def test_parse_requirement_name(req: str, expected: str) -> None:
    assert _parse_requirement_name(req) == expected


# ---------------------------------------------------------------------------
# Package dataclass
# ---------------------------------------------------------------------------

def test_package_equality_case_insensitive() -> None:
    a = Package(name="Requests", version="2.0")
    b = Package(name="requests", version="2.1")
    assert a == b


def test_package_hash_case_insensitive() -> None:
    a = Package(name="Flask", version="2.0")
    b = Package(name="flask", version="2.0")
    assert hash(a) == hash(b)
    assert len({a, b}) == 1


# ---------------------------------------------------------------------------
# resolve_package
# ---------------------------------------------------------------------------

def _make_dist(version: str, requires: list[str] | None):
    dist = MagicMock()
    dist.metadata = {"Version": version}
    dist.requires = requires
    return dist


@patch("depgraph.resolver.meta.distribution")
def test_resolve_package_no_deps(mock_dist) -> None:
    mock_dist.return_value = _make_dist("1.0.0", None)
    pkg = resolve_package("mypkg")
    assert pkg.name == "mypkg"
    assert pkg.version == "1.0.0"
    assert pkg.dependencies == []


@patch("depgraph.resolver.meta.distribution")
def test_resolve_package_filters_extras(mock_dist) -> None:
    mock_dist.return_value = _make_dist(
        "2.0",
        ["requests>=2", 'pytest; extra == "dev"', "click"],
    )
    pkg = resolve_package("mypkg")
    assert "requests" in pkg.dependencies
    assert "click" in pkg.dependencies
    assert not any("pytest" in d for d in pkg.dependencies)


@patch("depgraph.resolver.meta.distribution")
def test_resolve_package_not_found(mock_dist) -> None:
    mock_dist.side_effect = meta.PackageNotFoundError("ghost")
    with pytest.raises(meta.PackageNotFoundError):
        resolve_package("ghost")


# ---------------------------------------------------------------------------
# build_dependency_tree
# ---------------------------------------------------------------------------

@patch("depgraph.resolver.meta.distribution")
def test_build_dependency_tree_basic(mock_dist) -> None:
    def dist_factory(name):
        data = {
            "root": ("0.1", ["child"]),
            "child": ("1.0", []),
        }
        version, requires = data.get(name.lower(), ("0.0", []))
        return _make_dist(version, requires)

    mock_dist.side_effect = dist_factory
    tree = build_dependency_tree("root")
    assert "root" in tree
    assert "child" in tree
    assert tree["root"].dependencies == ["child"]


@patch("depgraph.resolver.meta.distribution")
def test_build_dependency_tree_missing_dep(mock_dist) -> None:
    def dist_factory(name):
        if name.lower() == "root":
            return _make_dist("1.0", ["missing"])
        raise meta.PackageNotFoundError(name)

    mock_dist.side_effect = dist_factory
    tree = build_dependency_tree("root")
    assert tree["missing"].version == "not installed"
