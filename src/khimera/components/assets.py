#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.components.
========================

Classes defining static resources (assets) in plugin models and instances.

Classes
-------
Asset
    Represents a static resource to provide to the host application.
AssetSpec
    Declare an asset expected by the host application.

See Also
--------
khimera.plugins.core.Component
    Abstract base class representing a component to a plugin instance.
khimera.plugins.core.FieldSpec
    Abstract base class for defining constraints and validations for components in a plugin
    model.
pathlib.Path
    Object-oriented filesystem paths.
"""
from importlib.resources import files, as_file
from pathlib import Path
from typing import Optional, Tuple
from types import ModuleType

from khimera.components.core import Component, FieldSpec


class Asset(Component):
    """
    Represents a static resource to provide to the host application.

    Arguments
    ---------
    package : str | ModuleType, optional
        Name of the package where the resource is located. It can be either a string representing a
        package name or a module object (e.g., `__name__`).

        Common scenarios:

        - If resources are directly in the package root, use the package name as specified in
          `pyproject.toml` (e.g.  `"my_package"`).
        - If resources are in a subdirectory, use dot notation to specify the subdirectory (e.g.
          `"my_package.resources"`).

        If not provided, the package is inferred from the caller's module, i.e. the module where the
        `Asset` instance is created (`__module__` attribute), which is assumed to be the file where
        the plugin is defined.

    file_path : str
        Path to the resource file, relative to the package root.

    Notes
    -----
    Resources cannot be loaded directly by resolving their absolute path on the client's filesystem.
    Indeed, during the installation of the plugin, the storage of the package resources depend on
    the packaging tool used (e.g., `setuptools`). The `importlib.resources` module provides a way to
    access the resources in a platform-independent way.

    Examples
    --------
    Consider the following directory structure for the plugin package:

    .. code-block:: none

        my_package/
        ├── __init__.py
        ├── assets/
        │   └── logo.png
        └── plugin.py


    In the plugin specification, add a component for the `logo.png` file in the `assets`
    directory:

    >>> asset = Asset(name="logo", package="my_package", file_path="assets/logo.png")

    In the host application, access the resource file:

    >>> with asset.get_path() as path:
    ...     print(path)
    ...     # Use the path to access the resource file

    See Also
    --------
    importlib.resources
    """
    def __init__(self, name: str, file_path : Optional[str], package : Optional[str | ModuleType] = None, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.file_path = file_path
        self.package = package or self.__module__ # default to the caller's module

    def get_path(self) -> Path:
        """
        Create a context manager to access the resource file. When used in a `with` statement, it
        provides a `pathlib.Path` object representing the resource.

        Returns
        -------
        Path
            Path to the resource file.

        Notes
        -----
        This implementation ensures that :

        - If the resource is already on the file system, it is accessed directly.
        - If the resource is not on the file system (e.g., in a zip file), it is extracted to a
          temporary location, and the context manager cleans up any temporary files or directories
          after the resource was extracted.
        """
        return as_file(files(self.package).joinpath(self.file_path))


class AssetSpec(FieldSpec[Asset]):
    """
    Declare an asset expected by the host application.

    Arguments
    ---------
    file_ext : Tuple of str, optional
        Allowed file extensions for the asset, corresponding to file formats that are supported by
        the host application. If not provided, any extension is accepted.

    Notes
    -----
    By default, assets are not required but they are unique, implying that the host application
    expects a single asset per name.
    """
    COMPONENT_TYPE = Asset

    def __init__(self, name: str, file_ext: Optional[Tuple[str]] = None, required: bool = False, unique: bool = True, description: Optional[str] = None):
        super().__init__(name=name, required=required, unique=unique, description=description)
        self.file_ext = file_ext

    def validate(self, comp: Asset) -> bool:
        """Check if the asset file extension is allowed."""
        if self.file_ext is None:
            return True
        return comp.file_path.endswith(self.file_ext)
