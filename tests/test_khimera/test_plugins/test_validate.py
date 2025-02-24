#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_plugins.test_validate
=======================================

Unit tests for the validation of plugin instances against their models.

See Also
--------
khimera.plugins.validate
"""
from typing import Any, Callable, Dict, List

import pytest
import pytest_mock

from khimera.plugins.validate import PluginValidator
from khimera.components.core import ComponentSet, Component, FieldSpec # mocked
from khimera.plugins.create import Plugin # mocked
from khimera.plugins.declare import PluginModel # mocked


# --- Tests for PluginValidator --------------------------------------------------------------------

@pytest.mark.parametrize("required_fields, plugin_fields, expected_missing", [
    (['required_field'], [], ['required_field']),
    (['required_field'], ['required_field'], []),
    (['required_field1', 'required_field2'], ['required_field1'], ['required_field2']),
])
def test_check_required(mocker : pytest_mock.MockFixture,
                        required_fields : dict,
                        plugin_fields : dict,
                        expected_missing : list
                        ):
    """
    Test if `check_required` correctly identifies missing required fields.

    Arguments
    ---------
    required_fields : List[str]
        Required fields specified in the model.
    plugin_fields : List[str]
        Fields present in the plugin.
    expected_missing : list
        Fields expected to be identified as missing.

    Test cases:

    1. Required field is missing.
    2. Required field is present.
    3. Multiple required fields, one is missing.

    Mocking:

    - Plugin model that has required fields and a `filter` method that returns them.
    - Plugin which may or may not have these required fields.

    Notes
    -----
    In the parametric definition, the `FieldSpec` values in the `required_fields` dictionary are set
    to None for simplicity, since they are not involved in the test.
    """
    # Mock model
    filter_output = {field: mocker.Mock(spec=FieldSpec) for field in required_fields}
    mock_model = mocker.Mock(spec=PluginModel, filter=mocker.Mock(return_value=filter_output))
    # Mock plugin
    components = {field: mocker.Mock(spec=ComponentSet) for field in plugin_fields}
    mock_plugin = mocker.Mock(spec=Plugin, model=mock_model, components=components)
    # Run test
    validator = PluginValidator(mock_plugin)
    validator.check_required()
    assert validator.missing == expected_missing


@pytest.mark.parametrize("unique_fields, component_counts, expected_not_unique", [
    (['unique_field'], [1], []),
    (['unique_field'], [2], ['unique_field']),
    (['field1', 'field2'], [1, 2], ['field2']),
])
def test_check_unique(mocker: pytest_mock.MockFixture,
                      unique_fields: List[str],
                      component_counts: List[int],
                      expected_not_unique: List[str]):
    """
    Test if `check_unique` correctly identifies non-unique fields.

    Arguments
    ---------
    unique_fields : List[str]
        Fields expected to be unique in the model.
    component_counts : List[int]
        Number of components for each field in the plugin to be validated.
    expected_not_unique : List[str]
        Fields expected to be identified as not unique.

    Test cases:

    1. Unique field has a single component.
    2. Unique field has multiple components.
    3. Multiple unique fields, one has multiple components.

    Mocking:

    - Plugin model that has unique fields and a `filter` method that returns them.
    - Plugin which may or may not have multiple components for these unique fields, and a `get`
      method which is called in the `check_unique` method.
    """
    # Mock model
    filter_output = {field: mocker.Mock(spec=FieldSpec) for field in unique_fields}
    mock_model = mocker.Mock(spec=PluginModel, filter=mocker.Mock(return_value=filter_output))
    components = {field: [mocker.Mock(spec=Component) for _ in range(count)]
                  for field, count in zip(unique_fields, component_counts)}
    # Mock plugin
    mock_plugin = mocker.Mock(spec=Plugin, model=mock_model) # no need of ComponentSet
    mock_plugin.get.side_effect = lambda field: components.get(field, [])
    # Run the test
    validator = PluginValidator(mock_plugin)
    validator.check_unique()
    assert validator.not_unique == expected_not_unique


@pytest.mark.parametrize("known_fields, plugin_fields, expected_unknown", [
    (['known_field'], ['known_field'], []),
    (['known_field'], ['unknown_field'], ['unknown_field']),
    (['known_field1'], ['known_field1', 'unknown_field'], ['unknown_field']),
])
def test_check_unknown(mocker: pytest_mock.MockFixture,
                       known_fields: List[str],
                       plugin_fields: List[str],
                       expected_unknown: List[str]):
    """
    Test if `check_unknown` correctly identifies unknown fields.

    Arguments
    ---------
    known_fields : List[str]
        Fields known to the model.
    plugin_fields : List[str]
        Fields present in the plugin.
    expected_unknown : List[str]
        Fields that are expected to be unknown.

    Test cases:

    1. Known field present in the plugin fields -> No unknown fields.
    2. Unknown field is present in the plugin fields -> One unknown field.
    3. Known and unknown fields present in the plugin fields -> One unknown field.

    Mocking:

    - Model with known fields.
    - Plugin with the specified fields for the test cases.
    """
    # Mock model
    fields = {field: mocker.Mock(spec=FieldSpec) for field in known_fields}
    mock_model = mocker.Mock(spec=PluginModel, fields=fields)
    # Mock plugin
    components = {field: mocker.Mock(spec=ComponentSet) for field in plugin_fields}
    mock_plugin = mocker.Mock(spec=Plugin, model=mock_model, components=components)
    # Run the test
    validator = PluginValidator(mock_plugin)
    validator.check_unknown()
    assert validator.unknown == expected_unknown



@pytest.mark.parametrize("component_values, validate_func, expected_invalid", [
    (
        {"field1": [1, 2, 3]},
        {"field1": lambda x: x > 1},
        {"field1": [1]}
    ),
    (
        {"field1": [1, 2, 3], "field2": ["a", "b", "c"]},
        {"field1": lambda x: x > 0, "field2": lambda x: x in ["a", "b"]},
        {"field2": ["c"]}
    ),
    (
        {"field1": [1, 2, 3]},
        {"field1": lambda x: x > 3},
        {"field1": [1, 2, 3]}
    ),
    (
        {"field1": [1, 2, 3]},
        {"field1": lambda x: x > 0},
        {}
    ),
])
def test_check_rules(mocker: pytest_mock.MockFixture,
                     component_values: Dict[str, List[Any]],
                     validate_func: Dict[str, Callable[[Any], bool]],
                     expected_invalid: Dict[str, ComponentSet]):
    """
    Test if `check_rules` correctly identifies invalid components.

    Arguments
    ---------
    component_values : dict
        Values within the components in the plugin to be validated.
    validate_func : dict
        Model specifications for fields (validation functions).
    expected_invalid : dict
        Expected invalid components after validation.

    Test cases:

    1. Single field with one invalid component.
    2. Multiple fields with one field having an invalid component.
    3. All components in a field are invalid.
    4. All components are valid.

    Mocking:

    - `FieldSpec` instances with the specified validation functions for their `validate` method.
    - Model with the specified field specs and `get` method that returns them.
    - Plugin with the specified components.

    Notes
    -----
    The `validate_func` dictionary contains validation functions for each field in the model. The
    validation functions are simple lambda functions that return True or False based on the
    component value.

    The `Spec` instances are mocked (using `Mock`) with a `validate` method that return these
    validation functions.

    The model `get` method is mocked (using `side_effect`) to return these `Spec` instances when
    called with a field name.

    Plugin components are mocked as basic types (int, str) rather than `Component` instances and are
    stored in bare lists rather than `ComponentSet` instances, because those are not relevant to the
    test.
    """
    # Mock model
    mock_model = mocker.Mock(spec=PluginModel)
    mock_specs = {field: mocker.Mock(validate=mocker.Mock(side_effect=func))
                  for field, func in validate_func.items()}
    mock_model.get.side_effect = lambda field: mock_specs[field]
    # Mock plugin
    components = {}
    for field, values in component_values.items():
        components[field] = component_values[field]
    mock_plugin = mocker.Mock(spec=Plugin, model=mock_model, components=components)
    # Run the test
    validator = PluginValidator(mock_plugin)
    validator.check_rules()
    # Check invalid components as expected
    assert validator.invalid == expected_invalid
    # Check that `model.get` was called for each field
    assert mock_model.get.call_count == len(components)
    mock_model.get.assert_has_calls([mocker.call(field) for field in components])
    # Check `validate` was called for each component
    for field, comps in components.items():
        assert mock_specs[field].validate.call_count == len(comps)


@pytest.mark.parametrize("dependencies, validation_results, expected_unsatisfied", [
    ({"dep1": "spec1", "dep2": "spec2"}, {"spec1": True, "spec2": True}, []),
    ({"dep1": "spec1", "dep2": "spec2"}, {"spec1": False, "spec2": True}, ["dep1"]),
    ({"dep1": "spec1", "dep2": "spec2"}, {"spec1": False, "spec2": False}, ["dep1", "dep2"]),
    ({}, {}, []),
])
def test_check_dependencies(mocker : pytest_mock.MockFixture,
                            dependencies : dict,
                            validation_results : dict,
                            expected_unsatisfied : list
                            ):
    """
    Test if `check_dependencies` correctly identifies unsatisfied dependencies.

    Arguments
    ---------
    dependencies : dict
        Dependencies in the model.
    validation_results : dict
        Validation results for the dependencies.
    expected_unsatisfied : list
        Expected unsatisfied dependencies.

    Test cases:

    1. All dependencies are satisfied.
    2. One dependency is unsatisfied.
    3. All dependencies are unsatisfied.
    4. No dependencies to check.

    Mocking:

    - `DependencySpec` instances with the specified validation results for their `validate` method.
    - Model with the specified dependencies and `get` method that returns them.
    - Plugin with the specified components.
    """
    # Mock model
    mock_model = mocker.Mock(spec=PluginModel)
    mock_model.dependencies = {
        field: mocker.Mock(validate=mocker.Mock(return_value=validation_results[spec]), __str__=lambda self: spec)
        for field, spec in dependencies.items()
    }
    mock_plugin = mocker.Mock(spec=Plugin, model=mock_model)
    # Run the test
    validator = PluginValidator(mock_plugin)
    validator.model = mock_model
    validator.check_dependencies()
    # Assert that the unsatisfied dependencies are as expected
    assert validator.deps_unsatisfied == expected_unsatisfied
    # Verify that validate was called for each dependency
    for field, spec in dependencies.items():
        mock_model.dependencies[field].validate.assert_called_once_with(mock_plugin)


@pytest.mark.parametrize("check_results, expected_validity", [
    ({}, True),
    ({"missing": ["field1"]}, False),
    ({"unknown": ["field2"]}, False),
    ({"not_unique": ["field3"]}, False),
    ({"invalid": {"field4": [1, 2]}}, False),
    ({"deps_unsatisfied": ["dep1"]}, False),
    ({"missing": ["field1"], "unknown": ["field2"], "not_unique": ["field3"],
      "invalid": {"field4": [1, 2]}, "deps_unsatisfied": ["dep1"]}, False),
])
def test_validate(mocker : pytest_mock.MockFixture,
                  check_results : dict,
                  expected_validity : bool
                  ):
    """
    Test if `validate` correctly validates a plugin instance.

    Arguments
    ---------
    check_results : dict
        Results of the individual checks.
    expected_validity : bool
        Expected validity of the plugin instance.

    Test cases:

    1. No issues found.
    2. Missing field.
    3. Unknown field.
    4. Non-unique field.
    5. Invalid field.
    6. Unsatisfied dependency.
    7. All issues combined.

    Mocking:

    - Plugin with the specified components.
    - Mock all check methods that are called in `validate`.
    - Set validator attributes based on `check_results`.
    """
    # Mock plugin
    mock_plugin = mocker.Mock(spec=Plugin, model=mocker.Mock(spec=PluginModel))
    # Mock all check methods
    validator = PluginValidator(mock_plugin)
    mocker.patch.object(validator, 'check_required')
    mocker.patch.object(validator, 'check_unique')
    mocker.patch.object(validator, 'check_unknown')
    mocker.patch.object(validator, 'check_rules')
    mocker.patch.object(validator, 'check_dependencies')
    # Set validator attributes based on `check_results`
    for attr, value in check_results.items():
        setattr(validator, attr, value)
    # Run the test
    result = validator.validate()
    assert result == expected_validity
    # Verify that all check methods were called
    validator.check_required.assert_called_once()
    validator.check_unique.assert_called_once()
    validator.check_unknown.assert_called_once()
    validator.check_rules.assert_called_once()
    validator.check_dependencies.assert_called_once()


@pytest.mark.parametrize("initial_components, invalid, unknown, not_unique, expected_components", [
    (
        {"valid": [1, 2], "invalid": [3, 4], "unknown": [5], "not_unique": [6, 7]},
        {"invalid": [3, 4]},
        ["unknown"],
        ["not_unique"],
        {"valid": [1, 2], "not_unique": [6]}
    ),
    (
        {"valid": [1, 2]},
        {},
        [],
        [],
        {"valid": [1, 2]}
    ),
    (
        {"invalid": [1, 2], "unknown": [3], "not_unique": [4, 5]},
        {"invalid": [1, 2]},
        ["unknown"],
        ["not_unique"],
        {"not_unique": [4]}
    )
])
def test_extract(mocker, initial_components, invalid, unknown, not_unique, expected_components):
    """
    Test if `extract` correctly extracts valid components from a plugin instance.

    Arguments
    ---------.
    initial_components : dict
        Initial components in the plugin.
    invalid : dict
        Invalid components.
    unknown : list
        Unknown fields.
    not_unique : list
        Non-unique fields.
    expected_components : dict
        Expected components after extraction.

    Test cases:

    1. All types of issues present.
    2. No issues present.
    3. Only one type of issue present.

    Mocking:

    - Plugin with the specified components.
    - Mock `copy` method of the plugin.
    """
    # Mock model and plugin
    mock_model = mocker.Mock(spec=PluginModel)
    mock_plugin = mocker.Mock(spec=Plugin)
    mock_plugin.model = mock_model
    mock_plugin.copy.return_value = mocker.Mock(spec=Plugin)
    mock_plugin.copy.return_value.components = initial_components.copy()
    # Mock internal attributes
    validator = PluginValidator(mock_plugin)
    validator.invalid = invalid
    validator.unknown = unknown
    validator.not_unique = not_unique
    # Run the test
    result = validator.extract()
    assert result.components == expected_components
    mock_plugin.copy.assert_called_once()
