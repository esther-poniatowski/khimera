#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.variants
========================

Classes and interfaces for defining the components of plugin models and instances.

Classes
-------
MetaData
    Represents metadata associated with a plugin instance.
MetaDataSpec
    Declare metadata expected by the host application.
Hook
    Represents a hook to be executed by the host application.
HookSpec
    Declare a hook expected by the host application.
Command
    Represents a command in the host application's CLI.
CommandSpec
    Declare the constraints that the commands of the plugins must satisfy to be accepted by the host
    application's CLI.
APIExtension
    Represents an API extension (function, class) to enrich the host application.
APIExtensionSpec
    Declare an API extension allowed in the host application.
Asset
    Represents a static resource expected by the host application.
AssetSpec
    Declare an asset expected by the host application.

See Also
--------
"""
from pathlib import Path
from typing import Any, Callable, Optional, Type, Union, Set, Tuple

from khimera.plugins.core import Contrib, CategorySpec


# --- Metadata -------------------------------------------------------------------------------------

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


# --- Hooks ----------------------------------------------------------------------------------------

class Hook(Contrib):
    """
    Represents a hook to be executed by the host application.

    Attributes
    ----------
    callable : Callable
        Function or method to be executed when the hook is triggered.
    """
    def __init__(self, name: str, callable: Callable, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.callable = callable


class HookSpec(CategorySpec[Hook]):
    """
    Declare a hook expected by the host application.

    Attributes
    ----------
    input_types : type or tuple of types
        Type or types of the arguments expected by the hook.
    output_type : type
        Type of the return value expected by the hook.

    Notes
    -----
    Hooks provided in the plugin must exactly match input types and output type expected by the host
    application.

    Usually the `unique` attribute is set to `True` since each hook (associated with the spec name)
    admits a single callable.
    """
    CONTRIB_TYPE = Hook

    def __init__(self, name: str, input_types, output_type, required: bool = False, unique : bool = True, description: Optional[str] = None):
        super().__init__(name=name, required=required, unique=unique, description=description)
        self.input_types = input_types
        self.output_type = output_type

    def validate(self, contrib: Hook) -> bool:
        """Check if the hook signature matches the expected input and output types."""
        valid_inputs = all(isinstance(arg, self.input_types) for arg in contrib.callable.__code__.co_varnames)
        valid_output = isinstance(contrib.callable(), self.output_type)
        return valid_inputs and valid_output


# --- Commands -------------------------------------------------------------------------------------

class Command(Contrib):
    """
    Represents a command in the host application's CLI, optionally nested in a predefined
    sub-command group.

    Attributes
    ----------
    callable : Callable
        Function or method to be executed when the command is invoked.
    group : str, optional
        Name of the sub-command group where the command will be nested.
        If not provided, the command will be a top-level command, if allowed by the host
        application.
        If the group names does not match any predefined group in the host application, a new group
        will be created, if allowed by the host application.
    """
    def __init__(self, name: str, callable: Callable, group: Optional[str] = None, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.callable = callable
        self.group = group


class CommandSpec(CategorySpec[Command]):
    """
    Declare the constraints that the commands of the plugins must satisfy to be accepted by the host
    application's CLI.

    Attributes
    ----------
    groups : Set[str], optional
        Allowed sub-command groups where new commands can be nested.
    admits_new_groups : bool, default=True
        Whether the plugin can add new sub-command groups.
    admits_top_level : bool, default=True
        Whether the plugin can add top-level commands.

    Notes
    -----
    Because new commands are not involved in the host application's execution flow, the constraints
    are related to the general CLI structure rather than to predefined and strict properties of the
    commands themselves.
    Usually the `unique` attribute is set to `False` since multiple commands can be nested in the
    same group, and the host application identifies all of them in a general list associated with
    the spec name.
    """
    CONTRIB_TYPE = Command

    def __init__(self, name: str,
                 groups: Optional[Set[str]] = None,
                 admits_new_groups: bool = True,
                 admits_top_level: bool = True,
                 required: bool = False,
                 unique: bool = False,
                 description: Optional[str] = None,
    ):
        super().__init__(name=name, required=required, unique=unique, description=description)
        # Configure CLI
        self.groups = groups or set()
        self.admits_new_groups = admits_new_groups
        self.admits_top_level = admits_top_level

    def validate(self, contrib: Command) -> bool:
        """Check if the command group is allowed by the host application."""
        if contrib.group is None and not self.admits_top_level:
            return False
        if contrib.group not in self.groups and not self.admits_new_groups:
            return False
        return True


# --- API Extensions -------------------------------------------------------------------------------

class APIExtension(Contrib):
    """
    Represents an API extension (function, class) to enrich the host application.

    Arguments
    ---------
    extension : Callable or Type
        Function or class to extend the host application's API.
    """
    def __init__(self, name: str, extension: Union[Callable, Type], description: Optional[str] = None):
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
        return isinstance(contrib, self.valid_types)


# --- Assets ---------------------------------------------------------------------------------------

class Asset(Contrib):
    """
    Represents a static resource expected by the host application.

    Arguments
    ---------
    path : str or Path
        Path to the resource file, relative to the plugin's directory.
    """
    def __init__(self, name: str, path: str | Path, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.path = path

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
