#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.core.components
=======================

Base classes for defining components in plugin models and instances.

Classes
-------
Component
    Base class representing a component to a plugin instance.
ComponentSet
    Container for multiple components associated with a single field in a plugin instance.

See Also
--------
khimera.components
    Module defining specialized components for plugins.
khimera.utils.mixins.DeepCopyable
    Mixin class for creating deep copies of objects.
khimera.utils.mixins.DeepComparable
    Mixin class for comparing objects by deep comparison.
"""
from abc import ABC
from typing import Optional, Type

from khimera.utils.factories import TypeConstrainedList
from khimera.utils.mixins import DeepCopyable, DeepComparable


class Component(ABC, DeepCopyable, DeepComparable):
    """
    Base class representing a component in a plugin, i.e. a unit of functionality or data that is
    supported by the host application.

    Attributes
    ----------
    name : str
        Unique name of the component in the plugin instance.
    description : str, optional
        Description of the component (e.g. purpose, usage).
    plugin : Plugin, optional
        Plugin instance to which the component is attached. This attribute is initially undefined
        and is filled once the component is added to a plugin. It is used to track the origin of
        each component during plugin registration and retrieval.
    category : Type
        (Property) Category of the component (e.g. `MetaData`, `APIExtension`, `Command`, `Hook`,
        `Asset`, or custom categories). It is used to filter and validate components in the plugin.

    Methods
    -------
    attach(plugin_name: str) -> None
        Attach the component to a plugin instance.
    copy() -> Component
        Create a deep copy of the component (provided by the `DeepCopyable` mixin).
    __eq__(other: Component) -> bool
        Compare the component with another component by deep comparison (provided by the
        `DeepComparable` mixin).
    """

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.plugin: Optional[str] = None

    def __str__(self):
        return f"{type(self).__name__}('{self.name}'): {self.description}"

    def __repr__(self):
        return f"{type(self).__name__}('{self.name}')"

    @property
    def category(self) -> Type:
        """Category of the component."""
        return type(self)

    def attach(self, plugin_name: str) -> None:
        """Attach the component to a plugin instance."""
        self.plugin = plugin_name


class ComponentSet(TypeConstrainedList[Component]):
    """Container of components in a plugin instance, behaving like a type constrained list."""

    def __init__(self, data=None):
        super().__init__(Component, data)

    def __str__(self):
        return f"{type(self).__name__}({[str(comp) for comp in self]})"

    def __repr__(self):
        return f"{type(self).__name__}({[repr(comp) for comp in self]})"
