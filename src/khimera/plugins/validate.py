#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.create
======================

Validate the contributions of a plugin against its model.

Classes
-------
PluginValidator
    Validates the contributions of a plugin instance against its model.

See Also
--------
khimera.plugins.core
khimera.plugins.declare
khimera.plugins.create
"""

from typing import List

from khimera.utils.factories import TypeConstrainedDict
from khimera.contributions.core import ContribList
from khimera.plugins.create import Plugin


class PluginValidator:
    """
    Validates the contributions of a plugin instance against its model.

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
        Fields that are expected to admit a unique contribution in the model, but contain more than
        one contribution in the plugin instance.
        Names are present in both the model and the plugin instance.
    invalid : TypeConstrainedDict[str, ContribList]
        Invalid contributions for each specification field in the plugin model, which do not satisfy
        pass the `validate` method of the corresponding `Spec` instance.
        Keys: Names of the fields present both in the model and the plugin instance.
        Values: Invalid contribution(s) from the plugin instance.
    deps_unsatisfied : List[str]
        Dependencies (`DependencySpec` fields in the model) that are not satisfied in the plugin
        instance.
        Names are present in the model only, since they are pure rules which do not expect to be
        filled by contributions in the plugin instance.
    """
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.model = plugin.model
        self.missing : List[str] = []
        self.unknown : List[str] = []
        self.not_unique : List[str] = []
        self.invalid = TypeConstrainedDict(str, ContribList)
        self.deps_unsatisfied : List[str] = []

    def check_required(self) -> None:
        """Check if all required contributions are present in the plugin instance."""
        specs = self.model.filter(self, required=True)
        for key in specs:
            if key not in self.plugin.contributions:
                self.missing.append(key)

    def check_unique(self) -> None:
        """Check if contributions are unique where required."""
        specs = self.model.filter(unique=True)
        for key, spec in specs.items():
            if key in self.plugin.contributions and len(self.plugin.contributions[key]) > 1:
                self.not_unique.append(key)

    def check_unknown(self) -> None:
        """Check if contributions are unknown."""
        for key in self.plugin.contributions:
            if key not in self.model.specs:
                self.unknown.append(key)

    def check_rules(self) -> None:
        """Validate the contributions of the plugin instance against the rules of the model."""
        for key, contribs in self.plugin.contributions.items(): # key: spec name, contribs: list
            spec = self.model.get(key)
            for item in contribs: # item: candidate contribution
                if not spec.validate(item):
                    self.invalid[key].append(item)

    def check_dependencies(self) -> None:
        """Check if all dependencies are satisfied in the plugin instance."""
        for key, spec in self.model.dependencies.items():
            if not spec.validate(self.plugin):
                self.deps_unsatisfied.append(key)

    def validate(self) -> bool:
        """
        Validate the contributions of the plugin instance against its model.

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
        Extract the valid contributions from the plugin instance.

        Return
        ------
        Plugin
            Plugin instance with only the valid contributions.

        Warning
        -------
        This correction does not guarantee that the resulting plugin instance is valid, as it does
        not provide missing contributions nor satisfy the dependencies.
        """
        valid = self.plugin.copy()
        for key in self.invalid: # keys in plugin instance
            valid.contributions.pop(key) # remove invalid contributions
        for key in self.unknown: # keys in plugin instance
            valid.contributions.pop(key) # remove unknown contributions
        for key in self.not_unique: # keys in plugin instance
            valid.contributions[key] = [valid.contributions[key][0]] # keep the first contribution
        return valid
