#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.create
======================

Validate the components of a plugin against its model.

Classes
-------
PluginValidator
    Validates the components of a plugin instance against its model.

See Also
--------
khimera.plugins.core
khimera.plugins.declare
khimera.plugins.create
"""

from typing import List

from khimera.utils.factories import TypeConstrainedDict
from khimera.components.core import ComponentSet
from khimera.plugins.create import Plugin


class PluginValidator:
    """
    Validates the components of a plugin instance against its model.

    Attributes
    ----------
    plugin : Plugin
        Plugin instance to validate.
    model : PluginModel
        Plugin model to validate against (referenced in the plugin instance).
    missing : List[str]
        Fields that are required in the model, but are missing in the plugin instance.
        Names are present in the model, but not in the plugin instance.
    unknown : List[str]
        Fields in the plugin instance which are not expected by the model.
        Names are present in the plugin instance, but not in the model.
    not_unique : List[str]
        Fields that are expected to admit a unique component in the model, but contain more than
        one component in the plugin instance.
        Names are present in both the model and the plugin instance.
    invalid : TypeConstrainedDict[str, ComponentSet]
        Invalid components for each specification field in the plugin model, which do not satisfy
        pass the `validate` method of the corresponding `Spec` instance.
        Keys: Names of the fields present both in the model and the plugin instance.
        Values: Invalid component(s) from the plugin instance.
    deps_unsatisfied : List[str]
        Dependencies (`DependencySpec` fields in the model) that are not satisfied in the plugin
        instance.
        Names are present in the model only, since they are pure rules which do not expect to be
        filled by components in the plugin instance.
    """
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.model = plugin.model
        self.missing : List[str] = []
        self.unknown : List[str] = []
        self.not_unique : List[str] = []
        self.invalid = TypeConstrainedDict(str, ComponentSet)
        self.deps_unsatisfied : List[str] = []

    def check_required(self) -> None:
        """Check if all required components are present in the plugin instance."""
        fields = self.model.filter(self, required=True)
        for key in fields:
            if key not in self.plugin.components:
                self.missing.append(key)

    def check_unique(self) -> None:
        """Check if components are unique where required."""
        fields = self.model.filter(unique=True)
        for key, field in fields.items():
            if key in self.plugin.components and len(self.plugin.components[key]) > 1:
                self.not_unique.append(key)

    def check_unknown(self) -> None:
        """Check if components are unknown."""
        for key in self.plugin.components:
            if key not in self.model.fields:
                self.unknown.append(key)

    def check_rules(self) -> None:
        """Validate the components of the plugin instance against the rules of the model."""
        for key, contribs in self.plugin.components.items(): # key: field name, contribs: list
            field = self.model.get(key)
            for item in contribs: # item: candidate component
                if not field.validate(item):
                    self.invalid[key].append(item)

    def check_dependencies(self) -> None:
        """Check if all dependencies are satisfied in the plugin instance."""
        for key, field in self.model.dependencies.items():
            if not field.validate(self.plugin):
                self.deps_unsatisfied.append(key)

    def validate(self) -> bool:
        """
        Validate the components of the plugin instance against its model.

        Returns
        -------
        bool
            Whether the entire plugin instance is valid.
        """
        self.check_required()
        self.check_unique()
        self.check_unknown()
        self.check_rules()
        self.check_dependencies()
        return not (self.missing or self.unknown or self.not_unique or self.invalid or self.deps_unsatisfied)

    def extract(self) -> Plugin:
        """
        Extract the valid components from the plugin instance.

        Return
        ------
        Plugin
            Plugin instance with only the valid components.

        Warning
        -------
        This correction does not guarantee that the resulting plugin instance is valid, as it does
        not provide missing components nor satisfy the dependencies.
        """
        valid = self.plugin.copy()
        for key in self.invalid: # keys in plugin instance
            valid.components.pop(key) # remove invalid components
        for key in self.unknown: # keys in plugin instance
            valid.components.pop(key) # remove unknown components
        for key in self.not_unique: # keys in plugin instance
            valid.components[key] = [valid.components[key][0]] # keep the first component
        return valid
