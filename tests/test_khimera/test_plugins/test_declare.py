"""
test_khimera.test_plugins.test_declare
======================================

Tests for the declaration of plugin models.

See Also
--------
khimera.plugins.declare
"""
# --- Silenced Errors ---
# pylint: disable=unused-variable
#   Test functions are used, but pylint does not detect it.

from typing import Callable

import pytest
import pytest_mock

from khimera.plugins.declare import PluginModel
from khimera.core.components import Component  # mocked
from khimera.core.specifications import FieldSpec  # mocked
from khimera.core.dependencies import DependencySpec  # mocked


# --- Mock classes for testing ---------------------------------------------------------------------


class MockComponent(Component):
    """Mock component subclass to test the `filter` method, used as the `COMPONENT_TYPE` attribute
    of the mocked `FieldSpec` class."""


def mock_field_spec(
    mocker: pytest_mock.MockFixture,
    name="test_spec",
    unique=False,
    required=False,
):
    """
    Create a mock `FieldSpec` class with attributes used by the plugin model:

    - `name` (str): Name of the field specification.
    - `unique` (bool): Whether the field is unique.
    - `required` (bool): Whether the field is required.
    - `COMPONENT_TYPE` (Component): Mocked component type (class attribute).


    Arguments
    ---------
    mocker : pytest_mock.MockFixture
        Pytest-mock fixture.
    name : str, default="test_spec"
        Name of the field specification.
    unique : bool
        Whether the field is unique.
    required : bool
        Whether the field is required.
    """
    field_spec = mocker.Mock(spec=FieldSpec)
    field_spec.configure_mock(
        name=name,
        unique=unique,
        required=required,
        COMPONENT_TYPE=MockComponent,
    )
    return field_spec


def mock_dependency_spec(mocker: pytest_mock.MockFixture, name="test_dep"):
    """Create a mock `DependencySpec` class."""
    dependency_spec = mocker.Mock(spec=DependencySpec)
    dependency_spec.configure_mock(name=name)
    return dependency_spec


# --- Tests for PluginModel ------------------------------------------------------------------------


def test_plugin_model_initialization():
    """Test initialization of PluginModel."""
    name = "test_model"
    version = "1.0.0"
    model = PluginModel(name=name, version=version)
    assert model.name == name
    assert model.version == version
    assert not model.fields  # empty list
    assert not model.dependencies  # empty list


@pytest.mark.parametrize(
    "spec_factory, spec_name, spec_attr",
    [(mock_field_spec, "test_spec", "fields"), (mock_dependency_spec, "test_dep", "dependencies")],
)
def test_add_spec(
    spec_factory: Callable,
    spec_name: str,
    spec_attr: str,
    mocker: pytest_mock.MockFixture,
):
    """
    Test adding a specification to a plugin model.

    Arguments
    ---------
    spec_factory :
        Utility function to use to mock the desired specification class.
    spec_name : str
        Name of the specification to add, which should be used as a key in the model.
    spec_attr : str
        Name of the attribute to which the specification should be added: "fields" for a `FieldSpec`
        and "dependencies" for a `DependencySpec`.
    """
    model = PluginModel(name="test_model")
    spec = spec_factory(mocker, name=spec_name)
    model.add(spec)
    assert spec_name in getattr(model, spec_attr)
    assert getattr(model, spec_attr)[spec_name] == spec


def test_add_duplicate_spec(mocker: pytest_mock.MockFixture):
    """Test adding a duplicate specification to a plugin model."""
    model = PluginModel(name="test_model")
    spec = mock_field_spec(mocker)
    model.add(spec)
    with pytest.raises(KeyError):
        model.add(spec)


def test_add_invalid_spec():
    """Test adding an invalid specification to a plugin model."""
    model = PluginModel(name="test_model")
    with pytest.raises(TypeError):
        model.add("not a spec")


def test_all_specs_property(mocker: pytest_mock.MockFixture):
    """Test the `specs` property of a plugin model."""
    field_name = "field_spec"
    dep_name = "dep_spec"
    model = PluginModel(name="test_model")
    field_spec = mock_field_spec(mocker, name=field_name)
    dep_spec = mock_dependency_spec(mocker, name=dep_name)
    model.add(field_spec)
    model.add(dep_spec)
    specs = model.specs
    assert len(specs) == 2
    assert field_name in specs and dep_name in specs


