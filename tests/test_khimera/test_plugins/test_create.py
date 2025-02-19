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
import pytest
from khimera.plugins.create import Plugin
from khimera.contributions.core import FieldSpec
from khimera.contributions.commands import CommandSpec


# --- Mock classes for testing ---------------------------------------------------------------------

class MockSpec(FieldSpec):
    """Mock specification class for testing."""
    def __init__(self, name: str):
        self.name = name


# --- Tests for Plugin -----------------------------------------------------------------------------

def test_plugin_initialization():
    """Test initialization of Plugin."""
    model = MockSpec(name="test_model")
    name = "my_plugin"
    version = "1.0.0"
    plugin = Plugin(model=model, name=name, version=version)
    assert plugin.name == name
    assert plugin.version == version
    assert plugin.model == model
    assert len(plugin.contributions) == 0

def test_add_contribution():
    model = MockSpec(name="test_model")
    plugin = Plugin(model=model)

    command_spec = CommandSpec(name="test_command")
    plugin.add("commands", command_spec)

    assert "commands" in plugin.contributions
    assert len(plugin.contributions["commands"]) == 1
    assert plugin.contributions["commands"][0] == command_spec

def test_add_duplicate_contribution():
    model = MockSpec(name="test_model")
    plugin = Plugin(model=model)

    command_spec = CommandSpec(name="test_command")
    plugin.add("commands", command_spec)

    with pytest.raises(AttributeError):
        plugin.add("commands", command_spec)

def test_get_contribution():
    model = MockSpec(name="test_model")
    plugin = Plugin(model=model)

    command_spec = CommandSpec(name="test_command")
    plugin.add("commands", command_spec)

    retrieved = plugin.get("commands")
    assert len(retrieved) == 1
    assert retrieved[0] == command_spec

def test_filter_contributions():
    model = MockSpec(name="test_model")
    plugin = Plugin(model=model)

    command_spec1 = CommandSpec(name="command1")
    command_spec2 = CommandSpec(name="command2")

    plugin.add("commands", command_spec1)
    plugin.add("commands", command_spec2)

    filtered = plugin.filter(category=CommandSpec)

    assert len(filtered) == 2
