#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.core
====================

Core classes and interfaces for defining the building blocks of plugin models and instances.

Classes
-------
DependencySpec
    Specialization of `Spec` enforcing dependencies between several components in the plugin,
    ensuring that structural or functional relationships are maintained.
PredicateDependency
    Default dependency specification for a single dependent and dependency component.

See Also
--------
khimera.components.core.Spec
    Base class representing constraints specifications for plugin components within a plugin model.
khimera.plugins.create.Plugin
    Class representing a plugin instance, which is a collection of components that adhere to a
    plugin model.
"""
from abc import ABC, abstractmethod
from typing import Optional, Callable, Iterable, TYPE_CHECKING

from khimera.components.core import Spec
if TYPE_CHECKING:
    from khimera.plugins.create import Plugin # only imported for type checking


# --- Base Class for Dependency Specifications -----------------------------------------------------

class DependencySpec(Spec):
    """
    Specification enforcing dependencies between several components in the plugin.

    Attributes
    ----------
    fields : Iterable[str], optional
        Arbitrary number of field names in the model that are involved in the dependency
        relationship.
    """
    def __init__(self, name: str, fields : Iterable[str], description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.fields = tuple(fields)

    def __str__(self):
        return f"{self.__class__.__name__}('{self.name}'):[{', '.join(self.fields if self.fields else [])}]"

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"

    @abstractmethod
    def validate(self, plugin: 'Plugin') -> bool:
        """Validate the dependencies globally in the plugin instance."""
        pass


# --- Default Dependency Specification ------------------------------------------------------------

class PredicateDependency(DependencySpec) :
    """
    Default dependency specification for a single dependent and dependency component.

    Attributes
    ----------
    predicate : Callable[..., bool], optional
        Validation rule, that admits any number of `ComponentSet` (named by their fields) and
        returns a boolean indicating whether the dependencies are satisfied.
    fields : Tuple[str], optional
        Arbitrary number of field names in the model that contain dependent and dependency
        components.

    Examples
    --------
    Define a predicate that checks that is a hook is provided, it is paired with an asset (assuming
    a unique component in both fields):

    >>> def hook_asset_dependency(hook: ComponentSet[Hook], asset: ComponentSet[Asset]) -> bool:
    ...     return bool(hook) == bool(asset)

    Define the dependency specification:

    >>> hook_asset_spec = PredicateDependency(name="hook_asset", predicate=hook_asset_dependency, fields=("hook", "asset"))

    Warning
    -------
    The predicate function should handle the case where the fields admit multiple components. For
    instance, it could iterate over the components in several fields in parallel and check the
    dependencies for each combination.
    """
    def __init__(self, name: str, predicate: Callable[..., bool], fields : Iterable[str], description: Optional[str] = None):
        super().__init__(name=name, fields=fields, description=description)
        self.predicate = predicate

    def validate(self, plugin: 'Plugin') -> bool:
        """Validate the dependencies globally in the plugin instance."""
        components = {field: plugin.components.get(field) for field in self.fields}
        if None in components.values():
            return False
        return self.predicate(**components)
