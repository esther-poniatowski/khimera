#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.create
======================

Standardized interface for creating plugins (on the plugin provider side).

Classes
-------
Plugin
    Represents the components provided by a plugin to the host application.

See Also
--------
khimera.core
khimera.plugins.declare
"""
from typing import Optional, Type, Dict, Self

from khimera.utils.factories import TypeConstrainedDict
from khimera.utils.mixins import DeepCopyable, DeepComparable
from khimera.core.components import Component, ComponentSet
from khimera.plugins.declare import PluginModel


class Plugin(DeepCopyable, DeepComparable):
    """
    Represents the components provided by a plugin to the host application.

    Attributes
    ----------
    model : PluginModel
        Plugin model specifying the expected structure and components of the plugin.
    name : str
        Name of the plugin.
    components : Dict[str, ComponentSet]
        Components of the plugin for each field specified in the plugin model.
        Keys: Fields declared in the plugin model.
        Values: Container of component(s) for each field. If the field expects one unique component,
        the container should include only one element.

    Methods
    -------
    add(key: str, comp: Component) -> Self
        Add a component to one of the specified fields in the plugin model.
    remove(key: str, comp_name: Optional[str] = None) -> Self
        Remove a component or all components for a specific key from the plugin.
    get(key: str, names: bool = False) -> ComponentSet
        Get the components of the plugin for a specific field.
    filter(category: Optional[Type[Component]] = None) -> Dict[str, ComponentSet]
        Get the components of the plugin, optionally filtered by category.
    copy() -> Self
        Create a deep copy of the plugin (provided by the `DeepCopyable` mixin).
    __eq__(other: Self) -> bool
        Compare the plugin with another plugin by deep comparison (provided by the `DeepComparable`
        mixin).

    Examples
    --------
    Import a plugin model from the host application:

    >>> from host_app.plugins.models import example_model

    Create a plugin with a name and version metadata for this model:

    >>> plugin = Plugin(model=example_model, name='my_plugin', version='1.0.0')

    Provide a command within a predefined sub-command group of the host application ('commands' field
    key in the model):

    >>> def my_command():
    ...     print("Plugin command executed")
    >>> plugin.add('commands', Command(name='my_cmd', callable=my_command, group='sub-command'))

    Provide a function to extend the host application's API ('api-functions' field key in the model):

    >>> def my_function():
    ...     print("Plugin function executed")
    >>> plugin.add('api-functions', APIExtension(name='my_func', callable=my_function))

    Provide a specific static resource processed by the host application ('input_file' field key in
    the model):

    >>> plugin.add('input_file', Asset(name='my_input', package="my_package", file_path="assets/logo.png"))

    Notes
    -----
    No validation of the components is performed when adding them to the plugin. The components are
    validated against the plugin model by the `PluginValidator` class in the module
    `khimera.plugins.validate`.

    Implications:

    - New fields (keys) can be added to the plugin, regardless of the presence of the corresponding
      field in the model.
    - Multiple components can be added to the same field, regardless of the uniqueness constraints
      set by the corresponding `FieldSpec` in the model.
    - Any type of component can be provided to the plugin, regardless of the expected category of
      the corresponding `FieldSpec` in the model.
    """

    def __init__(self, model: PluginModel, name: str, version: Optional[str] = None, **kwargs):
        self.model = model
        self.name = name
        self.version = version
        self.components = TypeConstrainedDict(str, ComponentSet)  # automatic type checking
        for key, value in kwargs.items():  # add immediate contents of kwargs
            self.add(key=key, comp=value)

    def __str__(self):
        fields_str = ", ".join(f"{key}" for key in self.components)
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}', model={self.model}):[{fields_str}]"

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}', model={self.model})"

    def add(self, key: str, comp: Component) -> Self:
        """
        Add a component to one of the specified fields in the plugin model.

        Arguments
        ---------
        key : str
            Key of the field as defined in the plugin model.
        comp : Component
            Component to add to the plugin.

        Returns
        -------
        Self
            Updated plugin instance, for method chaining.

        Raise
        -----
        TypeError
            If the `comp` argument is not a subclass of `Component`. Automatically raised by the
            `TypeConstrainedList` class when adding the component to the list of components.
        """
        if key not in self.components:  # initialize storage for the field
            self.components[key] = ComponentSet()  # automatic type checking
        if comp.name in self.get(key, names=True):  # check for duplicate component names
            raise AttributeError(f"Duplicate component '{comp.name}' for field '{key}'")
        self.components[key].append(comp)
        comp.attach(self.name)  # keep track of the plugin providing the component
        return self

    def remove(self, key: str, comp_name: Optional[str] = None) -> Self:
        """
        Remove a component or all components for a specific key from the plugin.

        Arguments
        ---------
        key : str
            Key of the field as defined in the plugin model.
        comp_name : str, optional
            Name of the specific component to remove. If not provided, all components for the
            key are removed.

        Returns
        -------
        Self
            Updated plugin instance, for method chaining.

        Raises
        ------
        KeyError
            If the key is not found in the plugin's components.
        ValueError
            If the specified component is not found for the given key.
        """
        if key not in self.components:
            raise KeyError(f"No key '{key}' in the plugin's components")
        if comp_name is None:
            del self.components[key]
        else:
            try:
                comp = next(comp for comp in self.components[key] if comp.name == comp_name)
                self.components[key].remove(comp)
            except (ValueError, KeyError, StopIteration):
                raise KeyError(f"No component '{comp_name}' for key '{key}'")
        return self

    def get(self, key: str, names: bool = False) -> ComponentSet:
        """
        Get the components of the plugin for a specific field.

        Arguments
        ---------
        key : str
            Key of the field in the plugin instance.
        names : bool, optional
            If True, return the names of the components instead of the components themselves.

        Returns
        -------
        ComponentSet
            Components of the plugin stored for the specified field.
        """
        components = self.components.get(key, [])
        if names:
            return [comp.name for comp in components]
        return components

    def filter(self, category: Optional[Type[Component]] = None) -> Dict[str, ComponentSet]:
        """
        Get the components of the plugin, optionally filtered by category.

        Arguments
        ---------
        category : Type[Component]
            Category of the components to filter. If not provided, all components are returned.

        Returns
        -------
        TypeConstrainedDict[str, ComponentSet]
            Components of the plugin, filtered by category if provided.
        """
        if category:
            return {
                key: comps
                for key, comps in self.components.items()
                if any(isinstance(item, category) for item in comps)
            }
        return self.components
