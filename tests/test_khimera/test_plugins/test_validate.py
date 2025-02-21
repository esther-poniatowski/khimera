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
from khimera.components.core import ComponentSet # mocked
from khimera.plugins.create import Plugin # mocked


# --- Tests for PluginValidator --------------------------------------------------------------------


@pytest.mark.parametrize("required_fields, plugin_components, expected_missing", [
    ({'required_field': None}, {}, ['required_field']),
    ({'required_field': None}, {'required_field': []}, []),
    ({'field1': None, 'field2': None}, {'field1': []}, ['field2']),
])
def test_check_required(mocker : pytest_mock.MockFixture,
                        required_fields : dict,
                        plugin_components : dict,
                        expected_missing : list
                        ):
    """
    Test if `check_required` correctly identifies missing required fields.

    Arguments
    ---------
    mocker : pytest_mock.MockFixture
        Pytest-mock fixture.
    required_fields : dict
        Dictionary of required fields in the model.
    plugin_components : dict
        Components of the plugin to be validated.
    expected_missing : list
        List of fields expected to be identified as missing.

    Test cases:

    1. Required field is missing.
    2. Required field is present.
    3. Multiple required fields, one is missing.

    Mocking:

    - Plugin model that has required fields (identified via `filter`).
    - Plugin which may or may not have these required fields.

    Notes
    -----
    In the parametric definition, the `FieldSpec` values in the `required_fields` dictionary are set
    to None for simplicity, since they are not involved in the test.
    """
    mock_model = mocker.Mock()
    mock_model.filter.return_value = required_fields
    mock_plugin = mocker.Mock()
    mock_plugin.model = mock_model
    mock_plugin.components = plugin_components

    validator = PluginValidator(mock_plugin)
    validator.check_required()
    assert validator.missing == expected_missing


@pytest.mark.parametrize("unique_fields, plugin_components, expected_not_unique", [
    ({'unique_field': None}, {'unique_field': [1, 2]}, ['unique_field']),
    ({'unique_field': None}, {'unique_field': [1]}, []),
    ({'field1': None, 'field2': None}, {'field1': [1, 2], 'field2': [1]}, ['field1']),
])
def test_check_unique(mocker : pytest_mock.MockFixture,
                      unique_fields :  dict,
                      plugin_components : dict,
                      expected_not_unique: list
                    ):
    """
    Test if `check_unique` correctly identifies non-unique fields.

    Arguments
    ---------
    mocker : pytest_mock.MockFixture
        Pytest-mock fixture.
    unique_fields : dict
        Fields expected to be unique in the model.
    plugin_components : dict
        Components of the plugin to be validated.
    expected_not_unique : list
        Fields expected to be identified as not unique.

    Test cases:

    1. Unique field has multiple components.
    2. Unique field has a single component.
    3. Multiple unique fields, one has multiple components.

    Mocking:

    - Plugin model that has unique fields (identified via `filter`).
    - Plugin which may or may not have multiple components for these unique fields.

    Notes
    -----
    In the parametric definition, the `FieldSpec` values in the `unique_fields` dictionary are set to
    None for simplicity, since they are not involved in the test.
    """
    mock_model = mocker.Mock()
    mock_model.filter.return_value = unique_fields
    mock_plugin = mocker.Mock()
    mock_plugin.model = mock_model
    mock_plugin.get.side_effect = lambda field: plugin_components.get(field, [])

    validator = PluginValidator(mock_plugin)
    validator.check_unique()
    assert validator.not_unique == expected_not_unique


