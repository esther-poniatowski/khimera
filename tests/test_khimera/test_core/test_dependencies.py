"""
test_khimera.test_core.test_dependencies
========================================

Tests for the dependency specifications in plugin models.

See Also
--------
khimera.core.dependencies
"""
# --- Silenced Errors ---
# pylint: disable=unused-variable
#   Test functions are used, but pylint does not detect it.
# pylint: disable=redefined-outer-name
#   Redefining fixtures is necessary for the tests.

import pytest

from khimera.core.components import Component
from khimera.core.dependencies import DependencySpec, PredicateDependency


# --- Mock Classes ---------------------------------------------------------------------------------


class MockComponent(Component):
    """Mock subclass of `Component` for testing."""


class MockPlugin:
    """Mock class representing a plugin instance, here as a collection of components."""

    def __init__(self, components):
        self.components = components


class MockDependencySpec(DependencySpec):
    """Mock subclass of `DependencySpec` for testing."""

    def validate(self, obj: MockPlugin) -> bool:
        """Simple validation: return True if plugin has all required dependencies."""
        return all(dep in obj.components for dep in self.fields)


# ---- Tests for DependencySpec --------------------------------------------------------------------


def test_dependency_spec_initialization():
    """Test initialization of `Dependency Spec`."""
    name = "dependency_spec"
    description = "Test dependency specification"
    spec = MockDependencySpec(name=name, fields=["field1", "field2"], description=description)
    assert spec.name == name
    assert "field1" in spec.fields
    assert "field2" in spec.fields
    assert spec.description == description


# --- Tests for PredicateDependency validation -----------------------------------------------------


def mock_predicate(dep1: Component, dep2: Component) -> bool:
    """Mock predicate for testing, here checking the names of two dependencies."""
    return dep1.name == "dep1" and dep2.name == "dep2"


@pytest.fixture
def dependency_spec():
    """Fixture for a `PredicateDependency` instance containing two dependencies and a predicate."""
    return PredicateDependency(
        name="predicate_dependency", predicate=mock_predicate, fields=["dep1", "dep2"]
    )


def test_predicate_dependency_validate_correct(dependency_spec: PredicateDependency):
    """Test `PredicateDependency` validation with correct dependencies."""
    plugin = MockPlugin(
        components={"dep1": MockComponent(name="dep1"), "dep2": MockComponent(name="dep2")}
    )
    assert dependency_spec.validate(plugin) is True


def test_predicate_dependency_validate_incorrect(dependency_spec: PredicateDependency):
    """Test `PredicateDependency` validation with incorrect dependencies."""
    plugin = MockPlugin(
        components={"dep1": MockComponent(name="dep1"), "dep2": MockComponent(name="wrong_name")}
    )
    assert dependency_spec.validate(plugin) is False


def test_predicate_dependency_validate_missing_dependency(dependency_spec: PredicateDependency):
    """Test `PredicateDependency` validation with missing dependencies."""
    plugin = MockPlugin(components={"dep1": MockComponent(name="dep1")})
    assert dependency_spec.validate(plugin) is False
