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
# --- Silenced Errors ---
# pylint: disable=unused-variable
#   Test functions are used, but pylint does not detect it.
# pylint: disable=unused-import
#   Pytest is imported for testing while not explicitly used in this module.
# pylint: disable=unused-argument
#   Sample test functions admit arguments that are not used.

from typing import Dict, Any

import pytest

from khimera.components.hooks import Hook, HookSpec


# --- Tests for Hook (Component) -------------------------------------------------------------------


def test_hook_initialization():
    """Test initialization of `Hook`."""
    name = "test_hook"
    description = "Test hook"

    def sample_hook(arg1: str, arg2: int) -> bool:
        return True

    hook = Hook(name=name, func=sample_hook, description=description)
    assert hook.name == name
    assert hook.func is sample_hook
    assert hook.description == description


# --- Tests for HookSpec (FieldSpec) ------------------------------------------------------------


def test_hook_spec_initialization():
    """Test initialization of `HookSpec`."""
    name = "test_spec"
    description = "Test hook specification"
    arg_types = {"arg1": str, "arg2": int}
    return_type = bool
    unique = True
    required = True
    hook_spec = HookSpec(
        name=name,
        arg_types=arg_types,
        return_type=return_type,
        unique=unique,
        required=required,
        description=description,
    )
    assert hook_spec.name == name
    assert hook_spec.arg_types == arg_types
    assert hook_spec.return_type == return_type
    assert hook_spec.unique == unique
    assert hook_spec.required == required
    assert hook_spec.description == description


def test_hook_spec_validate_valid_hook():
    """Test `HookSpec` validation with a valid hook."""

    def valid_hook(arg1: str, arg2: int) -> bool:
        return True

    hook_spec = HookSpec(name="test_spec", arg_types={"arg1": str, "arg2": int}, return_type=bool)
    hook = Hook(name="valid_hook", func=valid_hook)
    assert hook_spec.validate(hook) is True


# --- Tests for Input Types ------------------------------------------------------------------------


def test_hook_spec_validate_invalid_input_types():
    """Test `HookSpec` validation with invalid input types."""

    def invalid_hook(arg1: int, arg2: str) -> bool:
        return True

    hook_spec = HookSpec(name="test_spec", arg_types={"arg2": str, "arg1": int}, return_type=bool)
    hook = Hook(name="invalid_hook", func=invalid_hook)
    assert hook_spec.validate(hook) is False


def test_hook_spec_validate_without_annotation():
    """Test `HookSpec` validation with missing type annotations."""

    def invalid_hook(arg1, arg2):
        return True

    hook_spec = HookSpec(name="test_spec", arg_types={"arg1": str, "arg2": int}, return_type=bool)
    hook = Hook(name="invalid_hook", func=invalid_hook)
    assert hook_spec.validate(hook) is False


def test_hook_spec_validate_extra_parameter():
    """Test `HookSpec` validation with extra parameter."""

    def invalid_hook(arg1: str, arg2: int, extra: float) -> bool:
        return True

    hook_spec = HookSpec(name="test_spec", arg_types={"arg1": str, "arg2": int}, return_type=bool)
    hook = Hook(name="invalid_hook", func=invalid_hook)
    assert hook_spec.validate(hook) is False


def test_hook_spec_validate_missing_parameter():
    """Test `HookSpec` validation with missing parameter."""

    def invalid_hook(arg1: str) -> bool:
        return True

    hook_spec = HookSpec(name="test_spec", arg_types={"arg1": str, "arg2": int}, return_type=bool)
    hook = Hook(name="invalid_hook", func=invalid_hook)
    assert hook_spec.validate(hook) is False


# --- Tests for Output Type ------------------------------------------------------------------------


def test_hook_spec_validate_no_return():
    """Test `HookSpec` validation with no return value."""

    def valid_hook(arg1: str, arg2: int):
        return True

    hook_spec = HookSpec(name="test_spec", arg_types={"arg1": str, "arg2": int}, return_type=None)
    hook = Hook(name="valid_hook", func=valid_hook)
    assert hook_spec.validate(hook) is True


def test_hook_spec_validate_invalid_output_type():
    """Test `HookSpec` validation with invalid output type."""

    def invalid_hook(arg1: str, arg2: int) -> str:
        return "True"

    hook_spec = HookSpec(name="test_spec", arg_types={"arg1": str, "arg2": int}, return_type=bool)
    hook = Hook(name="invalid_hook", func=invalid_hook)
    assert hook_spec.validate(hook) is False
