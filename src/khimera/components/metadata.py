#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.components.metadata
===========================

Classes defining metadata components in plugin models and instances.

Notes
-----
Metadata is typically used to store additional information about a plugin that is not directly
related to its functionality: configuration parameters (plugin settings), author and repository
information...

Exceptions: name and version are specified outside of metadata, as top-level plugin attributes,
since they are common to all plugins and are used to identify and manage plugins in the host
application.

For simplicity and consistency, metadata it is treated as a special type of 'component', although it
is not an active contribution to the host application. However, this approach is useful to define,
access and validate metadata fields in a plugin model similarly to other components.

Classes
-------
MetaData
    Represents metadata specified in a plugin instance.
MetaDataSpec
    Declare metadata expected by the host application in the plugin model.

See Also
--------
khimera.plugins.core.Component
    Abstract base class representing a component to a plugin instance.
khimera.plugins.core.FieldSpec
    Abstract base class for defining constraints and validations for components in a plugin model.
"""
from typing import Any, Optional

from khimera.components.core import Component, FieldSpec


class MetaData(Component):
    """
    Represents metadata specified in a plugin instance.

    Attributes
    ----------
    value : Any
        Value of the metadata.
    """
    def __init__(self, name: str, value: Any, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.value = value


class MetaDataSpec(FieldSpec[MetaData]):
    """
    Declare metadata expected by the host application in the plugin model.

    Attributes
    ----------
    valid_type : type
        Type of the metadata value expected by the host application.

    Notes
    -----
    Metadata provided in the plugin must exactly match the field (key) and type expected by the host
    application.

    Usually, the `unique` attribute is automatically set to `True` since each metadata admits a
    single value. This can be overridden for metadata fields that accept multiple values by setting
    the `unique` attribute to `False`.
    """
    COMPONENT_TYPE = MetaData

    def __init__(self, name: str, valid_type: type, required: bool = False, unique: bool = True, description: Optional[str] = None):
        super().__init__(name=name, required=required, unique=unique, description=description)
        self.valid_type = valid_type

    def validate(self, contrib: MetaData) -> bool:
        """Check if the metadata value is of the expected type."""
        return isinstance(contrib.value, self.valid_type)
