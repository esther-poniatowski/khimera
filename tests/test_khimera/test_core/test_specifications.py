#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_core.test_specifications
==========================================

Tests for the `khimera.core.specifications` module.

See Also
--------
khimera.core.specifications
"""
import pytest

from khimera.core.components import Component
from khimera.core.specifications import FieldSpec


# --- Mock Classes ---------------------------------------------------------------------------------


class MockComponent(Component):
    """Mock subclass of `Component` for testing."""


class MockFieldSpec(FieldSpec[MockComponent]):
    """Mock subclass of `FieldSpec` for testing."""

    COMPONENT_TYPE = MockComponent

    def validate(self, comp: MockComponent) -> bool:
        """Simple validation: return True if name is non-empty."""
        return bool(comp.name)


# ---- Tests for Spec (Abstract Base Class) --------------------------------------------------------


def test_spec_initialization():
    name = "test_spec"
    description = "Test field"
    field = MockFieldSpec(name=name, description=description)
    assert field.name == name
    assert field.description == description


def test_spec_copy():
    """Test creating a deep copy of a `pec` object (via mixin `DeepCopyable`)."""
    name = "test_spec"
    description = "Test field"
    field = MockFieldSpec(name=name, description=description)
    field_copy = field.copy()
    assert field is not field_copy
    assert field.name == field_copy.name
    assert field.description == field_copy.description


def test_spec_equality():
    """Test comparing `Spec` objects by deep comparison (via mixin `DeepComparable`)."""
    name = "test_spec"
    description = "Test field"
    field1 = MockFieldSpec(name=name, description=description)
    field2 = MockFieldSpec(name=name, description=description)
    field3 = MockFieldSpec(name="other_spec", description=description)
    assert field1 == field2
    assert field1 != field3


# --- Tests for FieldSpec -----------------------------------------------------------------------


def test_spec_category():
    field = MockFieldSpec(name="test_spec")
    assert field.category == MockComponent


@pytest.mark.parametrize(
    "required, unique", [(True, False), (False, True), (True, True), (False, False)]
)
def test_category_spec_initialization(required, unique):
    name = "test_spec"
    field = MockFieldSpec(name=name, required=required, unique=unique)
    assert field.name == name
    assert field.required == required
    assert field.unique == unique


@pytest.mark.parametrize("comp_name, expected", [("valid_contrib", True), ("", False)])
def test_category_spec_validation(comp_name, expected):
    field = MockFieldSpec(name="test_spec")
    comp = MockComponent(name=comp_name)
    assert field.validate(comp) == expected
