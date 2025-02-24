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
from typing import Optional, List

from khimera.utils.factories import TypeConstrainedList
from khimera.plugins.declare import PluginModel
from khimera.plugins.create import Plugin


# --- Plugin Entry Point ---------------------------------------------------------------------------

class PluginEntryPoint:
    """
    Represents an entry point for a plugin in the host application, inspired by the `EntryPoint`
    class from `importlib.metadata`.

    Attributes
    ----------
    path : str or Path
        Path to the directory on the filesystem containing the plugin package.
    value : str
        Reference pointing to to a `Plugin` instance. Format: 'package.module:object'.
    module : str
        Name of the module containing the referenced object.
        It refers to the full Python import path, including both the package name and the module
        name. Format: 'package.module'.
    attr : str
        Name of the specific `Plugin` object within the module. Format: 'object'.

    Methods
    -------
    load()
        Dynamically imports and returns the referenced `Plugin` object.

    Examples
    --------
    Consider the following plugin package structure:

    .. code-block:: none

        path/to/project/
        ├── my_package/
        │   ├── __init__.py
        │   └── plugins.py
        └── ...

    The `plugins.py` module contains the following `Plugin` object:

    .. code-block:: python

        from khimera.plugins.create import Plugin
        from host_app.models import MyPluginModel

        my_plugin = Plugin(
            name='my_plugin',
            version='0.1.0',
            model=MyPluginModel,
            ...
        )

    Create a plugin entry point for this plugin:

    >>> entry_point = PluginEntryPoint(path='path/to/package', value='my_package.plugins:MyPlugin')

    Load the referenced plugin object:

    >>> plugin = entry_point.load()
    >>> print(plugin)
    Plugin(name='my_plugin', version='0.1.0', model=MyPluginModel, ...)

    Notes
    -----
    This class is inspired by the `EntryPoint` class from the `importlib.metadata` module.

    - Shared attributes: `name`, `value`, `module`, `attr`, `load`.
    - Omitted attributes: `name`, `group` (relevant for entry points specified in `pyproject.toml`).
    - New attributes: `path` (custom directory path to the plugin package).

    """
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value
        self.module, self.attr = value.split(':')

    def load(self) -> Plugin:
        """
        Dynamically imports and returns the referenced `Plugin` object.

        Returns
        -------
        Plugin
            Referenced `Plugin` object.
        """
        module = importlib.import_module(self.module)
        return getattr(module, self.attr)


# --- Abstract Strategy - PluginFinder -------------------------------------------------------------


class PluginFinder(ABC):
    """
    Abstract base class for plugins discovery strategies for the host application.

    Attributes
    ----------
    plugins : TypeConstrainedList[Plugin]
        All the discovered plugins.

    Examples
    --------
    Initialize a plugin finder to discover plugins from the `pyproject.toml` files:

    >>> finder = EntryPointsFinderPyproject(app_name='myapp')

    Discover the plugins provided by the installed packages for the host application:

    >>> finder.discover()

    Filter the discovered plugins by model:

    >>> plugins = finder.filter(model=MyPluginModel)
    >>> print(plugins)
    [Plugin(name='my_plugin', version='0.1.0', ...), ...]

    Get a specific plugin by name and version:

    >>> plugin = finder.get(name='my_plugin', version='0.1.0')
    >>> print(plugin)
    Plugin(name='my_plugin', version='0.1.0', ...)

    Notes
    -----
    The plugin discovery mechanism is designed to be comprehensive and to collect as many plugins as
    possible before selecting them, validating them, or resolving conflicts between them.

    To do so, all the plugins are stored in a list rather than a dictionary. Thus, plugins are not
    named, which allows to store multiple plugins of the same name but different versions.
    """
    def __init__(self):
        self.plugins = TypeConstrainedList(Plugin) # automatic type checking

    @abstractmethod
    def discover(self):
        """Discovers plugins by implementing the discovery strategy."""
        pass

    def store(self, plugin: Plugin) -> None:
        """
        Stores a discovered plugin.

        Notes
        -----
        Type checking is performed automatically by the `TypeConstrainedList` class.
        """
        self.plugins.append(plugin)

    def __iter__(self):
        """Iterates over the discovered plugins."""
        return iter(self.plugins)

    def get(self, name : str, version : Optional[str]) -> Optional[Plugin | List[Plugin]]:
        """
        Get a plugin by name, and optionally by version.

        Arguments
        ---------
        name : str
            Name of the plugin to get.
        version : str, optional
            Version of the plugin to get.

        Returns
        -------
        Plugin | List[Plugin] | None
            Plugins matching the name and version, or None if no plugin is found.
            If plugins correctly follow the name and version conventions, a single plugin should be
            retrieved.
        """
        found = [plugin for plugin in self.plugins if plugin.name == name and (version is None or plugin.version == version)]
        return found[0] if len(found) == 1 else found or None

    def filter(self, model : Optional[PluginModel]) -> List[Plugin]:
        """
        Filter the discovered plugins by model.

        Arguments
        ---------
        model : PluginModel
            Plugin model specifying the expected structure and components of the plugins.
            If not provided, all the plugins are considered regardless of the model they adhere to.
        """
        if model is None:
            return self.plugins
        return [plugin for plugin in self.plugins if plugin.model == model]


# --- Concrete Strategy - EntryPointsFinderPyproject -----------------------------------------------


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
                ):
        super().__init__()
        self.app_name = app_name
        self.entry_point_group = entry_point_group or f"{self.app_name}.plugins"

    def discover(self):
        """
        Discovers plugins from entry points in the `pyproject.toml` files of plugin packages.

        Raises
        ------
        TypeError
            If a plugin loaded from an entry point is not an instance of `Plugin`.
        """
        entry_points = self.get_entry_points()
        for entry_point in entry_points:
            plugin = entry_point.load() # expected: `Plugin` instance
            if not isinstance(plugin, Plugin):
                raise TypeError(
                    f"Invalid plugin loaded from entry point {entry_point.name}. "
                    "Expected `Plugin` instance."
                )
            self.store(plugin)

    def get_entry_points(self):
        """
        Finds all installed plugins that declare an entry point for the host application.

        Returns
        -------
        List[importlib.metadata.EntryPoint]
            Entry points for the host application.

        Raises
        ------
        RuntimeError
            If the entry points cannot be retrieved.
        """
        try:
            return importlib.metadata.entry_points(group=self.entry_point_group)
        except Exception as exc:
            raise RuntimeError(f"Failed to retrieve entry points for {self.entry_point_group}: {exc}")
