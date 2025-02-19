#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.components.api
=========================

Classes defining API extensions in plugin models and instances.

Classes
-------
APIExtension
    Represents an API extension (function, class) to enrich the host application.
APIExtensionSpec
    Declare an API extension allowed in the host application.

See Also
--------
khimera.plugins.core.Component
    Abstract base class representing a component to a plugin instance.
khimera.plugins.core.FieldSpec
    Abstract base class for defining constraints and validations for components in a plugin model.
"""
from typing import Callable, Optional, Type, Tuple

from khimera.components.core import Component, FieldSpec


class APIExtension(Component):
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


class APIExtensionSpec(FieldSpec[APIExtension]):
    """
    Declare an API extension allowed in the host application.

    Arguments
    ---------
    valid_types : Tuple of Types, optional
        Type(s) of the extension expected by the host application. If a tuple is provided, the
        extension must be an instance of one of the types. If not provided, any type is accepted.
    check_inheritance : bool, default=False
        Determines the type of check to perform relative to the valid type.
        If True, check whether the extension is a subclass of the valid class.
        If False, check whether the extension is an instance of the valid class (useful for
        functions, as instances of `types.FunctionType`).

    Examples
    --------
    Declare an API extension spec for a function:

    >>> from types import FunctionType
    >>> api_extension_spec = APIExtensionSpec(name="test_spec", valid_types=(FunctionType,), check_inheritance=False)
    >>> api_extension_spec.valid_types
    (<class 'types.FunctionType'>,)
    >>> api_extension_spec.validate(APIExtension(name="test_extension", extension=lambda: None))
    True

    Declare an API extension spec for a sub-class of a base class:

    >>> class BaseClass:
    ...     pass
    >>> api_extension_spec = APIExtensionSpec(name="test_spec", valid_types=(BaseClass,), check_inheritance=True)
    >>> api_extension_spec.valid_types
    (<class '__main__.BaseClass'>,)
    >>> class DerivedClass(BaseClass):
    ...    pass
    >>> api_extension_spec.validate(APIExtension(name="test_extension", extension=DerivedClass))
    True

    Notes
    -----
    Because new extensions are not involved in the host application's execution flow, the
    constraints are related to the general structure of the API rather than to strict predefined
    properties of the extensions themselves.

    Usually the `unique` attribute is set to `False` since multiple extensions can be provided for a
    single general field which collects extensions.
    """
    COMPONENT_TYPE = APIExtension

    def __init__(self, name: str,
                 valid_types: Optional[Tuple[Type, ...]] = None,
                 check_inheritance: bool = False,
                 required: bool = False,
                 unique: bool = False,
                 description: Optional[str] = None):
        super().__init__(name=name, required=required, unique=unique, description=description)
        self.valid_types = valid_types
        self.check_inheritance = check_inheritance

    def validate(self, comp: APIExtension) -> bool:
        """Check if the extension is of the expected types or subclasses."""
        if self.valid_types is None:
            return True
        extension = comp.extension
        if self.check_inheritance: # check for inheritance
            return isinstance(extension, type) and issubclass(extension, self.valid_types)
        else: # check for instance of valid type
            return isinstance(extension, self.valid_types)
        return False
