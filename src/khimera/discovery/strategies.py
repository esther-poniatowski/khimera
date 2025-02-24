#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.discovery.strategies
============================

Concrete discovery strategies for plugins in the host application.

Classes
-------
StandardEntryPoint
    Discovery strategy based on entry points declared in `pyproject.toml` files.

See Also
--------
khimera.discovery.find
    Base classes for plugin discovery.
"""
import importlib.metadata
from typing import Optional

from khimera.discovery.find import PluginFinder
from khimera.plugins.create import Plugin


# --- Concrete Strategy - StandardEntryPoint -----------------------------------------------


class StandardEntryPoint(PluginFinder):
    """
    Discovers plugins for the host application from entry points declared in `pyproject.toml` of the
    plugin packages.

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
            raise RuntimeError(
                f"Failed to retrieve entry points for {self.entry_point_group}: {exc}"
            )
