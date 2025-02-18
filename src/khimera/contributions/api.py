#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.contributions.api
=========================

Classes for defining API extensions in plugin models and instances.

Classes
-------
APIExtension
    Represents an API extension (function, class) to enrich the host application.
APIExtensionSpec
    Declare an API extension allowed in the host application.

See Also
--------
khimera.plugins.core.Contrib
    Abstract base class representing a contribution to a plugin instance.
khimera.plugins.core.CategorySpec
    Abstract base class for defining constraints and validations for contributions in a plugin model.
"""
from typing import Callable, Optional, Type, Tuple

from khimera.contributions.core import Contrib, CategorySpec


class APIExtension(Contrib):
    """
    Represents an API extension (function, class) to enrich the host application.

    Arguments
    ---------
    extension : Callable or Type
        Function or class to extend the host application's API.
    """
    def __init__(self, name: str, extension: Callable | Type, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.extension = extension


class APIExtensionSpec(CategorySpec[APIExtension]):
    """
    Declare an API extension allowed in the host application.

    Arguments
    ---------
    valid_types : Tuple of Types, optional
        Type(s) of the extension expected by the host application. If a tuple is provided, the
        extension must be an instance of one of the types. If not provided, any type is accepted.

    Notes
    -----
    Because new extensions are not involved in the host application's execution flow, the
    constraints are related to the general structure of the API rather than to predefined and strict
    properties of the extensions themselves.

    Usually the `unique` attribute is set to `False` since multiple extensions can be provided, and
    the host application identifies all of them in a general list associated with the spec name.
    """
    CONTRIB_TYPE = APIExtension

    def __init__(self, name: str, valid_types: Optional[Tuple[Type]] = None, required: bool = False, unique: bool = False, description: Optional[str] = None):
        super().__init__(name=name, required=required, unique=unique, description=description)
        self.valid_types = valid_types

    def validate(self, contrib: APIExtension) -> bool:
        """Check if the extension is of the expected types."""
        if self.valid_types is None:
            return True
        return isinstance(contrib.extension, self.valid_types)
