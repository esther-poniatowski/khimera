"""
khimera.discovery.strategies
============================

Concrete discovery strategies for plugins in the host application.

Classes
-------
FromInstalledFinder
    Discovery strategy based on entry points declared in `pyproject.toml` files.

See Also
--------
khimera.discovery.find
    Base classes for plugin discovery.
"""
import importlib.metadata
from typing import Optional

from khimera.discovery.find import PluginFinder, PluginEntryPoint
from khimera.plugins.create import Plugin


# --- FromInstalledFinder --------------------------------------------------------------------------


class FromInstalledFinder(PluginFinder):
    """
    Discovers plugins for the host application from entry points declared in `pyproject.toml` of the
    installed packages.

    Typically, this strategy is triggered automatically by the host application itself in its
    `__init__.py` file or by a CLI command that initializes the application.

    Attributes
    ----------
    app_name : str
        Name of the application requiring plugin discovery.
    entry_point_group : str, default='{app_name}.plugins'
        Entry point group where external packages declare their entry points to plugins for the host
        application.

    Examples
    --------
    On the plugin provider side, entry points for the host application are declared in the
    `pyproject.toml` file of the provider's package:

    .. code-block:: toml

        [project.entry-points.'host_name.plugins']
        plugin1 = "my_package.plugins:Plugin1"
        plugin2 = "my_package.plugins:Plugin2"

    On the host application side, external plugins can be discovered by triggering the
    `FromInstalledFinder` in the host application's `__init__.py` file (to ensure plugins are
    discovered at import time):

    .. code-block:: python

        from khimera.discovery.strategies import FromInstalledFinder

        finder = FromInstalledFinder(app_name="host_name")
        finder.discover()

    Notes
    -----
    The discovery mechanism does not differentiate between 'internal' plugins (packaged with the
    host application) and 'external' plugins (installed as third-party packages), as long as the
    host application itself defines its own plugins entry points in its `pyproject.toml` file. All
    plugins are treated similarly as entry points regardless of their sources by the `importlib`
    library since their metadata is registered during the packages' installation in the user's
    environment.
    """

    def __init__(
        self,
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
            plugin = entry_point.load()  # expected: `Plugin` instance
            if not isinstance(plugin, Plugin):
                raise TypeError(
                    f"Invalid plugin loaded from entry point {entry_point.name}. "
                    "Expected `Plugin` instance."
                )
            self.store(plugin)

    def get_entry_points(self):
        """
        Finds all installed plugins that declare entry points for the host application.

        Returns
        -------
        List[importlib.metadata.EntryPoint]
            Entry points for the host application.

        Raises
        ------
        RuntimeError
            If entry points retrial fails.
        """
        try:
            return importlib.metadata.entry_points(group=self.entry_point_group)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to retrieve entry points for {self.entry_point_group}: {exc}"
            ) from exc


# --- FromAPIFinder --------------------------------------------------------------------------------


class FromAPIFinder(PluginFinder):
    """
    Discovers plugins for the host application specified at import time by the user through the API.

    Typically, this strategy is triggered by the user in a `main.py` file which imports the host
    application, when the user develops plugins locally.

    Attributes
    ----------
    entry_points : List[PluginEntryPoint]
        Entry points for the plugins specified by the user.

    Examples
    --------
    Any user can develop plugins for the host application, for instance in distinct modules stored
    in a specific directory of the  user's project:

    .. code-block:: plaintext

        .
        ├── main.py
        └── plugins/
            ├── __init__.py
            ├── plugin1.py
            └── plugin2.py

    In the `main.py` file, the user can import the host application (if it is installed in the
    user's environment) and specify the plugins entry points that should be discovered:

    .. code-block:: python

        import host_name
        from khimera.discovery.strategies import FromAPIFinder
        from plugins.plugin1 import Plugin1
        from plugins.plugin2 import Plugin2

    """

    def __init__(self, *args: PluginEntryPoint):
        super().__init__()
        self.entry_points = list(args)

    def discover(self):
        """
        Discovers plugins specified by the user through the API.

        Raises
        ------
        TypeError
            If a plugin loaded from the API is not an instance of `Plugin`.
        """
        raise NotImplementedError("API-based plugin discovery is not yet implemented.")
