#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_components.test_core
=========================================

Tests for the core component and specification classes.

See Also
--------
khimera.components.core
"""
import pytest

from khimera.components.core import Component, ComponentSet, FieldSpec


# --- Mock Classes ---------------------------------------------------------------------------------

class MockContrib(Component):
    """Mock subclass of `Component` for testing."""
    pass


class MockFieldSpec(FieldSpec[MockContrib]):
    """Mock subclass of `FieldSpec` for testing."""
    COMPONENT_TYPE = MockContrib

    def validate(self, comp: MockContrib) -> bool:
        """Simple validation: return True if name is non-empty."""
        return bool(comp.name)


# --- Tests for Component ----------------------------------------------------------------------------

def test_contrib_initialization():
    """Test initialization of a `Component` object and its attributes."""
    name = "test_contrib"
    description = "Test component"
    comp = MockContrib(name=name, description=description)
    assert comp.name == name
    assert comp.description == description
    assert comp.plugin is None


def test_contrib_attach():
    """Test attaching a `Component` object to a plugin."""
    plugin_name = "test_plugin"
    comp = MockContrib(name="test_contrib")
    comp.attach(plugin_name=plugin_name)
    assert comp.plugin == plugin_name


def test_contrib_category():
    """Test getting the category of a `Component` object."""
    comp = MockContrib(name="test_contrib")
    assert comp.category == MockContrib


def test_contrib_list():
    """Test appending and accessing `Component` objects in a `ComponentSet`."""
    name1, name2 = "contrib1", "contrib2"
    contrib_list = ComponentSet()
    contrib1 = MockContrib(name=name1)
    contrib2 = MockContrib(name=name2)
    contrib_list.append(contrib1)
    contrib_list.append(contrib2)
    assert len(contrib_list) == 2
    assert contrib_list[0].name == name1
    assert contrib_list[1].name == name2


# ---- Tests for Spec (Abstract Base Class) --------------------------------------------------------

def test_spec_initialization():
    name = "test_spec"
    description = "Test field"
    field = MockFieldSpec(name=name, description=description)
    assert field.name == name
    assert field.description == description


# --- Tests for FieldSpec -----------------------------------------------------------------------

def test_spec_category():
    field = MockFieldSpec(name="test_spec")
    assert field.category == MockContrib


@pytest.mark.parametrize(
    "required, unique",
    [(True, False), (False, True), (True, True), (False, False)]
)
def test_category_spec_initialization(required, unique):
    name = "test_spec"
    field = MockFieldSpec(name=name, required=required, unique=unique)
    assert field.name == name
    assert field.required == required
    assert field.unique == unique


@pytest.mark.parametrize(
    "contrib_name, expected",
    [("valid_contrib", True), ("", False)]
)
def test_category_spec_validation(contrib_name, expected):
    field = MockFieldSpec(name="test_spec")
    comp = MockContrib(name=contrib_name)
    assert field.validate(comp) == expected