@pytest.mark.parametrize("plugin_components, expected_unknown", [
    ({'known_field': []}, []),
    ({'unknown_field': []}, ['unknown_field']),
    ({'known_field': [], 'unknown_field': []}, ['unknown_field']),
])
def test_check_unknown(mocker : pytest_mock.MockFixture,
                      plugin_components : dict,
                      expected_unknown : list
                      ):
    """
    Test if `check_unknown` correctly identifies unknown fields.

    Arguments
    ---------
    mocker : pytest_mock.MockFixture
        Pytest-mock fixture.
    plugin_components : dict
        Components of the plugin to be validated.
    expected_unknown : list
        List of fields that are expected to be unknown.

    Test cases:

    1. Known field present in the plugin components -> No unknown fields.
    2. Unknown field is present in the plugin components -> One unknown field.
    3. Known and unknown fields present in the plugin components -> One unknown field.

    Mocking:

    - Model with a known field.
    - Plugin with the specified components for the test cases.
    """
    mock_model = mocker.Mock()
    mock_model.fields = {'known_field': mocker.Mock()}
    mock_plugin = mocker.Mock()
    mock_plugin.model = mock_model
    mock_plugin.components = plugin_components

    validator = PluginValidator(mock_plugin)
    validator.check_unknown()
    assert validator.unknown == expected_unknown



@pytest.mark.parametrize("components, model_specs, expected_invalid", [
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
                     components: Dict[str, List[Any]],
                     model_specs: Dict[str, Callable[[Any], bool]],
                     expected_invalid: Dict[str, ComponentSet]):
    """
    Test if `check_rules` correctly identifies invalid components.

    Arguments
    ---------
    mocker : pytest_mock.MockFixture
        Pytest-mock fixture.
    components : dict
        Components in the plugin to be validated.
    model_specs : dict
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
    The `model_specs` dictionary contains validation functions for each field in the model. The
    validation functions are simple lambda functions that return True or False based on the
    component value.

    The `Spec` instances are mocked (using `Mock`) with a `validate` method that return these
    validation functions.

    The model `get` method is mocked (using `side_effect`) to return these `Spec` instances when
    called with a field name.

    Plugin components are mocked as basic types rather than `Component` instances and are stored in
    bare lists rather than `ComponentSet` instances, because those are not relevant to the test.
    """
    mock_model = mocker.Mock()
    mock_specs = {field: mocker.Mock(validate=mocker.Mock(side_effect=func))
                  for field, func in model_specs.items()}
    mock_model.get.side_effect = lambda field: mock_specs[field]
    mock_plugin = mocker.Mock()
    mock_plugin.components = components
    mock_plugin.model = mock_model

    validator = PluginValidator(mock_plugin)
    validator.check_rules()
    # Assert that the invalid components are as expected
    assert validator.invalid == expected_invalid
    # Verify that model.get was called for each field
    assert mock_model.get.call_count == len(components)
    mock_model.get.assert_has_calls([mocker.call(field) for field in components])
    # Verify that validate was called for each component
    for field, contribs in components.items():
        assert mock_specs[field].validate.call_count == len(contribs)


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
    mocker : pytest_mock.MockFixture
        Pytest-mock fixture.
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
    mock_model = mocker.Mock()
    mock_model.dependencies = {
        field: mocker.Mock(validate=mocker.Mock(return_value=validation_results[spec]), __str__=lambda self: spec)
        for field, spec in dependencies.items()
    }
    mock_plugin = mocker.Mock()

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
    mocker : pytest_mock.MockFixture
        Pytest-mock fixture.
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
    - Mock all check methods.
    - Set validator attributes based on `check_results`.
    """
    mock_plugin = mocker.Mock()
    validator = PluginValidator(mock_plugin)
    # Mock all check methods
    mocker.patch.object(validator, 'check_required')
    mocker.patch.object(validator, 'check_unique')
    mocker.patch.object(validator, 'check_unknown')
    mocker.patch.object(validator, 'check_rules')
    mocker.patch.object(validator, 'check_dependencies')
    # Set validator attributes based on check_results
    for attr, value in check_results.items():
        setattr(validator, attr, value)

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
    ---------
    mocker : pytest_mock.MockFixture
        Pytest-mock fixture.
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
    mock_model = mocker.Mock()
    mock_plugin = mocker.Mock(spec=Plugin)
    mock_plugin.model = mock_model
    mock_plugin.copy.return_value = mocker.Mock(spec=Plugin)
    mock_plugin.copy.return_value.components = initial_components.copy()

    validator = PluginValidator(mock_plugin)
    validator.invalid = invalid
    validator.unknown = unknown
    validator.not_unique = not_unique

    result = validator.extract()
    assert result.components == expected_components
    mock_plugin.copy.assert_called_once()
