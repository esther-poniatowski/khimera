#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.contributions.hooks
===========================

Classes for defining hooks in plugin models and instances.

Classes
-------
Hook
    Represents a hook to be executed by the host application.
HookSpec
    Declare a hook expected by the host application.

See Also
--------
khimera.plugins.core.Contrib
    Abstract base class representing a contribution to a plugin instance.
khimera.plugins.core.CategorySpec
    Abstract base class for defining constraints and validations for contributions in a plugin model.
"""
from typing import Any, Callable, Dict, Optional, Type, inspect

from khimera.contributions.core import Contrib, CategorySpec

class Hook(Contrib):
    """
    Represents a hook to be executed by the host application.

    Attributes
    ----------
    callable : Callable
        Function or method to be executed when the hook is triggered.
    """
    def __init__(self, name: str, callable: Callable, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.callable = callable


class HookSpec(CategorySpec[Hook]):
    """
    Declare a hook expected by the host application.

    Attributes
    ----------
    expected_inputs : Dict[str, Type]
        Expected argument names and their types.
    expected_output : Optional[Type]
        Expected return type of the function.

    Notes
    -----
    Hooks must exactly match the expected function signature in terms of argument names, types,
    and return type.

    Examples
    --------
    Declare a hook spec with expected inputs and output type:

    >>> hook_spec = HookSpec(name="on_event",
    ...                      expected_inputs={"name": str, "value": int},
    ...                      output_type=bool)

    Create valid and invalid hook contributions:

    >>> def valid_hook(name: str, value: int) -> bool:
    ...     return isinstance(value, int)
    >>> def invalid_hook(name: str, value: str) -> bool:
    ...     return True
    >>> valid_contrib = Hook(name="valid_hook", callable=valid_hook)
    >>> invalid_contrib = Hook(name="invalid_hook", callable=invalid_hook)

    Validate the contributions against the hook spec:

    >>> print(hook_spec.validate(valid_contrib))
    True
    >>> print(hook_spec.validate(invalid_contrib))
    False
    """
    CONTRIB_TYPE = Hook

    def __init__(self, name: str, expected_inputs: Dict[str, Type], expected_output: Optional[Type] = None,
                 required: bool = False, unique: bool = True, description: Optional[str] = None):
        super().__init__(name=name, required=required, unique=unique, description=description)
        self.expected_inputs = expected_inputs
        self.expected_output = expected_output

    def validate(self, contrib: Hook) -> bool:
        """Validate that the hook function matches the expected signature."""
        signature = inspect.signature(contrib.callable)
        self.check_inputs(signature.parameters)
        self.check_output(signature.return_annotation)
        return True

    def check_inputs(self, parameters: Dict[str, inspect.Parameter]) -> bool:
        """Check if the hook function has the expected input parameters."""
        if len(parameters) != len(self.expected_inputs):
            return False  # unexpected number of parameters
        for param_name, param in parameters.items():
            expected_type = self.expected_inputs.get(param_name)
            if expected_type is None:
                return False  # unexpected parameter
            if param.annotation is not inspect.Parameter.empty and param.annotation != expected_type:
                return False  # Type mismatch for this parameter
        return True

    def check_output(self, return_annotation: Any) -> bool:
        """Check if the hook function has the expected return type."""
        if self.expected_output is not None and return_annotation is not inspect.Signature.empty:
            return return_annotation == self.expected_output
        return True
