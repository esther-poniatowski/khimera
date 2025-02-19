#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_components.test_metadata
=============================================

Tests for the component and specification classes for metadata.

See Also
--------
khimera.components.metadata
"""
import pytest
from khimera.components.metadata import MetaData, MetaDataSpec

# --- Tests for Metadata (Component) -----------------------------------------------------------------

def test_metadata_initialization():
    """Test initialization of MetaData."""
    metadata = MetaData(name="test", value="value", description="test description")
    assert metadata.name == "test"
    assert metadata.value == "value"
    assert metadata.description == "test description"

# --- Tests for MetaDataSpec (FieldSpec) --------------------------------------------------------

def test_metadata_spec_initialization():
    """Test initialization of MetaDataSpec."""
    name = "test_spec"
    valid_type = str
    required = True
    unique = False
    description = "test field description"
    metadata_spec = MetaDataSpec(name=name, valid_type=valid_type, required=required, unique=unique, description=description)
    assert metadata_spec.name == name
    assert metadata_spec.valid_type == valid_type
    assert metadata_spec.required == required
    assert metadata_spec.unique == unique
    assert metadata_spec.description == description

def test_metadata_spec_validate_correct_type():
    """Test MetaDataSpec validation with correct type."""
    metadata_spec = MetaDataSpec(name="test_spec", valid_type=str)
    metadata = MetaData(name="test", value="value")
    assert metadata_spec.validate(metadata) is True

def test_metadata_spec_validate_incorrect_type():
    """Test MetaDataSpec validation with incorrect type."""
    metadata_spec = MetaDataSpec(name="test_spec", valid_type=int)
    metadata = MetaData(name="test", value="value")
    assert metadata_spec.validate(metadata) is False
