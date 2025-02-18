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
from typing import Optional, Type, Dict

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

    >>> model.declare(MetaDataSpec(name='author', required=True, description="Author of the plugin"))

    Allow integrating new commands in the host application's CLI, in sub-command groups:

    >>> model.declare(CommandSpec(name='commands',
    ...                           required=False,
    ...                           unique=False,
    ...                           groups={'setup', 'run'},
    ...                           admits_new_groups=True,
    ...                           description="New commands for the CLI"))

    Allow extending the host application with new API functions:

    >>> model.declare(APIExtensionSpec(name='api-functions',
    ...                                required=False,
    ...                                unique=False,
    ...                                description="New functions for the API"))

    Declare a named hook to use at a specific integration point in the host application:

    >>> model.declare(HookSpec(name='on_start', required=False, unique=True, description="Hook to run on application start"))

    Declare a static resource processed by the host application:

    >>> model.declare(AssetSpec(name='input_file',
    ...                          file_ext={'txt', 'csv'},
    ...                          required=False,
    ...                          unique=True,
    ...                          description="File to process"))

    Get all the metadata specifications in the plugin model:

    >>> model.get(category=MetaData)
    {'author': MetaDataSpec(name='author', required=True, description="Author of the plugin")}

    Notes
    -----
    Dependency specs are treated separately from category specs (two distinct attributes) since they
    do not share the same properties and constraints. However, they can be declared via the same
    `declare` method and retrieved via the same `get` method.
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

    def declare(self, spec: Spec):
        """Declares a `Spec` in the plugin model."""
        if spec.name in self.all_specs:
            raise AttributeError(f"Spec '{spec.name}' already declared in the plugin model")
        if isinstance(spec, CategorySpec):
            self.specs[spec.name] = spec
        elif isinstance(spec, DependencySpec):
            self.dependencies[spec.name] = spec
        else:
            raise TypeError(f"Unsupported spec type: '{type(spec)}' (must be a subclass of 'Spec')")

    def get(self, name: str) -> Spec:
        """Get a `Spec` from the plugin model by name."""
        return self.all_specs[name]

    def filter(self, category: Optional[Type[Contrib]] = None, unique: bool = False, required: bool = False) -> Dict[str, CategorySpec]:
        """
        Filter the specs in the plugin model by category, uniqueness or requiredness constraints.

        Arguments
        ---------
        category : Type[Contrib], optional
            Category of the specs to retain. If not provided, all specs are kept.
        unique : bool, optional
            Whether target specs must admit a unique contribution in the plugin.
        required : bool, optional
            Whether target specs are required in the plugin.

        Notes
        -----
        Dependency specs are not considered since they do not share the same filtering properties as
        category specs.
        """
        specs = {name: spec for name, spec in self.specs.items()} # copy all by default
        if category:
            specs = {name: spec for name, spec in specs.items() if spec.category == category}
        if unique:
            specs = {name: spec for name, spec in specs.items() if spec.unique}
        if required:
            specs = {name: spec for name, spec in specs.items() if spec.required}
        return specs
