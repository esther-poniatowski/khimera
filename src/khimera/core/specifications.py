#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.core.specifications
===========================

Base classes representing constraints specifications for components within a plugin model.

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

See Also
--------
khimera.components
    Module defining base and specialized components for plugins.
khimera.core.dependencies
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

from khimera.utils.mixins import DeepCopyable, DeepComparable
from khimera.core.components import Component

# --- Specifications -------------------------------------------------------------------------------

C = TypeVar("C", bound=Component)
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

    COMPONENT_TYPE: Type[C]

    def __init__(
        self,
        name: str,
        required: bool = False,
        unique: bool = False,
        description: Optional[str] = None,
    ):
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
        return getattr(self, "COMPONENT_TYPE", None)
