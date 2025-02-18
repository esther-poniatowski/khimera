#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.create
======================

Standardized interface for creating plugins, on the plugin provider side.

Classes
-------
Plugin
    Represents the contributions of a plugin.
Contributions
    Type for a list of contributions of a plugin.

See Also
--------
khimera.plugins.core
khimera.plugins.declare
"""
from typing import Optional, Type, Dict, Self
import copy

from khimera.utils.factories import TypeConstrainedDict, TypeConstrainedList
from khimera.contributions.core import Contrib, ContribList
from khimera.plugins.declare import PluginModel


class Plugin:
    """
    Represents the contributions of a plugin.

    Attributes
    ----------
    model : PluginModel
        Plugin model specifying the expected structure and contributions of the plugin.
    name : str
        Name of the plugin.
    contributions : Dict[str, ContribList]
        Contributions of the plugin for each specification field in the plugin model.
        Keys: Names of the specification fields declared in the plugin model.
        Values: Contribution(s) for each field. If the specification sets expects one unique
        contribution, the list should contain only one element.

    Examples
    --------
    Import a plugin model from the host application:

    >>> from host_app.plugins.models import example_model

    Create a plugin with a name and version metadata for this model:

    >>> plugin = Plugin(model=example_model, name='my_plugin', version='1.0.0')

    Provide a command within a predefined sub-command group of the host application ('commands' spec
    key in the model):

    >>> def my_command():
    ...     print("Plugin command executed")
    >>> plugin.add('commands', Command(name='my_cmd', callable=my_command, group='sub-command'))

    Provide a function to extend the host application's API ('api-functions' spec key in the model):

    >>> def my_function():
    ...     print("Plugin function executed")
    >>> plugin.add('api-functions', APIExtension(name='my_func', callable=my_function))

    Provide a specific static resource processed by the host application ('input_file' spec key in
    the model):

    >>> plugin.add('input_file', Asset(name='my_input', package="my_package", file_path="assets/logo.png"))

    Notes
    -----
    No validation of the contributions is performed when adding contributions to the plugin. The
    contributions are validated against the plugin model by the `PluginValidator` class in the
    module `khimera.plugins.validate`.

    Implications:

    - Any field (key) can be added to the plugin, regardless of the presence of the corresponding
      spec in the model.
    - Multiple contributions can be added to the same field, regardless of the uniqueness
      constraints set by the corresponding spec in the model.
    - Any type of contribution can be provided to the plugin, regardless of the expected category of
      the corresponding spec in the model.
    """
    def __init__(self,
                model : PluginModel,
                name: str,
                version: Optional[str] = None,
                **kwargs
                ):
        self.model = model
        self.name = name
        self.version = version
        self.contributions = TypeConstrainedDict(str, ContribList) # automatic type checking
        for key, value in kwargs.items(): # add immediate contents of kwargs
            self.add(key=key, contrib=value)

    def __str__(self):
        """Print name and metadata of the plugin."""
        return f"Plugin(name={self.name}, version={self.version}, model={self.model})"

    def add(self, key: str, contrib: Contrib) -> None:
        """
        Add a contribution to one of the specified fields in the plugin model.

        Arguments
        ---------
        key : str
            Key of the specification field in the plugin model.
        contrib : Contrib
            Contribution to add to the plugin.

        Raise
        -----
        TypeError
            If the `contrib` argument is not a subclass of `Contrib`. Automatically raised by the
            `TypeConstrainedList` class when adding the contribution to the list of contributions.
        """
        if key not in self.contributions: # initialize storage for the field
            self.contributions[key] = TypeConstrainedList(Contrib) # automatic type checking
        contrib.attach(self.name) # keep track of the plugin providing the contribution
        self.contributions[key].append(contrib)

    def get(self, key: str) -> ContribList:
        """
        Get the contributions of the plugin for a specific field.

        Arguments
        ---------
        key : str
            Key of the field in the plugin model.

        Returns
        -------
        ContribList
            Contributions of the plugin stored for the specified field.
        """
        return self.contributions.get(key, [])

    def filter(self, category: Optional[Type[Contrib]] = None) -> Dict[str, ContribList]:
        """
        Get the contributions of the plugin, optionally filtered by category.

        Arguments
        ---------
        category : Type[Contrib]
            Category of the contributions to filter. If not provided, all contributions are
            returned.

        Returns
        -------
        TypeConstrainedDict[str, ContribList]
            Contributions of the plugin, filtered by category if provided.
        """
        if category:
            return {key: contribs for key, contribs in self.contributions.items() if any(isinstance(item, category) for item in contribs)}
        return self.contributions

    def copy(self) -> Self:
        """
        Create a deep copy of the plugin, creating copies of all its nested contributions.

        Returns
        -------
        Plugin
            Copy of the plugin instance.

        See Also
        --------
        copy.deepcopy
        """
        return copy.deepcopy(self)
