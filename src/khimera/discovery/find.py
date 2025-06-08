"""
khimera.discovery.find
======================

Discovers plugins on the host application side.

Classes
-------
PluginEntryPoint
    Represents an entry point for a plugin in the host application.
PluginFinder
    Abstract base class for plugins discovery strategies.

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
        self.module, self.attr = value.split(":")

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

    >>> finder = FromInstalledFinder(app_name='myapp')

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
        self.plugins = TypeConstrainedList(Plugin)  # automatic type checking

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

    def get(self, name: str, version: Optional[str]) -> Optional[Plugin | List[Plugin]]:
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
        found = [
            plugin
            for plugin in self.plugins
            if plugin.name == name and (version is None or plugin.version == version)
        ]
        return found[0] if len(found) == 1 else found or None

    def filter(self, model: Optional[PluginModel]) -> List[Plugin]:
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
