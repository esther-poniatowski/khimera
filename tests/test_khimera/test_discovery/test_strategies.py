#!/usr/bin/env python3 -*- coding: utf-8 -*-
"""
test_khimera.test_discovery.test_strategies
===========================================

Test suite for the plugin discovery strategies in the `khimera.discovery.strategies` module.

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
khimera.discovery.strategies
    Module under test.
pytest_mock.MockFixture
    Mocking fixture for Pytest.
"""
import importlib.metadata
from typing import List, Optional

import pytest
import pytest_mock

from khimera.discovery.strategies import StandardEntryPoint
from khimera.plugins.create import Plugin
from khimera.plugins.declare import PluginModel


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


# --- Tests for `StandardEntryPoint` -------------------------------------------------------


def test_entry_points_finder_init():
    """
    Test initializing an `StandardEntryPoint` instance.

    Test Case:

    - `app_name` attribute: should be assigned.
    - `entry_point_group` : should be assigned as is if provided, otherwise default to
      `{app_name}.plugins`.
    -  `plugins` : empty list.
    """
    app_name = "test_app"
    finder1 = StandardEntryPoint(app_name=app_name)
    assert finder1.app_name == app_name
    assert finder1.entry_point_group == "test_app.plugins"
    assert len(finder1.plugins) == 0
    group = "custom.group"
    finder2 = StandardEntryPoint(app_name=app_name, entry_point_group=group)
    assert finder2.app_name == app_name
    assert finder2.entry_point_group == group
    assert len(finder2.plugins) == 0


def test_entry_points_finder_get_entry_points(mocker: pytest_mock.MockFixture):
    """
    Test the `get_entry_points` method of `StandardEntryPoint`.

    Test Cases:

    - `importlib.metadata.entry_points` should be called with the entry point group.
    - If entry points exist, they should be returned, otherwise an empty list should be returned.
    - If `importlib.metadata.entry_points` raises an error, it should be handled as `RuntimeError`.
    """
    finder = StandardEntryPoint(app_name="test_app")
    mock_entry_point = mocker.Mock()  # entry point returned by `importlib.metadata.entry_points`
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
    Test the `discover` method of `StandardEntryPoint`.

    Test Cases:

    - The `get_entry_points` method should be called during discovery.
    - Each entry point should be loaded using `entry_point.load()`.
    - Only valid Plugin instances should be stored.
    - If an entry point returns an invalid object, a TypeError should be raised.
    - If no valid plugins are discovered, the plugins list should remain empty.
    """
    finder = StandardEntryPoint(app_name="test_app")
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
