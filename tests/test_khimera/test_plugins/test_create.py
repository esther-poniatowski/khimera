#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_plugins.test_create
======================================

Tests for the creation of plugin instances.

See Also
--------
khimera.plugins.create
"""
import pytest

from khimera.plugins.create import Plugin
from khimera.core.components import Component
from khimera.core.specifications import FieldSpec
from khimera.plugins.declare import PluginModel


# --- Mock classes for testing ---------------------------------------------------------------------


class MockSpec(FieldSpec):
    """Mock specification class for testing."""

    def __init__(self, name: str):
        self.name = name

    def validate(self, comp) -> bool:
        """Implement abstract method for validation."""
        return True


@pytest.fixture
def mock_model():
    """Fixture for a mock model."""
    model = PluginModel(name="test_model")
    model.add(MockSpec(name="test_spec"))
    return model


class MockComponent(Component):
    """Mock component class for testing."""

    def __init__(self, name: str):
        self.name = name


class MockComponent2(Component):
    """Mock component class for testing different categories."""

    def __init__(self, name: str):
        self.name = name


# --- Tests for Plugin -----------------------------------------------------------------------------


def test_plugin_initialization(mock_model):
    """Test initialization of Plugin."""
    name = "my_plugin"
    version = "1.0.0"
    plugin = Plugin(model=mock_model, name=name, version=version)
    assert plugin.name == name
    assert plugin.version == version
    assert plugin.model == mock_model
    assert len(plugin.components) == 0


@pytest.mark.parametrize(
    "names, expected", [(False, lambda comp: comp), (True, lambda comp: comp.name)]
)
def test_get_component(mock_model, names, expected):
    """
    Test retrieving a component from a plugin.

    Notes
    -----
    Test `get` before `add` since the `get` method is used in `add`.
    """
    plugin = Plugin(model=mock_model, name="test_plugin")
    field_key = "test_spec"
    comp = MockComponent(name="test_comp")
    plugin.add(key=field_key, comp=comp)
    retrieved = plugin.get(field_key, names=names)
    assert len(retrieved) == 1
    assert retrieved[0] == expected(comp)


@pytest.mark.parametrize(
    "field_name, expected_field_exists", [("test_spec", True), ("new_spec", False)]
)
def test_add_component(mock_model, field_name, expected_field_exists):
    """Test adding a component to a plugin in various fields."""
    plugin = Plugin(name="test_plugin", model=mock_model)
    comp = MockComponent(name="test_contrib")
    plugin.add(field_name, comp)
    assert field_name in plugin.components
    assert len(plugin.components[field_name]) == 1
    assert plugin.components[field_name][0] == comp
    assert (field_name in mock_model.fields) == expected_field_exists


def test_add_duplicate_component(mock_model):
    plugin = Plugin(model=mock_model, name="test_plugin")
    field_key = "test_spec"
    comp = MockComponent(name="test_comp")
    plugin.add(key=field_key, comp=comp)
    with pytest.raises(AttributeError):
        plugin.add(key=field_key, comp=comp)


def test_remove_component(mock_model):
    """Test removing a named component from a plugin."""
    plugin = Plugin(model=mock_model, name="test_plugin")
    field_key = "test_spec"
    comp = MockComponent(name="test_comp")
    plugin.add(key=field_key, comp=comp)
    plugin.remove(key=field_key, comp_name=comp.name)
    assert len(plugin.components[field_key]) == 0


def test_remove_field(mock_model):
    """Test removing a field (no `comp_name` argument)."""
    plugin = Plugin(model=mock_model, name="test_plugin")
    field_key = "test_spec"
    comp = MockComponent(name="test_comp")
    plugin.add(key=field_key, comp=comp)
    plugin.remove(key=field_key)  # no `comp_name` argument
    assert field_key not in plugin.components


def test_remove_nonexistent_component(mock_model):
    plugin = Plugin(model=mock_model, name="test_plugin")
    field_key = "test_spec"
    comp = MockComponent(name="test_comp")
    plugin.add(key=field_key, comp=comp)  # initialize the field
    with pytest.raises(KeyError):
        plugin.remove(key=field_key, comp_name="nonexistent")


def test_filter_components(mock_model):
    """Test filtering components from a plugin by category."""
    model = MockSpec(name="test_model")
    plugin = Plugin(model=mock_model, name="test_plugin")
    spec1 = MockComponent(name="comp2")
    spec2 = MockComponent2(name="comp1")
    field_key = "test_spec"
    plugin.add(key=field_key, comp=spec1)
    plugin.add(key=field_key, comp=spec2)
    filtered = plugin.filter(category=MockComponent)
    assert len(filtered) == 1


def test_copy(mock_model):
    """Test copying a plugin instance (via the `DeepCopyable` mixin)."""
    plugin = Plugin(model=mock_model, name="test_plugin")
    comp = MockComponent(name="test_comp")
    plugin.add(key="test_spec", comp=comp)
    copied = plugin.copy()
    assert copied.name == plugin.name
    assert copied.version == plugin.version
    assert copied is not plugin
    assert copied.components == plugin.components
    assert copied.model == plugin.model


def test_equality(mock_model):
    """Test equality comparison of plugin instances (via the `DeepComparable` mixin)."""
    plugin1 = Plugin(model=mock_model, name="test_plugin")
    plugin2 = Plugin(model=mock_model, name="test_plugin")
    assert plugin1 == plugin2
    plugin1.add(key="test_spec", comp=MockComponent(name="test_comp"))
    assert plugin1 != plugin2
    plugin2.add(key="test_spec", comp=MockComponent(name="test_comp"))
    assert plugin1 == plugin2
