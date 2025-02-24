#!/usr/bin/env python3 -*- coding: utf-8 -*-
"""
test_khimera.test_plugins.test_discover
=======================================

Test suite for the `khimera.discovery.find` module.

Notes
-----
Mocking Strategy:

- Plugin Instances: Mocked to isolate discovery logic from plugin creation logic. Mocked
  attributes: `name`, `version`, `model` (used in filtering).
- PluginModel: Mocked to avoid dependencies on validation logic.

Warning
-------
The `Mock` class has a `name` attribute that conflicts with the `name` attributes of the `Plugin`
and `PluginModel` classes if passed as a keyword argument to the `Mock` constructor. Therefore,
`name` attributes of the mocked instances are set *after* creating the mock objects.

See Also
--------
khimera.discovery.find
    Module under test.
pytest_mock.MockFixture
    Mocking fixture for Pytest.
"""
from typing import Optional

import pytest
import pytest_mock

from khimera.discovery.find import PluginFinder
from khimera.plugins.create import Plugin
from khimera.plugins.declare import PluginModel
from khimera.utils.factories import TypeConstrainedList


# --- Fixtures and Utilities -----------------------------------------------------------------------


def mock_plugin(
    mocker: pytest_mock.MockFixture,
    name: str,
    version: str = "1.0.0",
    model: Optional[PluginModel] = None,
):
    """
    Create a mock `Plugin` instance with a specified name, version, and optional model.

    Arguments
    ---------
    name : str
        Name of the plugin.
    version : str, default="1.0.0"
        Version of the plugin.
    model : PluginModel, optional
        Plugin model associated with the plugin.

    Returns
    -------
    Plugin
        Mocked plugin instance.
    """
    plugin = mocker.Mock(spec=Plugin)
    plugin.name = name
    plugin.version = version
    plugin.model = model
    return plugin


class ConcreteFinder(PluginFinder):
    """Minimal concrete implementation of PluginFinder for testing."""

    def discover(self):
        """Implement the abstract method."""
        pass


# --- Tests for `PluginFinder` ---------------------------------------------------------------------


def test_plugin_finder_init():
    """
    Test initializing a PluginFinder instance.

    Test Case:

    - `plugins` attribute: should be an empty of `TypeConstrainedList(Plugin)`.
    """
    finder = ConcreteFinder()
    assert isinstance(finder.plugins, TypeConstrainedList)
    assert len(finder.plugins) == 0  # starts empty


def test_plugin_finder_store(mocker: pytest_mock.MockerFixture):
    """
    Test the `store` method of `PluginFinder`.

    Test Case:

    - A valid Plugin instance should be stored in the `plugins` list.
    - An invalid type should not be accepted.
    """
    finder = ConcreteFinder()
    plugin = mock_plugin(mocker, "test_plugin")
    # Store the plugin
    finder.store(plugin)
    # Ensure the plugin is in the list
    assert len(finder.plugins) == 1
    assert finder.plugins[0] == plugin
    # Type enforcement: Trying to store an invalid type should raise an error
    with pytest.raises(TypeError):
        finder.store("invalid_plugin")  # Not a Plugin instance


def test_plugin_finder_filter(mocker: pytest_mock.MockerFixture):
    """
    Test the `filter` method of `PluginFinder`.

    Test Cases:

    - If no model is provided, all plugins should be returned.
    - If a model is provided, only plugins matching the model should be returned.
    - If no plugins match the model, an empty list should be returned.
    """
    finder = ConcreteFinder()
    # Create mock plugin models
    modelA = mocker.Mock(spec=PluginModel)
    modelB = mocker.Mock(spec=PluginModel)
    # Create plugins with different models
    plugin1 = mock_plugin(mocker, "plugin1", model=modelA)
    plugin2 = mock_plugin(mocker, "plugin2", model=modelA)
    plugin3 = mock_plugin(mocker, "plugin3", model=modelB)
    # Store plugins
    finder.store(plugin1)
    finder.store(plugin2)
    finder.store(plugin3)
    # Case 1: No model provided -> Expect all plugins
    assert finder.filter(None) == [plugin1, plugin2, plugin3]
    # Case 2: Filter by modelA -> Expect only plugin1 and plugin2
    assert finder.filter(modelA) == [plugin1, plugin2]
    # Case 3: Filter by modelB -> Expect only plugin3
    assert finder.filter(modelB) == [plugin3]
    # Case 4: Filter by an unused model -> Expect an empty list
    unused_model = mocker.Mock(spec=PluginModel)
    assert finder.filter(unused_model) == []


def test_plugin_finder_get(mocker: pytest_mock.MockerFixture):
    """
    Test the `get` method of `PluginFinder`.

    Test Cases:

    - Retrieve a plugin by name when only one exists with that name.
    - Retrieve multiple plugins when multiple versions exist for the same name.
    - Retrieve a specific version of a plugin.
    - Return None when no plugin matches the given name.
    """
    finder = ConcreteFinder()
    # Create plugins with different names and versions
    plugin1 = mock_plugin(mocker, "pluginA", "1.0.0")
    plugin2 = mock_plugin(mocker, "pluginA", "1.1.0")
    plugin3 = mock_plugin(mocker, "pluginB", "2.0.0")
    # Store plugins
    finder.store(plugin1)
    finder.store(plugin2)
    finder.store(plugin3)
    # Case 1: Retrieve a single plugin by name
    assert finder.get("pluginB", None) == plugin3  # only one exists
    # Case 2: Retrieve multiple plugins with the same name but different versions
    assert finder.get("pluginA", None) == [plugin1, plugin2]
    # Case 3: Retrieve a specific version
    assert finder.get("pluginA", "1.0.0") == plugin1
    assert finder.get("pluginA", "1.1.0") == plugin2
    # Case 4: Retrieve a plugin that does not exist
    assert finder.get("pluginX", None) is None


def test_plugin_finder_iter(mocker: pytest_mock.MockerFixture):
    """
    Test that PluginFinder is iterable.

    Test Case:

    - Ensure that iterating over a PluginFinder instance yields its stored plugins in order.
    """
    finder = ConcreteFinder()
    # Create and store plugins
    plugin1 = mock_plugin(mocker, "pluginA", "1.0.0")
    plugin2 = mock_plugin(mocker, "pluginB", "2.0.0")
    finder.store(plugin1)
    finder.store(plugin2)
    # Convert iterator to a list and compare with expected order
    assert list(iter(finder)) == [plugin1, plugin2]
