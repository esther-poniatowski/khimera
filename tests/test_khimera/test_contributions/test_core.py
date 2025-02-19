#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_contributions.test_core
=========================================


"""
import pytest

from khimera.contributions.core import Contrib, ContribList, CategorySpec, DependencySpec


# --- Mock Classes ---------------------------------------------------------------------------------

class MockContrib(Contrib):
    """Mock subclass of `Contrib` for testing."""
    pass


class MockCategorySpec(CategorySpec[MockContrib]):
    """Mock subclass of `CategorySpec` for testing."""
    CONTRIB_TYPE = MockContrib

    def validate(self, contrib: MockContrib) -> bool:
        """Simple validation: return True if name is non-empty."""
        return bool(contrib.name)


class MockDependencySpec(DependencySpec[MockContrib]):
    """Mock subclass of `DependencySpec` for testing."""

    def validate(self, plugin) -> bool:
        """Simple validation: return True if plugin has all required dependencies."""
        return all(dep in plugin.contributions for dep in self.dependencies)


# --- Tests for Contrib ----------------------------------------------------------------------------

def test_contrib_initialization():
    """Test initialization of a `Contrib` object and its attributes."""
    name = "test_contrib"
    description = "Test contribution"
    contrib = MockContrib(name=name, description=description)
    assert contrib.name == name
    assert contrib.description == description
    assert contrib.plugin is None


def test_contrib_attach():
    """Test attaching a `Contrib` object to a plugin."""
    plugin_name = "test_plugin"
    contrib = MockContrib(name="test_contrib")
    contrib.attach(plugin_name=plugin_name)
    assert contrib.plugin == plugin_name


def test_contrib_category():
    """Test getting the category of a `Contrib` object."""
    contrib = MockContrib(name="test_contrib")
    assert contrib.category == MockContrib


def test_contrib_list():
    """Test appending and accessing `Contrib` objects in a `ContribList`."""
    name1, name2 = "contrib1", "contrib2"
    contrib_list = ContribList()
    contrib1 = MockContrib(name=name1)
    contrib2 = MockContrib(name=name2)
    contrib_list.append(contrib1)
    contrib_list.append(contrib2)
    assert len(contrib_list) == 2
    assert contrib_list[0].name == name1
    assert contrib_list[1].name == name2


# ---- Tests for Spec (Abstract Base Class) --------------------------------------------------------

def test_spec_initialization():
    name = "test_spec"
    description = "Test spec"
    spec = MockCategorySpec(name=name, description=description)
    assert spec.name == name
    assert spec.description == description


def test_spec_category():
    spec = MockCategorySpec(name="test_spec")
    assert spec.category == MockContrib


# --- Tests for CategorySpec -----------------------------------------------------------------------

@pytest.mark.parametrize(
    "required, unique",
    [(True, False), (False, True), (True, True), (False, False)]
)
def test_category_spec_initialization(required, unique):
    name = "test_spec"
    spec = MockCategorySpec(name=name, required=required, unique=unique)
    assert spec.name == name
    assert spec.required == required
    assert spec.unique == unique


@pytest.mark.parametrize(
    "contrib_name, expected",
    [("valid_contrib", True), ("", False)]
)
def test_category_spec_validation(contrib_name, expected):
    spec = MockCategorySpec(name="test_spec")
    contrib = MockContrib(name=contrib_name)
    assert spec.validate(contrib) == expected


# ---- Tests for DependencySpec --------------------------------------------------------------------

def test_dependency_spec_initialization():
    name = "dependency_spec"
    spec = MockDependencySpec(name=name, dependency1=MockContrib, dependency2=MockContrib)
    assert spec.name == name
    assert "dependency1" in spec.dependencies
    assert "dependency2" in spec.dependencies


def test_dependency_spec_validation():
    class MockPlugin:
        def __init__(self, contributions):
            self.contributions = contributions

    spec = MockDependencySpec(name="dependency_spec", dependency1=MockContrib, dependency2=MockContrib)

    plugin_with_deps = MockPlugin(contributions={"dependency1": MockContrib(name="dep1"), "dependency2": MockContrib(name="dep2")})
    plugin_missing_deps = MockPlugin(contributions={"dependency1": MockContrib(name="dep1")})

    assert spec.validate(plugin_with_deps) is True
    assert spec.validate(plugin_missing_deps) is False
