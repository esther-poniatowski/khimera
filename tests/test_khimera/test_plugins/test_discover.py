#!/usr/bin/env python3 -*- coding: utf-8 -*-
"""
test_khimera.test_plugins.test_discover
=======================================

Test suite for the `PluginFinder` and `EntryPointsFinderPyproject` classes in the
`khimera.plugins.discover` module.

Notes
-----
Mocking Strategy:

- Plugin Instances: Mocked to isolate discovery logic from plugin creation logic. Mocked
  attributes: `name`, `version`, `model` (used in filtering).
- PluginModel: Mocked to avoid dependencies on validation logic.
- Entry Points: Mocked to control the discovery process and avoid dependencies on external
  package metadata.
- Metadata Retrieval (`importlib.metadata.entry_points`): Mocked to simulate installed plugins
  with declared entry points.
- Entry Point Loading (`entry_point.load`): Mocked to return controlled plugin instances.

Warning
-------
The `Mock` class has a `name` attribute that conflicts with the `name` attributes of the `Plugin`
and `PluginModel` classes if passed as a keyword argument to the `Mock` constructor. Therefore,
`name` attributes of the mocked instances are set *after* creating the mock objects.

See Also
--------
khimera.plugins.discover
    Module under test.
pytest_mock.MockFixture
    Mocking fixture for Pytest.
"""
from typing import List, Optional

import pytest
import pytest_mock
import importlib.metadata

from khimera.plugins.discover import PluginFinder, EntryPointsFinderPyproject
from khimera.plugins.create import Plugin
from khimera.plugins.declare import PluginModel
from khimera.utils.factories import TypeConstrainedList


# --- Fixtures and Utilities -----------------------------------------------------------------------


def mock_plugin(mocker: pytest_mock.MockFixture, name: str, version: str = "1.0.0", model: Optional[PluginModel] = None):
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


def patch_entry_points(mocker: pytest_mock.MockFixture, entry_points: List):
    """
    Patch `importlib.metadata.entry_points` to return a controlled set of entry points.

    Arguments
    ---------
    entry_points : list
        Mocked entry points to return.

    Returns
    -------
    None
    """
    mocker.patch.object(importlib.metadata, "entry_points", return_value=entry_points)


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


# --- Tests for `EntryPointsFinderPyproject` -------------------------------------------------------


def test_entry_points_finder_init():
    """
    Test initializing an `EntryPointsFinderPyproject` instance.

    Test Case:

    - `app_name` attribute: should be assigned.
    - `entry_point_group` : should be assigned as is if provided, otherwise default to
      `{app_name}.plugins`.
    -  `plugins` : empty list.
    """
    app_name = "test_app"
    finder1 = EntryPointsFinderPyproject(app_name=app_name)
    assert finder1.app_name == app_name
    assert finder1.entry_point_group == "test_app.plugins"
    assert len(finder1.plugins) == 0
    group = "custom.group"
    finder2 = EntryPointsFinderPyproject(app_name=app_name, entry_point_group=group)
    assert finder2.app_name == app_name
    assert finder2.entry_point_group == group
    assert len(finder2.plugins) == 0


def test_entry_points_finder_get_entry_points(mocker: pytest_mock.MockFixture):
    """
    Test the `get_entry_points` method of `EntryPointsFinderPyproject`.

    Test Cases:

    - `importlib.metadata.entry_points` should be called with the entry point group.
    - If entry points exist, they should be returned, otherwise an empty list should be returned.
    - If `importlib.metadata.entry_points` raises an error, it should be handled as `RuntimeError`.
    """
    finder = EntryPointsFinderPyproject(app_name="test_app")
    mock_entry_point = mocker.Mock() # entry point returned by `importlib.metadata.entry_points`
    # Case 1: Entry points exist
    patch_entry_points(mocker, [mock_entry_point])
    assert finder.get_entry_points() == [mock_entry_point]
    # Case 2: No entry points exist
    patch_entry_points(mocker, [])
    assert finder.get_entry_points() == []
    # Case 3: `importlib.metadata.entry_points` raises an error
    mocker.patch.object(importlib.metadata, "entry_points", side_effect=Exception("Metadata error"))
    with pytest.raises(RuntimeError, match="Failed to retrieve entry points"):
        finder.get_entry_points()


def test_entry_points_finder_discover(mocker: pytest_mock.MockFixture):
    """
    Test the `discover` method of `EntryPointsFinderPyproject`.

    Test Cases:

    - The `get_entry_points` method should be called during discovery.
    - Each entry point should be loaded using `entry_point.load()`.
    - Only valid Plugin instances should be stored.
    - If an entry point returns an invalid object, a TypeError should be raised.
    - If no valid plugins are discovered, the plugins list should remain empty.
    """
    finder = EntryPointsFinderPyproject(app_name="test_app")
    # Mock entry points
    valid_plugin = mock_plugin(mocker, "valid_plugin")
    invalid_plugin = "invalid_plugin"  # not Plugin
    entry_point_valid = mocker.Mock()
    entry_point_valid.load.return_value = valid_plugin
    entry_point_invalid = mocker.Mock()
    entry_point_invalid.load.return_value = invalid_plugin
    # Case 1: Discover valid plugins
    mocker.patch.object(finder, "get_entry_points", return_value=[entry_point_valid])
    finder.discover()
    assert len(finder.plugins) == 1
    assert finder.plugins[0] == valid_plugin
    # Case 2: Discover invalid plugin
    finder.plugins.clear()  # Reset state
    mocker.patch.object(finder, "get_entry_points", return_value=[entry_point_invalid])
    with pytest.raises(TypeError, match="Invalid plugin loaded from entry point"):
        finder.discover()
    # Case 3: No entry points found
    finder.plugins.clear()
    mocker.patch.object(finder, "get_entry_points", return_value=[])
    finder.discover()
    assert len(finder.plugins) == 0
