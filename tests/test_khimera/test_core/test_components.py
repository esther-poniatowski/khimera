"""
test_khimera.test_core.test_components
======================================

Tests for the `khimera.core.components` module.

See Also
--------
khimera.core.components
"""
# --- Silenced Errors ---
# pylint: disable=unused-variable
#   Test functions are used, but pylint does not detect it.

import pytest

from khimera.core.components import Component, ComponentSet
from khimera.core.specifications import FieldSpec


# --- Mock Classes ---------------------------------------------------------------------------------


class MockComponent(Component):
    """Mock subclass of `Component` for testing."""


class MockFieldSpec(FieldSpec[MockComponent]):
    """Mock subclass of `FieldSpec` for testing."""

    COMPONENT_TYPE = MockComponent

    def validate(self, obj: MockComponent) -> bool:
        """Simple validation: return True if name is non-empty."""
        return bool(obj.name)


# --- Tests for Component --------------------------------------------------------------------------


def test_component_initialization():
    """Test initialization of a `Component` object and its attributes."""
    name = "test_comp"
    description = "Test component"
    comp = MockComponent(name=name, description=description)
    assert comp.name == name
    assert comp.description == description
    assert comp.plugin is None


def test_component_attach():
    """Test attaching a `Component` object to a plugin."""
    plugin_name = "test_plugin"
    comp = MockComponent(name="test_comp")
    comp.attach(plugin_name=plugin_name)
    assert comp.plugin == plugin_name


def test_component_category():
    """Test getting the category of a `Component` object."""
    comp = MockComponent(name="test_comp")
    assert comp.category == MockComponent


def test_component_copy():
    """Test creating a deep copy of a `Component` object (via mixin `DeepCopyable`)."""
    name = "test_comp"
    description = "Test component"
    comp = MockComponent(name=name, description=description)
    comp_copy = comp.copy()
    assert comp is not comp_copy
    assert comp.name == comp_copy.name
    assert comp.description == comp_copy.description
    assert comp.plugin == comp_copy.plugin


def test_component_equality():
    """Test comparing `Component` objects by deep comparison (via mixin `DeepComparable`)."""
    name = "test_comp"
    description = "Test component"
    comp1 = MockComponent(name=name, description=description)
    comp2 = MockComponent(name=name, description=description)
    comp3 = MockComponent(name="other_comp", description=description)
    assert comp1 == comp2
    assert comp1 != comp3


# --- Tests for ComponentSet -----------------------------------------------------------------------


def test_component_set():
    """Test appending and accessing `Component` objects in a `ComponentSet`."""
    name1, name2 = "comp1", "comp2"
    component_set = ComponentSet()
    comp1 = MockComponent(name=name1)
    comp2 = MockComponent(name=name2)
    component_set.append(comp1)
    component_set.append(comp2)
    assert len(component_set) == 2
    assert component_set[0] is comp1
    assert component_set[1] is comp2


def test_component_set_append_invalid():
    """Test appending an invalid object to a `ComponentSet`."""
    component_set = ComponentSet()
    with pytest.raises(TypeError):
        component_set.append(None)
