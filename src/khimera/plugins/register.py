#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.register
========================

Registers plugins on the host application side.

Classes
-------
PluginRegistry

See Also
--------
"""
from typing import Dict, List, Type, TypeVar, Optional, Generic
import warnings

from khimera.utils.factories import TypeConstrainedDict, TypeConstrainedList
from khimera.plugins.declare import PluginModel
from khimera.plugins.create import Plugin
from khimera.components.core import Component, ComponentSet
from khimera.plugins.validate import PluginValidator

E = TypeVar('E', bound=Plugin | Component)
"""Type variable for elements in the registry."""


class ConflictResolver:
    """Implements different strategies for resolving conflicts between plugins.

    Attributes
    ----------
    MODES : Dict[str, callable]
        Mapping of conflict resolution modes to their respective methods.
    mode : str
        Strategy to apply to resolve conflicts between plugins.
    """
    def __init__(self, mode: str = 'RAISE_ERROR'):
        self.mode = mode
        self.MODES: Dict[str, callable] = {
            "RAISE_ERROR": self.raise_error,
            "OVERRIDE": self.override,
            "IGNORE": self.ignore
        }

    def resolve(self, new: E) -> E | None:
        """
        Select and apply the conflict resolution strategy.

        Returns
        -------
        E
            Resolved element to register, if any.

        Raises
        ------
        ValueError, UserWarning
            Depending on the conflict resolution strategy.
        """
        return self.MODES[self.mode](new)

    def raise_error(self, new: E) -> E:
        """Fail when conflicts occur."""
        raise ValueError(f"Already registered.")

    def override(self,  new: E) -> E:
        """ Replace the existing element by the latest registered."""
        warnings.warn(f"Overridden: name '{new.name}' already registered.", UserWarning)
        return new

    def ignore(self,  new: E) -> None:
        """Keep the existing element and discard the new one."""
        warnings.warn(f"Ignored: name '{new.name}' already registered.", UserWarning)
        return None


class PluginRegistry:
    """
    Stores and manage plugins, resolve conflicts and provide components retrieval.

    Attributes
    ----------
    resolver : ConflictResolver
        Strategy to resolve conflicts when registering plugins.
    validator : PluginValidator
        Validator to check the plugin structure and components against its model.
    enable_by_default : bool
        Whether to enable plugins by default when registering them.
    plugins : Dict[str, Plugin]
        Registered plugins by name.
    enabled : List[str]
        List of enabled plugins, whose components are available in the registry.
    components : Dict[str, ComponentSet]
        Mapping of component keys to the actual components provided by the plugins.
        Keys: Contribution key, as specified in the plugin model.
        Values: List of components registered under this key across all plugins.

    Examples
    --------
    Initialize a plugin registry:

    >>> registry = PluginRegistry()

    Define a plugin with two components:

    >>> plugin = Plugin('my_plugin', '1.0.0')
    >>> def plugin_hook(arg) -> bool:
    ...     print(arg)
    >>> plugin.add('hook', Hook(name="my_hook", callable=plugin_hook))
    >>> plugin.add('input_file', Asset(name="logo", package="my_package", file_path="assets/logo.png"))

    Register the plugin in the registry:

    >>> registry.register(plugin)
    >>> print(registry.plugins)
    {'my_plugin': Plugin(name='my_plugin', version='1.0.0', ...)}

    Get all the components under a specific key:

    >>> hooks = registry.get('hook')
    >>> print(hooks)
    [Hook(name='my_hook')]

    Disable the plugin:

    >>> registry.disable('my_plugin')
    >>> print(registry.enabled)
    []

    Notes
    -----
    So far, a single version per plugin is allowed in the registry.
    """
    def __init__(self, resolver = ConflictResolver('RAISE_ERROR'), validator = PluginValidator(), enable_by_default = True):
        self.resolver = resolver
        self.validator = validator
        self.enable_by_default = enable_by_default
        self.plugins = TypeConstrainedDict(str, Plugin)
        self.enabled : List[str] = []
        self.components = TypeConstrainedDict(str, ComponentSet)

    def register(self, plugin: Plugin):
        """
        Default registering behavior. Override this method to customize the registration process.
        """
        if self.validator.validate(plugin):
            new = plugin
            if plugin.name in self.plugins:
                new = self.resolver.resolve(plugin)
            if new :
                self.plugins[plugin.name] = plugin
                if self.enable_by_default:
                    self.enable(plugin)
        else:
            raise ValueError(f"Invalid plugin: {plugin.name}")

    def enable(self, name: str) -> None:
        """
        Enable all the components of the plugin from the registry.

        Arguments
        ---------
        name : str
            Name of the plugin to enable.

        Notes
        -----
        Enabling a plugin consists in making all its components available in the registry.
        Components are unpacked from the plugin and stored in the registered components under
        the same key. If the key does not exist, it is created.
        """
        plugin = self.plugins[name]
        for key, contribs in plugin.components.items():
            if key not in self.components:
                self.components[key] = TypeConstrainedList(Component)
            self.components[key].extend(contribs)

    def disable(self, name: str) -> None:
        """
        Disable all the components of the plugin from the registry.

        Arguments
        ---------
        name : str
            Name of the plugin to disable.

        Notes
        -----
        Disabling a plugin consists in removing all its components from the registry.
        Components are still stored in the plugin instance, but are not available for retrieval.
        """
        for key in self.plugins[name].components:
            self.components[key] = [contrib for contrib in self.components[key] if contrib.plugin != name]

    def get(self, key: str, name: Optional[str]) -> List[Component]:
        """
        Retrieve all components under a specific key.

        Arguments
        ---------
        key : str
            Contribution key (general category) to retrieve.
        name : str, optional
            Name of the specific component to retrieve.

        Returns
        -------
        ComponentSet
            All the components registered under this key, and matching the name if provided.
        """
        contribs = self.components[key]
        return [contrib for contrib in contribs if name is None or contrib.name == name]
