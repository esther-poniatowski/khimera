#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.core
====================

Core classes and interfaces for defining the building blocks of plugin models and instances.

Classes
-------
Component
    Base class representing a component to a plugin instance.
ComponentSet
    Container for multiple components associated with a single field in a plugin instance.
Spec
    Base class representing constraints specifications for plugin components within a plugin model.
FieldSpec
    Specialization of `Spec` defining a field in the plugin that is supported by the host
    application.
DependencySpec
    Specialization of `Spec` enforcing dependencies between several components in the plugin,
    ensuring that structural or functional relationships are maintained.

Notes
-----
**Components and Specifications**

Each specification defines constraints that plugin components should satisfy to be supported by the
host application.

The association between specifications in a model and components in actual plugin instances occurs
at two levels:

1. At the class level, each `FieldSpec` sub-class references a `Component` sub-class on which the
   constraints apply (via the `COMPONENT_TYPE` class attribute).
2. At the plugin instance level (during the plugin creation process), each candidate component is
   stored in the plugin instance under a key corresponding to a `FieldSpec` instance's name in the
   model. This mapping ensures that each component can be validated against the corresponding
   specification in the model and be recognized by the host application.

**Extensibility**

The system provides multiple strategies for defining custom components and extending validation
constraints, ranging from simple type checks to complex structural validations.

Extension Strategies:

1. Using Predefined Component and Specification Types: The `khimera.components` module provides
  built-in components and their associated specification rules (e.g. `MetaData`/`MetaDataSpec`,
  `APIExtension`/`APIExtensionSpec`, `Command`/`MCommandSpec`, `Hook`/`HookSpec`,
  `Asset`/`AssetSpec`). These components include default validation logic tailored to common plugin
  elements.

2. Extending Component and Specification Classes: The base class interfaces allow the host
  application to define new types of constraints that are not covered by the built-in
  specifications:

  - The `FieldSpec` and `Component` classes can be subclassed to implement new component categories
    or to override validation rules for existing ones.
  - The `Spec` class can be subclassed to establish complex relational constraints between
    components that depend on each other to be meaningful in the host application's context.

**Validation Strategies**

By balancing strict integration constraints and general-purpose validations, the system supports a
broad range of plugin architectures, ensuring both flexibility and maintainability.

Specifically, the host application can enforce constraints at varying levels of strictness and
granularity, depending on how components integrate into its execution flow:

- Strict Constraints for Integration Points: Components that interact directly with the host
  application (e.g. hooks, assets) require precise constraints to integrate seamlessly with the host
  application's logics. For instance, the host application may require that each plugin provides a
  single hook with determined inputs and outputs.
- General Constraints for Client-Facing Components: Components used primarily by client code or end
  users (e.g., commands, API extensions) may follow more flexible constraints. For instance, the
  host application may require that all plugin-provided commands reside within a specific namespace.

See Also
--------
khimera.components
    Module defining base and specialized components for plugins.
khimera.components.dependencies
    Module defining dependency specifications for plugin components.
khimera.plugins.declare.PluginModel
    Class defining the structure of a plugin model, including its fields and dependencies.
khimera.plugins.create.Plugin
    Class representing a plugin instance, which is a collection of components that adhere to a
    plugin model.
khimera.utils.mixins.DeepCopyable
    Mixin class for creating deep copies of objects.
khimera.utils.mixins.DeepComparable
    Mixin class for comparing objects by deep comparison.
"""
from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar, Generic

from khimera.utils.factories import TypeConstrainedList
from khimera.utils.mixins import DeepCopyable, DeepComparable


# --- Components --------------------------------------------------------------------------------

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
        self.plugin = None

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


# --- Specifications -------------------------------------------------------------------------------

C = TypeVar('C', bound=Component)
"""Type variable for a component to a plugin instance."""


class Spec(ABC, DeepCopyable, DeepComparable):
    """
    Base class representing constraints specifications for plugin components within a plugin model.

    Attributes
    ----------
    name : str
        Unique name of the Spec in the plugin model.
    description : str, optional
        Description of the Spec.
    category : Type[Component]
        (Property) Category of the component associated with the specification, if any. If not
        applicable, returns `None`.

    Methods
    -------
    validate(*args, **kwargs) -> bool
        Validates a candidate component against the Spec.
    copy() -> Spec
        Create a deep copy of the specification (provided by the `DeepCopyable` mixin).
    __eq__(other: Spec) -> bool
        Compare the specification with another specification by deep comparison (provided by the
        `DeepComparable` mixin).
    """
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description

    def __str__(self):
        return f"{type(self).__name__}('{self.name}'): {self.description}"

    def __repr__(self):
        return f"{type(self).__name__}('{self.name}')"

    @abstractmethod
    def validate(self, *args, **kwargs) -> bool:
        """
        Validates a candidate component against the Spec. To be implemented by subclasses.

        Arguments
        ---------
        args, kwargs
            Component instances to validate.

        Returns
        -------
        bool
            Whether the component(s) are valid.
        """
        pass


class FieldSpec(Spec, Generic[C]):
    """
    Specification of a field in the plugin that is supported by the host application.

    Class Attributes
    ----------------
    COMPONENT_TYPE : Type[Component]
        Type of the component associated with the specification.

    Attributes
    ----------
    required : bool, optional
        Whether at least one component is required in the plugin under this name.
    unique : bool, optional
        Whether the component must be unique in the plugin.
    category : Type[Component]
        (Property) Category of the component associated with the specification.

    Methods
    -------
    validate(comp: C) -> bool
        Validate one component against the specification.
    """
    COMPONENT_TYPE : Type[C]

    def __init__(self, name: str, required : bool = False, unique : bool = False, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.required = required
        self.unique = unique

    def __str__(self):
        return f"{type(self).__name__}('{self.name}'): {self.description}"

    def __repr__(self):
        return f"{type(self).__name__}('{self.name}')"

    @abstractmethod
    def validate(self, comp: C) -> bool:
        """Validate one component against the specification (narrower signature)."""
        pass

    @property
    def category(self) -> Optional[Type[Component]]:
        """
        Category of the specification.

        Returns
        -------
        Type[Component] or None

        Notes
        -----
        The `category` property is used during filtering and validation processes. For consistency
        across the `Spec` classes, it returns `None` if the `COMPONENT_TYPE` class attribute is not
        set by the subclass.
        """
        return getattr(self, 'COMPONENT_TYPE', None)
