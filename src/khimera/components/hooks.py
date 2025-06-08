"""
khimera.components.hooks
========================

Classes defining hooks in plugin models and instances.

Classes
-------
Hook
    Represents a hook to be executed by the host application.
HookSpec
    Declare a hook expected by the host application.

See Also
--------
khimera.core.components.Component
    Abstract base class representing a component to a plugin instance.
khimera.core.specifications.FieldSpec
    Abstract base class for defining constraints and validations for components in a plugin model.
"""
from collections import OrderedDict
import inspect
from typing import Any, Callable, Union, Optional, Type, Tuple, List

from khimera.core.components import Component
from khimera.core.specifications import FieldSpec


class Hook(Component):
    """
    Represents a hook to be executed by the host application.

    Attributes
    ----------
    func : Callable
        Function or method to be executed when the hook is triggered.

    Warnings
    --------
    The hook function must be annotated with type hints. This is necessary to match the expected
    signature defined by the corresponding `HookSpec`.
    """

    def __init__(self, name: str, func: Callable, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.func = func


class HookSpec(FieldSpec[Hook]):
    """
    Declare a hook expected by the host application.

    Attributes
    ----------
    arg_types : OrderedDict[str, Type]
        Expected names and types of positional arguments, in order.
        If the argument passed at initialization is a bare dictionary, it will be converted to an
        OrderedDict to ensure consistent ordering.
    allow_var_args : bool
        Allow arbitrary positional arguments.
    allow_var_kwargs : bool
        Allow arbitrary keyword arguments.
    return_type : Optional[Type]
        Expected return type(s). If None, the function should not return anything.

    Notes
    -----
    Hooks must exactly match the expected function signature in terms of argument names, types,
    and return type.

    Examples
    --------
    Declare a hook field with expected inputs and output type:

    >>> hook_spec = HookSpec(name="on_event",
    ...                      arg_types={"name": str, "value": int},
    ...                      output_type=bool)

    Create valid and invalid hook components:

    >>> def valid_hook(name: str, value: int) -> bool:
    ...     return isinstance(value, int)
    >>> def invalid_hook(value: str, name: str) -> bool:
    ...     return True
    >>> valid_comp = Hook(name="valid_hook", callable=valid_hook)
    >>> invalid_comp = Hook(name="invalid_hook", callable=invalid_hook)

    Validate the components against the hook field:

    >>> print(hook_spec.validate(valid_comp))
    True
    >>> print(hook_spec.validate(invalid_comp))
    False
    """

    COMPONENT_TYPE = Hook

    def __init__(
        self,
        name: str,
        arg_types: OrderedDict[str, Type],
        allow_var_args: bool = False,
        allow_var_kwargs: bool = False,
        return_type: Optional[Union[Type, Tuple[Type, ...]]] = None,
        required: bool = False,
        unique: bool = True,
        description: Optional[str] = None,
    ):
        super().__init__(name=name, required=required, unique=unique, description=description)
        self.arg_types = arg_types if isinstance(arg_types, OrderedDict) else OrderedDict(arg_types)
        self.allow_var_args = allow_var_args
        self.allow_var_kwargs = allow_var_kwargs
        self.return_type = return_type

    def validate(self, obj: Hook) -> bool:
        """Validate that the hook function matches the expected signature."""
        pos, _, has_var_pos, has_var_kw, return_ann = self.describe_signature(obj.func)
        return self.check_inputs(pos, has_var_pos, has_var_kw) and self.check_output(return_ann)

    @staticmethod
    def describe_signature(
        fn: Callable,
    ) -> Tuple[List[Tuple[str, Any]], List[str], bool, bool, Any]:
        """
        Describe the signature of a function or method.

        Parameters
        ----------
        fn : Callable
            Function or method to describe.

        Returns
        -------
        positional : List[Tuple[str, Any]]
            Names and types of positional arguments, in order. Types are inferred from type hints,
            and Any is used if no type hint is provided.
        keyword_only : List[str]
            Names of keyword-only arguments.
        has_var_positional : bool
            True if the function has `*args`.
        has_var_keyword : bool
            True if the function has `**kwargs`.
        return_annotation : Any
            Return type annotation of the function. If None, the return type is not annotated.
        """
        sig = inspect.signature(fn)
        params = sig.parameters
        return_annotation = sig.return_annotation
        positional: List[Tuple[str, Any]] = []
        keyword_only: List[str] = []
        has_var_positional = False
        has_var_keyword = False
        for param in params.values():
            if param.kind in {  # check if parameter is positional
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            }:
                positional.append((param.name, param.annotation))
            elif param.kind == inspect.Parameter.KEYWORD_ONLY:
                keyword_only.append(param.name)
            elif param.kind == inspect.Parameter.VAR_POSITIONAL:  # *args
                has_var_positional = True
            elif param.kind == inspect.Parameter.VAR_KEYWORD:  # **kwargs
                has_var_keyword = True
        return positional, keyword_only, has_var_positional, has_var_keyword, return_annotation

    def check_inputs(
        self,
        positional: List[Tuple[str, Any]],
        has_var_positional: bool,
        has_var_keyword: bool,
    ) -> bool:
        """
        Validate if a function matches the signature constraints.

        Returns
        -------
        bool
            True if the function matches the constraints, False otherwise.
        """
        # Check exact argument names and order
        expected_names, expected_types = zip(*self.arg_types.items())
        actual_names, actual_types = zip(*positional)
        if expected_names != actual_names:
            return False
        # Check argument types (more permissive if not provided)
        for expected, actual in zip(expected_types, actual_types):
            if expected is not Any and not issubclass(actual, expected):
                return False
        # Check *args and **kwargs constraints
        if has_var_positional and not self.allow_var_args:
            return False
        if has_var_keyword and not self.allow_var_kwargs:
            return False
        return True

    def check_output(self, return_annotation: Any) -> bool:
        """Check if the hook function has the expected return type."""
        if self.return_type is Any:
            return True
        if self.return_type is None:
            return return_annotation in {None, inspect.Signature.empty}
        if isinstance(self.return_type, tuple):
            return isinstance(return_annotation, self.return_type)
        return return_annotation == self.return_type
