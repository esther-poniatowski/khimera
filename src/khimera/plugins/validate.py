#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.plugins.create
======================

Validate the contributions of a plugin against its model.


See Also
--------
khimera.plugins.core
khimera.plugins.declare
khimera.plugins.create
"""

from typing import List

from khimera.utils.factories import TypeConstrainedDict
from khimera.plugins.core import Contrib, Spec
from khimera.plugins.declare import PluginModel
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
        Names of the fields that are required in the model, but are missing in the plugin instance.
    unknown : List[str]
        Names of the fields in the plugin instance which are not expected by the model.
    not_unique : List[str]
        Names of the fields are expected to admit a unique contribution in the model, but contain
        more than one contribution in the plugin instance.
    invalid : TypeConstrainedDict[str, List[Contrib]]
        Invalid contributions for each specification field in the plugin model, which do not satisfy
        pass the `validate` method of the corresponding `Spec` instance.
        Keys: Names of the specification fields declared in the plugin model.
        Values: Invalid contribution(s) for each field.
    deps_unsatisfied : List[str]
        Names of the dependencies that are not satisfied in the plugin instance.
    """
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.model = plugin.model
        self.missing : List[str] = []
        self.unknown : List[str] = []
        self.not_unique : List[str] = []
        self.invalid = TypeConstrainedDict[str, List[Contrib]]()
        self.deps_unsatisfied : List[str] = []

    def check_required(self) -> None:
        """Check if all required contributions are present in the plugin instance."""
        specs = self.model.filter(self, required=True)
        for key in specs:
            if key not in self.plugin.contributions:
                self.invalid[key].append(None)

    def check_unique(self) -> None:
        """Check if contributions are unique where required."""
        specs = self.model.filter(self, unique=True)
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
