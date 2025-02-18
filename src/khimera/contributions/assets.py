#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.contributions.
========================

Classes for defining static resources (assets) in plugin models and instances.

Classes
-------
Asset
    Represents a static resource to provide to the host application.
AssetSpec
    Declare an asset expected by the host application.

See Also
--------
khimera.plugins.core.Contrib
    Abstract base class representing a contribution to a plugin instance.
khimera.plugins.core.CategorySpec
    Abstract base class for defining constraints and validations for contributions in a plugin model.
"""
from pathlib import Path
from typing import Optional, Tuple

from khimera.contributions.core import Contrib, CategorySpec


class Asset(Contrib):
    """
    Represents a static resource to provide to the host application.

    Arguments
    ---------
    path : str or Path
        Path to the resource file, relative to the plugin's directory.

    Notes
    -----

    """
    def __init__(self, name: str, path: str | Path, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.path = path

    def get_path(self) -> Path:
        """Get the absolute path to the resource file in the actual filesystem."""
        return Path(self.path)


class AssetSpec(CategorySpec[Asset]):
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
    CONTRIB_TYPE = Asset

    def __init__(self, name: str, file_ext: Optional[Tuple[str]] = None, required: bool = False, unique: bool = True, description: Optional[str] = None):
        super().__init__(name=name, required=required, unique=unique, description=description)
        self.file_ext = file_ext

    def validate(self, contrib: Asset) -> bool:
        """Check if the asset file extension is allowed."""
        if self.file_ext is None:
            return True
        return contrib.path.suffix in self.file_ext
