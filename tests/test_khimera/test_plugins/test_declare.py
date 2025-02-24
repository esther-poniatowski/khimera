#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_plugins.test_declare
======================================

Tests for the declaration of plugin models.

See Also
--------
khimera.plugins.declare
"""
import pytest
from typing import Type

from khimera.plugins.declare import PluginModel
from khimera.core.core import Spec, Component, FieldSpec
from khimera.core.dependencies import DependencySpec


# --- Mock classes for testing ---------------------------------------------------------------------


class MockComponent(Component):
    """Mock component class for testing."""

    pass


class MockFieldSpec(FieldSpec):
    """Mock category specification class for testing."""

    COMPONENT_TYPE = MockComponent

    def validate(self, comp: MockComponent) -> bool:
        """Implement abstract method for validation."""
        return True


class MockDependencySpec(DependencySpec):
    """Mock dependency specification class for testing."""

    def __init__(self, name: str):
        super().__init__(name=name, fields=["field1", "field2"])

    def validate(self, contrib1: MockComponent, contrib2: MockComponent) -> bool:
        """Implement abstract method for validation."""
        return True


# --- Tests for PluginModel ------------------------------------------------------------------------


def test_plugin_model_initialization():
    """Test initialization of PluginModel."""
    name = "test_model"
    version = "1.0.0"
    model = PluginModel(name=name, version=version)
    assert model.name == name
    assert model.version == version
    assert len(model.fields) == 0
    assert len(model.dependencies) == 0


@pytest.mark.parametrize(
    "spec_class, spec_name, spec_attr",
    [(MockFieldSpec, "test_spec", "fields"), (MockDependencySpec, "test_dep", "dependencies")],
)
def test_add_spec(spec_class: Type[Spec], spec_name: str, spec_attr: str):
    """Test adding a specification to a plugin model."""
    model = PluginModel(name="test_model")
    field = spec_class(name=spec_name)
    model.add(field)
    assert spec_name in getattr(model, spec_attr)
    assert getattr(model, spec_attr)[spec_name] == field


def test_add_duplicate_spec():
    """Test adding a duplicate specification to a plugin model."""
    model = PluginModel(name="test_model")
    field = MockFieldSpec(name="test_spec")
    model.add(field)
    with pytest.raises(KeyError):
        model.add(field)


def test_add_invalid_spec():
    """Test adding an invalid specification to a plugin model."""
    model = PluginModel(name="test_model")
    with pytest.raises(TypeError):
        model.add("not a spec")


def test_all_specs_property():
    """Test the `specs` property of a plugin model."""
    field_name = "field_spec"
    dep_name = "dep_spec"
    model = PluginModel(name="test_model")
    field_spec = MockFieldSpec(name=field_name)
    dep_spec = MockDependencySpec(name=dep_name)
    model.add(field_spec)
    model.add(dep_spec)
    specs = model.specs
    assert len(specs) == 2
    assert field_name in specs and dep_name in specs


@pytest.mark.parametrize(
    "spec_class, spec_name, spec_attr",
    [(MockFieldSpec, "test_spec", "fields"), (MockDependencySpec, "test_dep", "dependencies")],
)
def test_remove_spec(spec_class: Type[Spec], spec_name: str, spec_attr: str):
    """Test removing a specification from a plugin model."""
    model = PluginModel(name="test_model")
    field = spec_class(name=spec_name)
    model.add(field)
    model.remove(spec_name)
    assert spec_name not in getattr(model, spec_attr)


def test_remove_nonexistent_spec():
    """Test removing a nonexistent specification from a plugin model."""
    model = PluginModel(name="test_model")
    with pytest.raises(KeyError):
        model.remove("nonexistent")


def test_get_existing_spec():
    """Test getting an existing specification from a plugin model."""
    name = "test_spec"
    model = PluginModel(name="test_model")
    field = MockFieldSpec(name=name)
    model.add(field)
    assert model.get(name) == field


def test_get_nonexistent_spec():
    """Test getting a nonexistent specification from a plugin model."""
    model = PluginModel(name="test_model")
    assert model.get("nonexistent") is None


def test_filter_by_category():
    """Test filtering fields by category."""
    model = PluginModel(name="test_model")
    spec1 = MockFieldSpec(name="spec1")
    spec2 = MockFieldSpec(name="spec2")
    model.add(spec1)
    model.add(spec2)
    filtered = model.filter(category=MockComponent)
    assert len(filtered) == 2
    assert "spec1" in filtered and "spec2" in filtered


def test_filter_by_unique():
    """Test filtering fields by uniqueness."""
    model = PluginModel(name="test_model")
    spec1 = MockFieldSpec(name="spec1", unique=True)
    spec2 = MockFieldSpec(name="spec2", unique=False)
    model.add(spec1)
    model.add(spec2)
    filtered = model.filter(unique=True)
    assert len(filtered) == 1
    assert "spec1" in filtered


def test_filter_by_required():
    """Test filtering fields by requirement."""
    model = PluginModel(name="test_model")
    spec1 = MockFieldSpec(name="spec1", required=True)
    spec2 = MockFieldSpec(name="spec2", required=False)
    model.add(spec1)
    model.add(spec2)
    filtered = model.filter(required=True)
    assert len(filtered) == 1
    assert "spec1" in filtered


def test_filter_with_custom_filter():
    """Test filtering fields with a custom filter function."""
    model = PluginModel(name="test_model")
    spec1 = MockFieldSpec(name="spec1")
    spec2 = MockFieldSpec(name="spec2")
    model.add(spec1)
    model.add(spec2)

    def custom_filter(field: FieldSpec) -> bool:
        return field.name == "spec1"

    filtered = model.filter(custom_filter=custom_filter)
    assert len(filtered) == 1
    assert "spec1" in filtered


def test_method_chaining():
    """Test method chaining in PluginModel."""
    model = PluginModel(name="test_model")
    spec1 = MockFieldSpec(name="spec1")
    spec2 = MockFieldSpec(name="spec2")
    model.add(spec1).add(spec2).remove("spec1")
    assert "spec1" not in model.fields
    assert "spec2" in model.fields


def test_copy():
    """Test copying a plugin model (via the `DeepCopyable` mixin)."""
    model = PluginModel(name="test_model")
    spec1 = MockFieldSpec(name="spec1")
    model.add(spec1)
    copy = model.copy()
    assert model is not copy
    assert model.name == copy.name
    assert model.version == copy.version
    assert model.fields == copy.fields
    assert model.dependencies == copy.dependencies
    assert model.specs == copy.specs


def test_equality():
    """Test equality of plugin models (via the `DeepComparable` mixin)."""
    model1 = PluginModel(name="test_model")
    model2 = PluginModel(name="test_model")
    assert model1 == model2
    spec1 = MockFieldSpec(name="spec1")
    model1.add(spec1)
    assert model1 != model2
    model2.add(spec1)
    assert model1 == model2
