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

See Also
--------
khimera.plugins.core
khimera.plugins.declare
"""
from typing import List, Optional, Type, Union, overload

from khimera.utils.factories import TypeConstrainedDict
from khimera.plugins.core import Contrib
from khimera.plugins.variants import MetaData
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
    metadata : Dict[str, MetaData]
        Metadata associated with the plugin.
    contributions : Dict[str, List[Contrib]]
        Contributions of the plugin for each specification field in the plugin model.
        Keys: Names of the specification fields declared in the plugin model.
        Values: Contribution(s) for each field. If the specification sets expects one unique
        contribution, the list should contain only one element.
    specific_storages : Dict[Type[Contrib], str]
        Mapping between specific sub-categories of contributions that should be stored in separate
        dictionaries in the plugin instance, and the corresponding attribute in the plugin.
        By default, `MetaData` contributions are stored in the 'metadata' attribute while all other
        types of contributions are stored in the 'contributions' attribute.
    default_storage : str, default='contributions'
        Default attribute in the plugin instance where contributions are stored.

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

    >>> plugin.add('input_file', Asset(name='my_input', path='path/to/input/file'))

    Notes
    -----
    The internal structure of the plugin separates metadata from other contributions, to provide a
    more straightforward access to the metadata for filtering and indexing purposes. Model, name and
    version information is not stored in the metadata dictionary but as separate attributes, since
    they are excepted in plugins while metadata is optional.
    """
    SPECIFIC_STORAGES : TypeConstrainedDict[Type[Contrib], str] = {MetaData: 'metadata'}
    DEFAULT_STORAGE = 'contributions'

    def __init__(self,
                model : PluginModel,
                name: str,
                version: Optional[str] = None,
                specific_storages: TypeConstrainedDict[Type[Contrib], str] = SPECIFIC_STORAGES,
                default_storage: str = DEFAULT_STORAGE,
                **kwargs
                ):
        self.model = model
        self.name = name
        self.version = version
        self.specific_storages = specific_storages
        self.default_storage = default_storage
        # Initialize storage dictionaries
        setattr(self, self.default_storage, TypeConstrainedDict(str, List[Contrib]))
        for attr in self.specific_storages.values():
            setattr(self, attr, TypeConstrainedDict(str, List[Contrib]))
        # Automatically add contents of kwargs
        for key, value in kwargs.items():
            self.add(key=key, contrib=value)

    def __str__(self):
        """Print name and metadata of the plugin."""
        return f"Plugin(name={self.name}, version={self.version}, model={self.model})"

    @overload
    def get_storage(self, contrib: Contrib | Type[Contrib], name=False) -> TypeConstrainedDict[str, List[Contrib]]:
        pass

    @overload
    def get_storage(self, contrib: Contrib | Type[Contrib], name=True) -> str:
        pass

    def get_storage(self, contrib: Contrib | Type[Contrib], name=False) -> TypeConstrainedDict[str, List[Contrib]] | str:
        """
        Get the attribute in the plugin instance where a contribution should be stored.

        Arguments
        ---------
        contrib : Contrib or Type[Contrib]
            Contribution to store, or its type.
        name : bool, default=False
            Whether to return the name of the attribute instead of the attribute itself.

        Returns
        -------
        TypeConstrainedDict[str, List[Contrib]] or str
            If `name` is False, attribute in the plugin instance where the contribution should be
            stored.
            If `name` is True, name of this attribute.
        """
        type_contrib = contrib if isinstance(contrib, type) else type(contrib)
        name = self.specific_storages.get(type_contrib, self.default_storage)
        if name:
            return name
        return getattr(self, name)

    def add(self, key: str, contrib: Contrib) -> None:
        """
        Add a contribution to one of the specification fields in the plugin model.

        Arguments
        ---------
        key : str
            Key of the specification field in the plugin model.
        contrib : Contrib
            Contribution to add to the plugin.

        Raises
        ------
        KeyError
            If the key does not correspond to any specification declared in the plugin model.
        """
        if key not in self.model.specs:
            raise KeyError(f"Spec '{key}' not declared in the plugin model")
        storage = self.get_storage(contrib, name=False) # storage attribute for contribution type
        if key not in storage:
            storage[key] = []
        storage[key].append(contrib)

    def get(self, key: str) -> List[Contrib]:
        """
        Get the contributions of the plugin for a specific field.

        Arguments
        ---------
        key : str
            Key of the field in the plugin model.

        Returns
        -------
        List[Contrib]
            Contributions of the plugin stored for the specified field.

        Implementation
        --------------
        To get the contributions for a specific field, the method:

        1. Retrieves the category of the field from the plugin model, using the key.
        2. Retrieves the storage dictionary corresponding to the category.
        3. Retrieves the contributions of the plugin for the specified field from the storage
           dictionary.
        """
        category = self.model.get(key).category
        storage = self.get_storage(category, name=False)
        return storage.get(key, [])

    def filter(self, category: Optional[Type[Contrib]] = None) -> TypeConstrainedDict[str, List[Contrib]]:
        """
        Get the contributions of the plugin, optionally filtered by category.

        Arguments
        ---------
        category : Type[Contrib]
            Category of the contributions to filter. If not provided, all contributions are
            returned.

        Returns
        -------
        TypeConstrainedDict[str, List[Contrib]]
            Contributions of the plugin, filtered by category if provided.

        Implementation
        --------------
        To filter the contributions by category, the method:

        1. Retrieves the storage dictionary corresponding to the category (if separated). If no
           category is provided, it combines the default storage dictionary with the specific
           storage dictionaries.
        2. Filters the dictionary to keep only contributions of the specified category (to handle
           sub-classes hierarchy in a specific storage, or multiple categories in the default
           storage). This is done by scanning the values of the dictionary (lists of contributions)
           and checking if any of their contributions is an instance of the specified category.
        """
        if category is None: # combine all storage dictionaries
            return {**getattr(self, self.default_storage), **{attr: getattr(self, attr) for attr in self.specific_storages.values()}}
        storage = self.get_storage(category, name=False)
        return {key: values for key, values in storage.items() if any(isinstance(contrib, category) for contrib in values)}
