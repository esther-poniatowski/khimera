#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_components.test_api
=====================================

Tests for the component and specification classes for API extensions.

See Also
--------
khimera.components.api
"""
# --- Silenced Errors ---
# pylint: disable=unused-variable
#   Test functions are used, but pylint does not detect it.
# pylint: disable=unused-import
#   Pytest is imported for testing while not explicitly used in this module.

from types import FunctionType
from collections.abc import Callable

import pytest

from khimera.components.api import APIExtension, APIExtensionSpec


# --- Tests for APIExtension (Component) -----------------------------------------------------------


def test_api_extension_initialization():
    """Test initialization of `APIExtension`."""
    name = "test_extension"
    description = "test description"

    def sample_function():
        pass

    api_extension = APIExtension(name=name, extension=sample_function, description=description)
    assert api_extension.name == name
    assert api_extension.extension is sample_function
    assert api_extension.description == description


# --- Tests for APIExtensionSpec (FieldSpec) -------------------------------------------------------


def test_api_extension_spec_initialization():
    """Test initialization of `APIExtensionSpec`."""
    name = "test_spec"
    valid_types = (Callable,)
    required = True
    unique = False
    description = "test field description"
    api_extension_spec = APIExtensionSpec(
        name=name,
        valid_types=valid_types,
        required=required,
        unique=unique,
        description=description,
    )
    assert api_extension_spec.name == name
    assert api_extension_spec.valid_types == valid_types
    assert api_extension_spec.required == required
    assert api_extension_spec.unique == unique
    assert api_extension_spec.description == description


def test_api_extension_spec_validate_no_type_restriction():
    """Test `APIExtensionSpec` validation with no type restriction."""

    class SampleClass:
        pass

    api_extension_spec = APIExtensionSpec(name="test_spec")
    api_extension = APIExtension(name="test_extension", extension=SampleClass)
    assert api_extension_spec.validate(api_extension) is True


def test_api_extension_spec_validate_function():
    """Test `APIExtensionSpec` validation for a function."""

    def sample_function():
        pass

    api_extension_spec = APIExtensionSpec(
        name="test_spec",
        valid_types=(FunctionType,),
        check_inheritance=False,
    )
    api_extension = APIExtension(name="test_extension", extension=sample_function)
    assert api_extension_spec.validate(api_extension) is True


def test_api_extension_spec_validate_function_incorrect():
    """Test `APIExtensionSpec` validation for function, providing a class."""

    class SampleClass:
        pass

    api_extension_spec = APIExtensionSpec(
        name="test_spec",
        valid_types=(FunctionType,),
        check_inheritance=False,
    )
    api_extension = APIExtension(name="test_extension", extension=SampleClass)
    assert api_extension.extension == SampleClass
    assert api_extension_spec.valid_types is not None
    assert api_extension_spec.validate(api_extension) is False


def test_api_extension_spec_validate_inheritance():
    """Test `APIExtensionSpec` validation for inheritance (checks subclass of valid type)."""

    class BaseClass:
        pass

    class DerivedClass(BaseClass):
        pass

    api_extension_spec = APIExtensionSpec(
        name="test_spec",
        valid_types=(BaseClass,),
        check_inheritance=True,
    )
    api_extension = APIExtension(name="test_extension", extension=DerivedClass)
    assert api_extension_spec.validate(api_extension) is True


def test_api_extension_spec_validate_no_inheritance():
    """Test `APIExtensionSpec` validation for instance of valid type."""

    class BaseClass:
        pass

    class DerivedClass(BaseClass):
        pass

    api_extension_spec = APIExtensionSpec(
        name="test_spec",
        valid_types=(BaseClass,),
        check_inheritance=False,
    )
    api_extension = APIExtension(name="test_extension", extension=DerivedClass)
    assert api_extension_spec.validate(api_extension) is False


def test_api_extension_spec_validate_union_type():
    """Test `APIExtensionSpec` validation with multiple valid types."""

    class BaseClass1:
        pass

    class BaseClass2:
        pass

    class DerivedClass1(BaseClass1):
        pass

    class DerivedClass2(BaseClass2):
        pass

    api_extension_spec = APIExtensionSpec(
        name="test_spec", valid_types=(BaseClass1, BaseClass2), check_inheritance=True
    )
    api_extension1 = APIExtension(name="test_extension1", extension=DerivedClass1)
    api_extension2 = APIExtension(name="test_extension2", extension=DerivedClass2)
    assert api_extension_spec.validate(api_extension1) is True
    assert api_extension_spec.validate(api_extension2) is True


def test_api_extension_spec_validate_function_with_inheritance_check():
    """Test `APIExtensionSpec` validation of a function with inheritance checking enabled."""

    def sample_function():
        pass

    api_extension_spec = APIExtensionSpec(
        name="test_spec",
        valid_types=(FunctionType,),
        check_inheritance=True,
    )
    api_extension = APIExtension(name="test_extension", extension=sample_function)
    assert api_extension_spec.validate(api_extension) is False


def test_api_extension_spec_validate_builtin_types():
    """Test `APIExtensionSpec` validation with built-in types."""
    api_extension_spec = APIExtensionSpec(
        name="test_spec",
        valid_types=(int, str),
        check_inheritance=False,
    )
    api_extension1 = APIExtension(name="test_extension1", extension=1)
    api_extension2 = APIExtension(name="test_extension2", extension="a")
    assert api_extension_spec.validate(api_extension1) is True
    assert api_extension_spec.validate(api_extension2) is True
