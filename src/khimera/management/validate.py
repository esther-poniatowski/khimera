"""
khimera.management.validate
===========================

Validate the components of a plugin against its model.

See Also
--------
khimera.core
khimera.plugins.declare
khimera.plugins.create
"""

from dataclasses import dataclass, field
from typing import List, Dict

from khimera.plugins.create import Plugin


@dataclass(frozen=True)
class ValidationResult:
    """Structured diagnostics produced by :class:`PluginValidator`."""

    missing: List[str] = field(default_factory=list)
    """Required fields absent from the plugin instance."""
    unknown: List[str] = field(default_factory=list)
    """Fields present in the plugin but not declared in the model."""
    not_unique: List[str] = field(default_factory=list)
    """Fields constrained to a unique component that contain more than one."""
    invalid: Dict[str, list] = field(default_factory=dict)
    """Mapping of field names to lists of components that failed rule validation."""
    deps_unsatisfied: List[str] = field(default_factory=list)
    """Dependency specifications that the plugin does not satisfy."""

    @property
    def is_valid(self) -> bool:
        """Whether the validation passed with no diagnostics."""
        return not (
            self.missing or self.unknown or self.not_unique or self.invalid or self.deps_unsatisfied
        )


class PluginValidator:
    """
    Validates the components of a plugin instance against its model.

    Parameters
    ----------
    plugin : Plugin
        Plugin instance to validate. The plugin's model is used as the validation reference.
    """

    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.model = plugin.model
        self.missing: List[str] = []
        self.unknown: List[str] = []
        self.not_unique: List[str] = []
        self.invalid: Dict = {}
        self.deps_unsatisfied: List[str] = []

    def check_required(self) -> None:
        """Check if all required components are present in the plugin instance."""
        specs = self.model.filter(required=True)
        self.missing = [field for field in specs if field not in self.plugin.components]

    def check_unique(self) -> None:
        """Check if components are unique where required."""
        specs = self.model.filter(unique=True)
        self.not_unique = [field for field in specs if len(self.plugin.get(field)) > 1]

    def check_unknown(self) -> None:
        """Check if components are unknown."""
        self.unknown = [field for field in self.plugin.components if field not in self.model.fields]

    def check_rules(self) -> None:
        """Validate the components of the plugin instance against the rules of the model."""
        invalid: Dict = {}
        for field, comps in self.plugin.components.items():  # field: field name, comps: list
            spec = self.model.get(field)  # spec to use for validation
            invalid_components = [item for item in comps if not spec.validate(item)]
            if invalid_components:
                invalid[field] = invalid_components
        self.invalid = invalid

    def check_dependencies(self) -> None:
        """Check if all dependencies are satisfied in the plugin instance."""
        self.deps_unsatisfied = [
            field for field, spec in self.model.dependencies.items() if not spec.validate(self.plugin)
        ]

    def validate(self) -> ValidationResult:
        """
        Validate the components of the plugin instance against its model.

        Returns
        -------
        ValidationResult
            Frozen dataclass containing all diagnostics, with an ``is_valid`` property.
        """
        self.check_required()
        self.check_unique()
        self.check_unknown()
        self.check_rules()
        self.check_dependencies()
        return ValidationResult(
            missing=list(self.missing),
            unknown=list(self.unknown),
            not_unique=list(self.not_unique),
            invalid=dict(self.invalid),
            deps_unsatisfied=list(self.deps_unsatisfied),
        )

    def extract(self) -> Plugin:
        """
        Extract the valid components from the plugin instance.

        Return
        ------
        valid_plugin : Plugin
            Plugin instance containing only the valid components.

        Warning
        -------
        This correction does not guarantee that the resulting plugin instance is valid, as it does
        not provide missing components nor satisfy the dependencies.
        """
        valid_plugin = self.plugin.copy()
        for key in self.invalid:  # key in plugin instance
            valid_plugin.components.pop(key)  # remove invalid components
        for key in self.unknown:  # key in plugin instance
            valid_plugin.components.pop(key)  # remove unknown components
        for key in self.not_unique:  # key in plugin instance
            valid_plugin.components[key] = [
                valid_plugin.components[key][0]
            ]  # keep the first component
        return valid_plugin
