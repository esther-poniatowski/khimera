#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_components.test_hooks
=======================================

Tests for the component and specification classes for hooks.

See Also
--------
khimera.components.hooks
"""
import pytest
from typing import Dict, Any
from khimera.components.hooks import Hook, HookSpec


# --- Tests for Hook (Component) ---------------------------------------------------------------------

def test_hook_initialization():
    """Test initialization of Hook."""
    name = "test_hook"
    description = "Test hook"
    def sample_hook(arg1: str, arg2: int) -> bool:
        return True

    hook = Hook(name=name, callable=sample_hook, description=description)
    assert hook.name == name
    assert hook.callable == sample_hook
    assert hook.description == description


# --- Tests for HookSpec (FieldSpec) ------------------------------------------------------------

def test_hookspec_initialization():
    """Test initialization of HookSpec."""
    name = "test_spec"
    description = "Test hook specification"
    arg_types: Dict[str, Any] = {"arg1": str, "arg2": int}
    return_type = bool
    unique = True
    required = True
    hookspec = HookSpec(
        name=name,
        arg_types=arg_types,
        return_type=return_type,
        unique=unique,
        required=required,
        description=description
    )
    assert hookspec.name == name
    assert hookspec.arg_types == arg_types
    assert hookspec.return_type == return_type
    assert hookspec.unique == unique
    assert hookspec.required == required
    assert hookspec.description == description

def test_hookspec_validate_valid_hook():
    """Test HookSpec validation with a valid hook."""
    def valid_hook(arg1: str, arg2: int) -> bool:
        return True

    hookspec = HookSpec(
        name="test_spec",
        arg_types={"arg1": str, "arg2": int},
        return_type=bool
    )
    hook = Hook(name="valid_hook", callable=valid_hook)
    assert hookspec.validate(hook) is True

# --- Tests for Input Types ---

def test_hookspec_validate_invalid_input_types():
    """Test HookSpec validation with invalid input types."""
    def invalid_hook(arg1: int, arg2: str) -> bool:
        return True

    hookspec = HookSpec(
        name="test_spec",
        arg_types={"arg2": str, "arg1": int},
        return_type=bool
    )
    hook = Hook(name="invalid_hook", callable=invalid_hook)
    assert hookspec.validate(hook) is False

def test_hookspec_validate_without_annotation():
    """Test HookSpec validation with missing type annotations."""
    def invalid_hook(arg1, arg2):
        return True

    hookspec = HookSpec(
        name="test_spec",
        arg_types={"arg1": str, "arg2": int},
        return_type=bool
    )
    hook = Hook(name="invalid_hook", callable=invalid_hook)
    assert hookspec.validate(hook) is False

def test_hookspec_validate_extra_parameter():
    """Test HookSpec validation with extra parameter."""
    def invalid_hook(arg1: str, arg2: int, extra: float) -> bool:
        return True

    hookspec = HookSpec(
        name="test_spec",
        arg_types={"arg1": str, "arg2": int},
        return_type=bool
    )
    hook = Hook(name="invalid_hook", callable=invalid_hook)
    assert hookspec.validate(hook) is False

def test_hookspec_validate_missing_parameter():
    """Test HookSpec validation with missing parameter."""
    def invalid_hook(arg1: str) -> bool:
        return True

    hookspec = HookSpec(
        name="test_spec",
        arg_types={"arg1": str, "arg2": int},
        return_type=bool
    )
    hook = Hook(name="invalid_hook", callable=invalid_hook)
    assert hookspec.validate(hook) is False



# --- Tests for Output Type ---

def test_hookspec_validate_no_return():
    """Test HookSpec validation with no return value."""
    def valid_hook(arg1: str, arg2: int):
        return True

    hookspec = HookSpec(
        name="test_spec",
        arg_types={"arg1": str, "arg2": int},
        return_type=None
    )
    hook = Hook(name="valid_hook", callable=valid_hook)
    assert hookspec.validate(hook) is True

def test_hookspec_validate_invalid_output_type():
    """Test HookSpec validation with invalid output type."""
    def invalid_hook(arg1: str, arg2: int) -> str:
        return "True"

    hookspec = HookSpec(
        name="test_spec",
        arg_types={"arg1": str, "arg2": int},
        return_type=bool
    )
    hook = Hook(name="invalid_hook", callable=invalid_hook)
    assert hookspec.validate(hook) is False
