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
from typing import Type

from khimera.plugins.create import Plugin
from khimera.components.core import FieldSpec, Component
from khimera.plugins.declare import PluginModel


# --- Mock classes for testing ---------------------------------------------------------------------

class MockSpec(FieldSpec):
    """Mock specification class for testing."""
    def __init__(self, name: str):
        self.name = name

    def validate(self, contrib) -> bool:
        """Implement abstract method for validation."""
        return True

@pytest.fixture
def mock_model():
    """Fixture for a mock model."""
    model = PluginModel(name="test_model")
    model.add(MockSpec(name="test_spec"))
    return model

class MockContrib(Component):
    """Mock component class for testing."""
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

@pytest.mark.parametrize("field_name, expected_field_exists", [
    ("test_spec", True),
    ("new_spec", False)
])
def test_add_component(mock_model, field_name, expected_field_exists):
    """Test adding a component to a plugin in various fields."""
    plugin = Plugin(name="test_plugin", model=mock_model)
    contrib = MockContrib(name="test_contrib")
    plugin.add(field_name, contrib)
    assert field_name in plugin.components
    assert len(plugin.components[field_name]) == 1
    assert plugin.components[field_name][0] == contrib
    assert (field_name in mock_model.fields) == expected_field_exists

def test_add_duplicate_component():
    model = MockSpec(name="test_model")
    plugin = Plugin(model=model)

    command_spec = CommandSpec(name="test_command")
    plugin.add("commands", command_spec)

    with pytest.raises(AttributeError):
        plugin.add("commands", command_spec)

def test_get_component():
    model = MockSpec(name="test_model")
    plugin = Plugin(model=model)

    command_spec = CommandSpec(name="test_command")
    plugin.add("commands", command_spec)

    retrieved = plugin.get("commands")
    assert len(retrieved) == 1
    assert retrieved[0] == command_spec

def test_filter_components():
    model = MockSpec(name="test_model")
    plugin = Plugin(model=model)

    command_spec1 = CommandSpec(name="command1")
    command_spec2 = CommandSpec(name="command2")

    plugin.add("commands", command_spec1)
    plugin.add("commands", command_spec2)

    filtered = plugin.filter(category=CommandSpec)

    assert len(filtered) == 2
