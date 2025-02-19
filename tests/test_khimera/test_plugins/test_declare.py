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
from khimera.contributions.core import Spec, Contrib, CategorySpec, DependencySpec


# --- Mock classes for testing ---------------------------------------------------------------------

class MockContrib(Contrib):
    """Mock contribution class for testing."""
    pass

class MockCategorySpec(CategorySpec):
    """Mock category specification class for testing."""
    CONTRIB_TYPE = MockContrib

    def validate(self, contrib: MockContrib) -> bool:
        """Implement abstract method for validation."""
        return True

class MockDependencySpec(DependencySpec):
    """Mock dependency specification class for testing."""

    def validate(self, contrib1: MockContrib, contrib2: MockContrib) -> bool:
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
    assert len(model.specs) == 0
    assert len(model.dependencies) == 0

@pytest.mark.parametrize("spec_class, spec_name, spec_attr", [
    (MockCategorySpec, "test_spec", "specs"),
    (MockDependencySpec, "test_dep", "dependencies")
])
def test_add_spec(spec_class: Type[Spec], spec_name: str, spec_attr: str):
    """Test adding a specification to a plugin model."""
    model = PluginModel(name="test_model")
    spec = spec_class(name=spec_name)
    model.add(spec)
    assert spec_name in getattr(model, spec_attr)
    assert getattr(model, spec_attr)[spec_name] == spec

def test_add_duplicate_spec():
    """Test adding a duplicate specification to a plugin model."""
    model = PluginModel(name="test_model")
    spec = MockCategorySpec(name="test_spec")
    model.add(spec)
    with pytest.raises(KeyError):
        model.add(spec)

def test_add_invalid_spec():
    """Test adding an invalid specification to a plugin model."""
    model = PluginModel(name="test_model")
    with pytest.raises(TypeError):
        model.add("not a spec")

def test_all_specs_property():
    """Test the all_specs property of a plugin model."""
    model = PluginModel(name="test_model")
    cat_spec = MockCategorySpec(name="cat_spec")
    dep_spec = MockDependencySpec(name="dep_spec")
    model.add(cat_spec)
    model.add(dep_spec)
    all_specs = model.all_specs
    assert len(all_specs) == 2
    assert "cat_spec" in all_specs and "dep_spec" in all_specs

@pytest.mark.parametrize("spec_class, spec_name, spec_attr", [
    (MockCategorySpec, "test_spec", "specs"),
    (MockDependencySpec, "test_dep", "dependencies")
])
def test_remove_spec(spec_class: Type[Spec], spec_name: str, spec_attr: str):
    """Test removing a specification from a plugin model."""
    model = PluginModel(name="test_model")
    spec = spec_class(name=spec_name)
    model.add(spec)
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
    spec = MockCategorySpec(name=name)
    model.add(spec)
    assert model.get(name) == spec

def test_get_nonexistent_spec():
    """Test getting a nonexistent specification from a plugin model."""
    model = PluginModel(name="test_model")
    assert model.get("nonexistent") is None

def test_filter_by_category():
    """Test filtering specs by category."""
    model = PluginModel(name="test_model")
    spec1 = MockCategorySpec(name="spec1")
    spec2 = MockCategorySpec(name="spec2")
    model.add(spec1)
    model.add(spec2)
    filtered = model.filter(category=MockContrib)
    assert len(filtered) == 2
    assert "spec1" in filtered and "spec2" in filtered

def test_filter_by_unique():
    """Test filtering specs by uniqueness."""
    model = PluginModel(name="test_model")
    spec1 = MockCategorySpec(name="spec1", unique=True)
    spec2 = MockCategorySpec(name="spec2", unique=False)
    model.add(spec1)
    model.add(spec2)
    filtered = model.filter(unique=True)
    assert len(filtered) == 1
    assert "spec1" in filtered

def test_filter_by_required():
    """Test filtering specs by requirement."""
    model = PluginModel(name="test_model")
    spec1 = MockCategorySpec(name="spec1", required=True)
    spec2 = MockCategorySpec(name="spec2", required=False)
    model.add(spec1)
    model.add(spec2)
    filtered = model.filter(required=True)
    assert len(filtered) == 1
    assert "spec1" in filtered

def test_filter_with_custom_filter():
    """Test filtering specs with a custom filter function."""
    model = PluginModel(name="test_model")
    spec1 = MockCategorySpec(name="spec1")
    spec2 = MockCategorySpec(name="spec2")
    model.add(spec1)
    model.add(spec2)
    custom_filter = lambda spec: spec.name == "spec1"
    filtered = model.filter(custom_filter=custom_filter)
    assert len(filtered) == 1
    assert "spec1" in filtered

def test_method_chaining():
    """Test method chaining in PluginModel."""
    model = PluginModel(name="test_model")
    spec1 = MockCategorySpec(name="spec1")
    spec2 = MockCategorySpec(name="spec2")
    model.add(spec1).add(spec2).remove("spec1")
    assert "spec1" not in model.specs
    assert "spec2" in model.specs
