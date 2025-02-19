#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.declare
=======================

Standardized interface for declaring plugin models, on the host application side.

Classes
-------
PluginModel
    Represents the expected structure and contributions of a plugin.

See Also
--------
"""
from typing import Optional, Type, Dict, Callable, Self

from khimera.utils.factories import TypeConstrainedDict
from khimera.contributions.core import Spec, Contrib, DependencySpec, CategorySpec


class PluginModel:
    """
    Represents a plugin model specifying the expected structure and contributions of a plugin.

    Attributes
    ----------
    name : str
        Name of the model.
    version : str, optional
        Version of the model.
    specs : Dict[str, CategorySpec]
        Specifications for single or multiple contributions of the same category in the plugin
        model.
    dependencies : Dict[str, DependencySpec]
        Specifications enforcing dependencies between several contributions in the plugin model.

    Examples
    --------
    Create a plugin model with a name and version:

    >>> model = PluginModel(name='my_plugin', version='1.0.0')

    Declare a metadata field in the plugin model:

    >>> model.add(MetaDataSpec(name='author', required=True, description="Author of the plugin"))

    Allow integrating new commands in the host application's CLI, in sub-command groups:

    >>> model.add(CommandSpec(name='commands',
    ...                           required=False,
    ...                           unique=False,
    ...                           groups={'setup', 'run'},
    ...                           admits_new_groups=True,
    ...                           description="New commands for the CLI"))

    Allow extending the host application with new API functions:

    >>> model.add(APIExtensionSpec(name='api-functions',
    ...                                required=False,
    ...                                unique=False,
    ...                                description="New functions for the API"))

    Declare a named hook to use at a specific integration point in the host application:

    >>> model.add(HookSpec(name='on_start', required=False, unique=True, description="Hook to run on application start"))

    Declare a static resource processed by the host application:

    >>> model.add(AssetSpec(name='input_file',
    ...                          file_ext={'txt', 'csv'},
    ...                          required=False,
    ...                          unique=True,
    ...                          description="File to process"))

    Get all the metadata specifications in the plugin model:

    >>> model.get(category=MetaData)
    {'author': MetaDataSpec(name='author', required=True, description="Author of the plugin")}

    Notes
    -----
    Modular plugin models can be created using the `add` and `remove` methods to compose
    specifications with dynamic overrides.

    Implementation
    --------------
    Dependency specs are treated separately from category specs (two distinct attributes) since they
    do not share the same properties and constraints. However, they can be declared via the same
    `add` method and retrieved via the same `get` method.
    """
    def __init__(self, name: str, version: Optional[str] = None):
        # Initialize model's metadata
        self.name = name
        self.version = version
        # Initialize model's specifications
        self.specs = TypeConstrainedDict(str, CategorySpec)
        self.dependencies = TypeConstrainedDict(str, DependencySpec)

    @property
    def all_specs(self) -> Dict[str, Spec]:
        """All specifications in the plugin model (combined category and dependency specs)."""
        return {**self.specs, **self.dependencies}

    def add(self, spec: Spec) -> Self:
        """
        Declares a `Spec` in the plugin model.

        Arguments
        ---------
        spec : Spec
            Specification to declare in the plugin model. The name is used as the key in the model.

        Returns
        -------
        Self
            Updated plugin model instance, for method chaining.

        Raises
        ------
        TypeError
            If the spec is not a subclass of `Spec` supported by the plugin model (either
            `CategorySpec` or `DependencySpec`).
        KeyError
            If a spec with the same name is already declared in the plugin model
            (category and dependency specs are unique by name).
        """
        if not isinstance(spec, (CategorySpec, DependencySpec)): # before accessing `name` attribute
            raise TypeError(f"Unsupported spec type: '{type(spec)}' (must be a subclass of 'Spec': either 'CategorySpec' or 'DependencySpec')")
        if spec.name in self.all_specs:
            raise KeyError(f"Spec '{spec.name}' already declared in the plugin model")
        if isinstance(spec, CategorySpec):
            self.specs[spec.name] = spec
        else: # isinstance(spec, DependencySpec)
            self.dependencies[spec.name] = spec
        return self

    def remove(self, name: str) -> Self:
        """
        Remove a spec from the plugin model by name.

        Arguments
        ---------
        name : str
            Name of the spec to remove from the plugin model.

        Returns
        -------
        Self
            Updated plugin model instance, for method chaining.

        Raises
        ------
        KeyError
            If the spec with the given name is not found in the plugin model.
        """
        if name in self.specs:
            del self.specs[name]
        elif name in self.dependencies:
            del self.dependencies[name]
        else:
            raise KeyError(f"Spec '{name}' not found in the plugin model")
        return self

    def get(self, name: str) -> Spec | None:
        """Get a `Spec` from the plugin model by name. None if not present in the model."""
        return self.all_specs.get(name)

    def filter(self,
               category: Optional[Type[Contrib]] = None,
               unique: Optional[bool] = None,
               required: Optional[bool] = None,
               custom_filter: Optional[Callable[[CategorySpec], bool]] = None
              ) -> Dict[str, CategorySpec]:
        """
        Filter the specs in the plugin model based on various criteria.

        Arguments
        ---------
        category : Type[Contrib], optional
            Category of the specs to retain. If not provided, all categories are considered.
        unique : bool, optional
            If True, retain only specs that admit a unique contribution.
            If False, retain only specs that admit multiple contributions.
            If None (default), this criterion is not applied.
        required : bool, optional
            If True, retain only required specs.
            If False, retain only optional specs.
            If None (default), this criterion is not applied.
        custom_filter : Callable[[CategorySpec], bool], optional
            Custom function for more complex filtering logic.
            It should take a CategorySpec and returns a boolean.

        Returns
        -------
        Dict[str, CategorySpec]
            Specs that meet all the specified criteria.

        Examples
        --------
        Filter with a custom function:

        >>> def custom_filter(spec: CategorySpec) -> bool:
        ...     return spec.name.startswith('test_')
        >>> model.filter(custom_filter=custom_filter)

        Notes
        -----
        Dependency specs are not considered since they do not share the same
        filtering properties as category specs.
        """
        def meets_criteria(spec: CategorySpec) -> bool:
            return (
                (category is None or spec.CONTRIB_TYPE == category) and
                (unique is None or spec.unique == unique) and
                (required is None or spec.required == required) and
                (custom_filter is None or custom_filter(spec))
            )

        return {name: spec for name, spec in self.specs.items() if meets_criteria(spec)}
