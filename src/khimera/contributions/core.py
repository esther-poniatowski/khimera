#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.core
====================

Core classes and interfaces for defining the components of plugin models and instances.

Classes
-------
Contrib
    Base class representing a contribution to a plugin instance.
ContribList
    List of contributions in a plugin instance.
Spec
    Base class representing constraints and validations for contributions in a plugin model.
CategorySpec
    Variant of `Spec` applying to one or multiple contributions of the same category.
DependencySpec
    Variant of `Spec` enforcing dependencies between several contributions.


Notes
-----
**Contributions and Specifications**

Each specification instance represents constraints and validations that contributions should satisfy
to be accepted by the host application for a specific purpose.

The association between specifications and contributions the specifications occurs at two levels:

1. At the class level, most `Spec` sub-classes reference a companion `Contrib` sub-class via the
   `CONTRIB_TYPE` class attribute (if applicable, except for the `DependencySpec` class which
   can involve contributions from any category).
2. At the instance level (within the plugin creation process), each candidate contribution is added
   in the plugin instance under a key which is the name of one `Spec` instance (see `Plugin` class
   in the `khimera.plugins.create` module).

**Extensibility**

The current system allows the host application to define of custom categories of contributions by
subclassing the `Contrib` and `Spec` classes.

Default `Spec` sub-classes are defined in the `khimera.plugins.variants` module, providing a default
validation logic for the distinct categories of contributions. The current system can be extended
with variant specifications implementing other validation constraints for existing or new
categories, by subclassing the `CategorySpec` class (or the `DependencySpec` class to
specify relational constraints between several plugin components).

See Also
--------
"""
from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar, Generic
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from khimera.plugins.create import Plugin # only imported for type checking

from khimera.utils.factories import TypeConstrainedList


# --- Contributions --------------------------------------------------------------------------------

class Contrib(ABC):
    """
    Base class representing a component in a plugin, conceived as a 'contribution' to the main
    application.

    Attributes
    ----------
    name : str
        Unique name of the contribution in the plugin instance.
    description : str, optional
        Description of the contribution.
    plugin : Plugin, optional
        Plugin instance to which the contribution is attached. Useful during registration and
        retrieval processes.

    Notes
    -----
    For simplicity and consistency, the `MetaData` sub-class is treated as a contribution in the
    plugins, although they are rather used to describe the plugin itself.
    """
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.plugin = None

    @property
    def category(self) -> Type:
        """Category of the contribution."""
        return type(self)

    def attach(self, plugin_name: str) -> None:
        """Attach the contribution to a plugin instance."""
        self.plugin = plugin_name


class ContribList(TypeConstrainedList[Contrib]):
    """List of contributions in a plugin instance."""
    def __init__(self, data=None):
        super().__init__(Contrib, data)


# --- Specifications -------------------------------------------------------------------------------

C = TypeVar('C', bound=Contrib)
"""Type variable for a contribution to a plugin instance."""


class Spec(ABC):
    """
    Base class representing constraints and validations for contributions in a plugin model.

    Attributes
    ----------
    name : str
        Unique name of the Spec in the plugin model.
    description : str, optional
        Description of the Spec.
    category : Type[Contrib]
        (Property) Category of the contribution associated with the specification, if any. If not
        applicable, returns `None`.
    """
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description

    @property
    def category(self) -> Optional[Type[Contrib]]:
        """
        Category of the specification.

        Returns
        -------
        Type[Contrib] or None

        Notes
        -----
        The `category` property is used during filtering and validation processes. For consistency
        across the `Spec` classes, it returns `None` if the `CONTRIB_TYPE` class attribute is not
        set by the subclass. This is the case for the `DependencySpec` class, which can
        involve contributions from any of the plugin's categories.
        """
        return getattr(self, 'CONTRIB_TYPE', None)

    @abstractmethod
    def validate(self, *args, **kwargs) -> bool:
        """
        Validates a candidate contribution against the Spec. To be implemented by subclasses.

        Arguments
        ---------
        args, kwargs
            Contribution instances to validate.

        Returns
        -------
        bool
            Whether the contribution(s) are valid.
        """
        pass


class CategorySpec(Spec, Generic[C]):
    """
    Variant of `Spec` applying to one or multiple contributions of the same category.

    Attributes
    ----------
    required : bool, optional
        Whether at least one contribution is required in the plugin under this name.
    unique : bool, optional
        Whether the contribution must be unique in the plugin.

    Notes
    -----
    For contributions that are involved at precise integration points in the host application's
    execution flow (e.g., hooks), the host application can define strict and precise constraints to
    ensure the plugin's contributions integrate seamlessly with the host application's logics. For
    instance, the host application can require that plugins provide a unique hook, with determined
    inputs and outputs, to be executed at a specific point in the application's workflow.

    For contributions that do not directly intervene in the host application's logics (e.g.,
    commands, API extensions) but are rather used by the client code or the user, the host
    application can define more general constraints that should be respected by all the
    contributions of this category, independently of the specific usage they will have once
    integrated in the host application. For instance, the host application can require that all the
    commands provided by plugins are nested in a specific namespace.
    """
    CONTRIB_TYPE : Type[C]

    def __init__(self, name: str, required : bool = False, unique : bool = False, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.required = required
        self.unique = unique

    @abstractmethod
    def validate(self, contrib: C) -> bool:
        """Validate one contribution against the specification (narrower signature)."""
        pass


class DependencySpec(Spec, Generic[C]):
    """
    Variant of `Spec` enforcing dependencies between several contributions.

    Attributes
    ----------
    dependencies : Dict[str, Type[Contrib]]
        Names of the contributions expected by the host application and their associated types.
    """
    def __init__(self, name: str, description: Optional[str] = None, **dependencies):
        super().__init__(name=name, description=description)
        self.dependencies = dependencies

    @abstractmethod
    def validate(self, plugin: 'Plugin') -> bool:
        """Validate the dependencies globally in the plugin instance."""
        pass