@pytest.mark.parametrize(
    "spec_factory, spec_name, spec_attr",
    [(mock_field_spec, "test_spec", "fields"), (mock_dependency_spec, "test_dep", "dependencies")],
)
def test_remove_spec(
    spec_factory: Callable, spec_name: str, spec_attr: str, mocker: pytest_mock.MockFixture
):
    """
    Test removing a specification from a plugin model.

    Arguments
    ---------
    spec_factory : Type[Spec]
        Utility function to use to mock the desired specification class.
    spec_name : str
        Name of the specification to add.
    spec_attr : str
        Name of the attribute to which the specification should be added.
    """
    model = PluginModel(name="test_model")
    spec = spec_factory(mocker, name=spec_name)
    model.add(spec)
    model.remove(spec_name)
    assert spec_name not in getattr(model, spec_attr)


def test_remove_nonexistent_spec():
    """Test removing a nonexistent specification from a plugin model."""
    model = PluginModel(name="test_model")
    with pytest.raises(KeyError):
        model.remove("nonexistent")


def test_get_existing_spec(mocker: pytest_mock.MockFixture):
    """Test getting an existing specification from a plugin model."""
    name = "test_spec"
    model = PluginModel(name="test_model")
    spec = mock_field_spec(mocker, name=name)
    model.add(spec)
    assert model.get(name) == spec


def test_get_nonexistent_spec():
    """Test getting a nonexistent specification from a plugin model."""
    model = PluginModel(name="test_model")
    assert model.get("nonexistent") is None


def test_filter_by_category(mocker: pytest_mock.MockFixture):
    """Test filtering fields by category."""
    model = PluginModel(name="test_model")
    spec1 = mock_field_spec(mocker, name="spec1")
    spec2 = mock_field_spec(mocker, name="spec2")
    model.add(spec1)
    model.add(spec2)
    filtered = model.filter(category=MockComponent)
    assert len(filtered) == 2
    assert "spec1" in filtered and "spec2" in filtered


def test_filter_by_unique(mocker: pytest_mock.MockFixture):
    """Test filtering fields by uniqueness."""
    model = PluginModel(name="test_model")
    spec1 = mock_field_spec(mocker, name="spec1", unique=True)
    spec2 = mock_field_spec(mocker, name="spec2", unique=False)
    model.add(spec1)
    model.add(spec2)
    filtered = model.filter(unique=True)
    assert len(filtered) == 1
    assert "spec1" in filtered


def test_filter_by_required(mocker: pytest_mock.MockFixture):
    """Test filtering fields by requirement."""
    model = PluginModel(name="test_model")
    spec1 = mock_field_spec(mocker, name="spec1", required=True)
    spec2 = mock_field_spec(mocker, name="spec2", required=False)
    model.add(spec1)
    model.add(spec2)
    filtered = model.filter(required=True)
    assert len(filtered) == 1
    assert "spec1" in filtered


def test_filter_with_custom_filter(mocker: pytest_mock.MockFixture):
    """Test filtering fields with a custom filter function."""
    model = PluginModel(name="test_model")
    spec1 = mock_field_spec(mocker, name="spec1")
    spec2 = mock_field_spec(mocker, name="spec2")
    model.add(spec1)
    model.add(spec2)

    def custom_filter(field: FieldSpec) -> bool:
        return field.name == "spec1"

    filtered = model.filter(custom_filter=custom_filter)
    assert len(filtered) == 1
    assert "spec1" in filtered


def test_method_chaining(mocker: pytest_mock.MockFixture):
    """Test method chaining in PluginModel."""
    model = PluginModel(name="test_model")
    spec1 = mock_field_spec(mocker, name="spec1")
    spec2 = mock_field_spec(mocker, name="spec2")
    model.add(spec1).add(spec2).remove("spec1")
    assert "spec1" not in model.fields
    assert "spec2" in model.fields


def test_copy(mocker: pytest_mock.MockFixture):
    """Test copying a plugin model (via the `DeepCopyable` mixin)."""
    model = PluginModel(name="test_model")
    spec1 = mock_field_spec(mocker, name="spec1")
    model.add(spec1)
    copy = model.copy()
    assert model is not copy
    assert model.name == copy.name
    assert model.version == copy.version
    for f, c in zip(model.fields.values(), copy.fields.values()):
        assert f.name == c.name
    for d, c in zip(model.dependencies.values(), copy.dependencies.values()):
        assert d.name == c.name


def test_equality(mocker: pytest_mock.MockFixture):
    """Test equality of plugin models (via the `DeepComparable` mixin)."""
    model1 = PluginModel(name="test_model")
    model2 = PluginModel(name="test_model")
    assert model1 == model2
    spec1 = mock_field_spec(mocker, name="spec1")
    model1.add(spec1)
    assert model1 != model2
    model2.add(spec1)
    assert model1 == model2
