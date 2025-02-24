#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_components.test_core
=========================================

Tests for the core component and specification classes.

See Also
--------
khimera.core.core
"""
import pytest

from khimera.core.core import Component, ComponentSet, FieldSpec


# --- Mock Classes ---------------------------------------------------------------------------------


class MockComponent(Component):
    """Mock subclass of `Component` for testing."""

    pass


class MockFieldSpec(FieldSpec[MockComponent]):
    """Mock subclass of `FieldSpec` for testing."""

    COMPONENT_TYPE = MockComponent

    def validate(self, comp: MockComponent) -> bool:
        """Simple validation: return True if name is non-empty."""
        return bool(comp.name)


# --- Tests for Component ----------------------------------------------------------------------------


def test_component_initialization():
    """Test initialization of a `Component` object and its attributes."""
    name = "test_contrib"
    description = "Test component"
    comp = MockComponent(name=name, description=description)
    assert comp.name == name
    assert comp.description == description
    assert comp.plugin is None


def test_component_attach():
    """Test attaching a `Component` object to a plugin."""
    plugin_name = "test_plugin"
    comp = MockComponent(name="test_contrib")
    comp.attach(plugin_name=plugin_name)
    assert comp.plugin == plugin_name


def test_component_category():
    """Test getting the category of a `Component` object."""
    comp = MockComponent(name="test_contrib")
    assert comp.category == MockComponent


def test_component_copy():
    """Test creating a deep copy of a `Component` object (via mixin `DeepCopyable`)."""
    name = "test_contrib"
    description = "Test component"
    comp = MockComponent(name=name, description=description)
    comp_copy = comp.copy()
    assert comp is not comp_copy
    assert comp.name == comp_copy.name
    assert comp.description == comp_copy.description
    assert comp.plugin == comp_copy.plugin


def test_component_equality():
    """Test comparing `Component` objects by deep comparison (via mixin `DeepComparable`)."""
    name = "test_contrib"
    description = "Test component"
    comp1 = MockComponent(name=name, description=description)
    comp2 = MockComponent(name=name, description=description)
    comp3 = MockComponent(name="other_contrib", description=description)
    assert comp1 == comp2
    assert comp1 != comp3


# --- Tests for ComponentSet -----------------------------------------------------------------------


def test_component_set():
    """Test appending and accessing `Component` objects in a `ComponentSet`."""
    name1, name2 = "contrib1", "contrib2"
    component_set = ComponentSet()
    contrib1 = MockComponent(name=name1)
    contrib2 = MockComponent(name=name2)
    component_set.append(contrib1)
    component_set.append(contrib2)
    assert len(component_set) == 2
    assert component_set[0].name == name1
    assert component_set[1].name == name2


def test_component_set_append_invalid():
    """Test appending an invalid object to a `ComponentSet`."""
    component_set = ComponentSet()
    with pytest.raises(TypeError):
        component_set.append(None)


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
