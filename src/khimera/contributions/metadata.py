#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.contributions.metadata
==============================

Classes for defining metadata components of plugin models and instances.

Classes
-------
MetaData
    Represents metadata associated with a plugin instance.
MetaDataSpec
    Declare metadata expected by the host application.

See Also
--------
khimera.plugins.core.Contrib
    Abstract base class representing a contribution to a plugin instance.
khimera.plugins.core.CategorySpec
    Abstract base class for defining constraints and validations for contributions in a plugin model.
"""
from typing import Any, Optional

from khimera.contributions.core import Contrib, CategorySpec


class MetaData(Contrib):
    """
    Represents metadata associated with a plugin instance.

    Attributes
    ----------
    value : Any
        Value of the metadata.
    """
    def __init__(self, name: str, value: Any, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.value = value


class MetaDataSpec(CategorySpec[MetaData]):
    """
    Declare metadata expected by the host application.

    Attributes
    ----------
    valid_type : type
        Type of the metadata value expected by the host application.

    Notes
    -----
    Metadata provided in the plugin must exactly match the name (key) and type (value) expected by
    the host application.
    Usually, the `unique` attribute is automatically set to `True` since each metadata admits a single
    value. This can be overridden for metadata fields that accept multiple values by setting the
    `unique` attribute to `False`.
    """
    CONTRIB_TYPE = MetaData

    def __init__(self, name: str, valid_type: type, required: bool = False, unique: bool = True, description: Optional[str] = None):
        super().__init__(name=name, required=required, unique=unique, description=description)
        self.valid_type = valid_type

    def validate(self, contrib: MetaData) -> bool:
        """Check if the metadata value is of the expected type."""
        return isinstance(contrib.value, self.valid_type)
