"""
khimera.exceptions
==================

Domain-specific exception hierarchy for the khimera framework.

Classes
-------
KhimeraError
    Base exception for all khimera errors.
PluginValidationError
    Raised when a plugin fails validation against its model.
PluginConflictError
    Raised when a naming conflict occurs during plugin registration.
PluginNotFoundError
    Raised when a requested plugin cannot be found.
ComponentError
    Raised for component-level errors (duplicates, missing keys).
AmbiguousLookupError
    Raised when a lookup matches multiple results where one was expected.

See Also
--------
khimera.management.validate : Validation pipeline that produces ValidationResult.
khimera.management.register : Registration pipeline that raises on conflicts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from khimera.management.validate import ValidationResult


class KhimeraError(Exception):
    """Base exception for all khimera framework errors."""


class PluginValidationError(KhimeraError):
    """Raised when a plugin fails validation against its model.

    Attributes
    ----------
    result : ValidationResult
        Structured diagnostics from the validation pipeline.
    """

    def __init__(self, result: ValidationResult):
        self.result = result
        super().__init__(self._format(result))

    @staticmethod
    def _format(result: ValidationResult) -> str:
        parts = ["Plugin validation failed:"]
        if result.missing:
            parts.append(f"  Missing required fields: {result.missing}")
        if result.unknown:
            parts.append(f"  Unknown fields: {result.unknown}")
        if result.not_unique:
            parts.append(f"  Non-unique fields: {result.not_unique}")
        if result.invalid:
            parts.append(f"  Invalid components: {result.invalid}")
        if result.deps_unsatisfied:
            parts.append(f"  Unsatisfied dependencies: {result.deps_unsatisfied}")
        return "\n".join(parts)


class PluginConflictError(KhimeraError):
    """Raised when a naming conflict occurs during plugin registration."""


class PluginNotFoundError(KhimeraError):
    """Raised when a requested plugin cannot be found."""


class ComponentError(KhimeraError):
    """Raised for component-level errors (duplicates, missing keys)."""


class AmbiguousLookupError(KhimeraError):
    """Raised when a lookup matches multiple results where one was expected."""
