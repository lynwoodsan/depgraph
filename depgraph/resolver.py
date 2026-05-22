"""Resolve Python project dependencies from package metadata."""

import importlib.metadata as meta
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Package:
    name: str
    version: str
    dependencies: list[str] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.name.lower())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Package):
            return NotImplemented
        return self.name.lower() == other.name.lower()


def _parse_requirement_name(req: str) -> str:
    """Extract the bare package name from a requirement string."""
    for sep in (">", "<", "=", "!", "[", ";", " "):
        req = req.split(sep)[0]
    return req.strip()


def resolve_package(name: str, _visited: Optional[set[str]] = None) -> Package:
    """Recursively resolve a package and its dependencies.

    Args:
        name: The package name to resolve.
        _visited: Internal set used to avoid infinite recursion.

    Returns:
        A Package instance with resolved dependency names.

    Raises:
        importlib.metadata.PackageNotFoundError: If the package is not installed.
    """
    if _visited is None:
        _visited = set()

    canonical = name.lower()
    if canonical in _visited:
        return Package(name=name, version="(circular)")

    _visited.add(canonical)

    dist = meta.distribution(name)
    version = dist.metadata["Version"] or "unknown"
    raw_requires = dist.requires or []

    # Filter out extras/conditional dependencies
    direct_deps = [
        _parse_requirement_name(r)
        for r in raw_requires
        if "; extra ==" not in r
    ]

    return Package(name=name, version=version, dependencies=direct_deps)


def build_dependency_tree(
    root: str, max_depth: int = 5
) -> dict[str, Package]:
    """Build a flat map of all reachable packages from *root*.

    Args:
        root: The top-level package name.
        max_depth: Maximum recursion depth to prevent very large trees.

    Returns:
        A dict mapping lowercase package names to Package objects.
    """
    tree: dict[str, Package] = {}

    def _walk(name: str, depth: int) -> None:
        key = name.lower()
        if key in tree or depth > max_depth:
            return
        try:
            pkg = resolve_package(name)
        except meta.PackageNotFoundError:
            pkg = Package(name=name, version="not installed")
        tree[key] = pkg
        for dep in pkg.dependencies:
            _walk(dep, depth + 1)

    _walk(root, 0)
    return tree
