"""Tests for depgraph.graph module."""

import pytest

from depgraph.graph import DependencyGraph, Node


def test_node_hash_case_insensitive():
    assert hash(Node("Flask")) == hash(Node("flask"))


def test_node_equality_case_insensitive():
    assert Node("Flask") == Node("FLASK")


def test_node_inequality():
    assert Node("Flask") != Node("Django")


def test_add_node():
    g = DependencyGraph()
    node = g.add_node("requests")
    assert node.name == "requests"
    assert "requests" in g


def test_add_node_deduplicates():
    g = DependencyGraph()
    g.add_node("Requests")
    g.add_node("requests")
    assert len(g) == 1


def test_add_edge_creates_nodes():
    g = DependencyGraph()
    g.add_edge("A", "B")
    assert "A" in g
    assert "B" in g


def test_dependencies_of():
    g = DependencyGraph()
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    deps = g.dependencies_of("A")
    assert set(deps) == {"B", "C"}


def test_dependencies_of_missing_node():
    g = DependencyGraph()
    assert g.dependencies_of("ghost") == []


def test_dependents_of():
    g = DependencyGraph()
    g.add_edge("A", "C")
    g.add_edge("B", "C")
    assert set(g.dependents_of("C")) == {"A", "B"}


def test_roots_single_chain():
    g = DependencyGraph()
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    assert g.roots() == ["A"]


def test_roots_multiple():
    g = DependencyGraph()
    g.add_edge("A", "C")
    g.add_edge("B", "C")
    assert set(g.roots()) == {"A", "B"}


def test_leaves():
    g = DependencyGraph()
    g.add_edge("A", "B")
    g.add_edge("A", "C")
    assert set(g.leaves()) == {"B", "C"}


def test_edges_list():
    g = DependencyGraph()
    g.add_edge("X", "Y")
    assert ("X", "Y") in g.edges


def test_len():
    g = DependencyGraph()
    g.add_node("A")
    g.add_node("B")
    assert len(g) == 2


def test_contains_case_insensitive():
    g = DependencyGraph()
    g.add_node("Flask")
    assert "flask" in g
    assert "FLASK" in g
