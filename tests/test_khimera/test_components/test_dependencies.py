#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_components.test_dependencies
==============================================

Tests for the dependency specifications in plugin models.

See Also
--------
khimera.components.dependencies
"""
import pytest

from khimera.core.core import Component
from khimera.core.dependencies import DependencySpec, PredicateDependency


# --- Mock Classes ---------------------------------------------------------------------------------


class MockComponent(Component):
    """Mock subclass of `Component` for testing."""

    pass


class MockDependencySpec(DependencySpec):
    """Mock subclass of `DependencySpec` for testing."""

    def validate(self, plugin) -> bool:
        """Simple validation: return True if plugin has all required dependencies."""
        return all(dep in plugin.components for dep in self.fields)


class MockPlugin:
    def __init__(self, components):
        self.components = components


# ---- Tests for DependencySpec --------------------------------------------------------------------


def test_dependency_spec_initialization():
    name = "dependency_spec"
    description = "Test dependency specification"
    spec = MockDependencySpec(name=name, fields=["field1", "field2"], description=description)
    assert spec.name == name
    assert "field1" in spec.fields
    assert "field2" in spec.fields
    assert spec.description == description


# --- Tests for PredicateDependency validation --------------------------------------------------------


def mock_predicate(dep1: Component, dep2: Component) -> bool:
    return dep1.name == "dep1" and dep2.name == "dep2"


def test_predicate_dependency_validate_correct():
    """Test PredicateDependency validation with correct dependencies."""
    spec = PredicateDependency(
        name="predicate_dependency", predicate=mock_predicate, fields=["dep1", "dep2"]
    )
    plugin = MockPlugin(
        components={"dep1": MockComponent(name="dep1"), "dep2": MockComponent(name="dep2")}
    )
    assert spec.validate(plugin) is True


def test_predicate_dependency_validate_incorrect():
    """Test PredicateDependency validation with incorrect dependencies."""
    spec = PredicateDependency(
        name="predicate_dependency", predicate=mock_predicate, fields=["dep1", "dep2"]
    )
    plugin = MockPlugin(
        components={"dep1": MockComponent(name="dep1"), "dep2": MockComponent(name="wrong_name")}
    )
    assert spec.validate(plugin) is False


def test_predicate_dependency_validate_missing_dependency():
    """Test PredicateDependency validation with missing dependencies."""
    spec = PredicateDependency(
        name="predicate_dependency", predicate=mock_predicate, fields=["dep1", "dep2"]
    )
    plugin = MockPlugin(components={"dep1": MockComponent(name="dep1")})
    assert spec.validate(plugin) is False
