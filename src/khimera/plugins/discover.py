#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.discover
========================

Discovers plugins on the host application side.

Classes
-------
PluginFinder
    Abstract base class for plugins discovery strategies.
EntryPointsFinderPyproject
    Discovery strategy based on entry points declared in `pyproject.toml` files.

See Also
--------
"""
from abc import ABC, abstractmethod
import importlib.metadata
from typing import Optional, Dict
import warnings

from khimera.utils.factories import TypeConstrainedDict
from khimera.plugins.declare import PluginModel
from khimera.plugins.create import Plugin


class PluginFinder(ABC):
    """
    Abstract base class for plugins discovery strategies for the host application.

    Attributes
    ----------
    plugins : Dict[str, Plugin]
        Discovered plugins.
        Keys: Names of the plugins. Values: Plugin instances.
    """
    def __init__(self):
        self.plugins = TypeConstrainedDict(str, Plugin) # automatic type checking

    @abstractmethod
    def discover(self):
        """Discovers plugins by implementing the discovery strategy."""
        pass

    def register(self, plugin: Plugin) -> None:
        """
        Default registering behavior. Override this method to customize the registration process.

        Warnings
        --------
        UserWarning
            If the plugin is not an instance of the 'Plugin' class (no `name` attribute).
            If the plugin name is already registered.
        """
        if not isinstance(plugin, Plugin):
            warnings.warn("Ignored plugin: not instance of 'Plugin' class.", UserWarning)
        if plugin.name in self.plugins:
            warnings.warn(f"Ignored plugin: name '{plugin.name}' already registered.", UserWarning)
        self.plugins[plugin.name] = plugin

    def get(self, name : str, version : Optional[str]) -> Optional[Plugin]:
        """
        Get a plugin by name, and optionally by model.

        Arguments
        ---------
        name : str
            Name of the plugin to get.
        version : str, optional
            Version of the plugin to get.

        Returns
        -------
        Plugin
            Plugin instance if found, otherwise None.
        """
        plugin = self.plugins.get(name)
        if version and not plugin.version == version:
            return None
        return plugin

    def filter(self, model : PluginModel) -> Dict[str, Plugin]:
        """
        Filter the discovered plugins by model.

        Arguments
        ---------
        model : PluginModel
            Plugin model specifying the expected structure and contributions of the plugins.
            If not provided, all the plugins are considered regardless of the model they adhere to.
        """
        return {name: plugin for name, plugin in self.plugins.items() if plugin.model == model}


class EntryPointsFinderPyproject(PluginFinder):
    """
    Discovers plugins for the host application based on entry points declared in `pyproject.toml` of
    the plugin packages.

    Attributes
    ----------
    app_name : str
        Name of the application requiring plugin discovery.
    entry_point_group : str, optional
        Entry point group where external plugins declare their entry points.
        If not provided, defaults to '{app_name}.plugins'.

    Notes
    -----
    The discovery mechanism does not differentiate between 'internal' plugins (packaged with the
    host application) and 'external' plugins (installed as third-party packages). All plugins are
    treated as entry points and are registered during the package installation process, as long as
    the host application itself defines its own plugins in entry points in its `pyproject.toml` file
    in the appropriate section.
    """
    def __init__(self,
                app_name: str,
                entry_point_group: Optional[str] = None,
                model : PluginModel = None,
                ):
        super().__init__()
        self.app_name = app_name
        self.entry_point_group = entry_point_group or f"{self.app_name}.plugins"

    def discover(self):
        """Discovers plugins from entry points in the `pyproject.toml` files of plugin packages."""
        entry_points = self.get_entry_points()
        for entry_point in entry_points:
            plugin = entry_point.load() # expected: `Plugin` instance
            self.register(plugin) # automatic checks

    def get_entry_points(self):
        """Finds all installed plugins that declare an entry point for the host application."""
        return importlib.metadata.entry_points(group=self.entry_point_group)
