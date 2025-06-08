"""
test_khimera.test_utils.test_factories
======================================

Tests for the factory functions and classes.

See Also
--------
khimera.utils.factories
"""
# --- Silenced Errors ---
# pylint: disable=unused-variable
#   Test functions are used, but pylint does not detect it.

from abc import ABC, abstractmethod
from typing import Union, List, Type

import pytest

from khimera.utils.factories import TypeConstrainedList, TypeConstrainedDict


# --- Tests for TypeConstrainedList ----------------------------------------------------------------


@pytest.mark.parametrize(
    "value_type, value, expected",
    [
        # Single type constraints
        (int, 1, True),
        (int, 1.1, False),
        (str, "test", True),
        (str, 123, False),
        (float, 1.1, True),
        (float, "1.1", False),
        # List type constraints
        (List[str], ["a", "b", "c"], True),
        (List[str], [1, 2, 3], False),
        # Union type constraints
        (Union[int, float], 1, True),
        (Union[int, float], 1.1, True),
        (Union[int, float], "1.1", False),
        # Complex type constraints
        (Union[str, List[str]], "text", True),
        (Union[str, List[str]], ["a", "b"], True),
        (Union[str, List[str]], [1, 2], False),
        (Union[str, List[str]], 2, False),
        # Edge cases
        (List[int], [], True),  # empty list should still be valid
        (Union[int, List[int]], [], True),
    ],
)
def test_is_valid(value_type, value, expected):
    """
    Test `is_valid` method of `TypeConstrainedList` for various type constraints.

    Arguments
    ---------
    value_type : type
        Type constraint for the list elements.
    value : Any
        Value to check for validity.
    expected : bool
        Expected result of the validity check.

    Notes
    -----
    Test cases:

    - Single type constraints (int, str, float).
    - Union types with valid and invalid values.
    - Lists with various element types (for nested lists).
    - Complex type hints (e.g., Union).
    - Edge cases (empty lists, mixed-type lists).

    Warning
    -------
    Tests might fail if the list elements are mixed types, since the `BeartypeStrategy` randomly
    samples one element of the container to check the type.
    """
    tc_list = TypeConstrainedList(value_type)
    assert tc_list.is_valid(value) == expected


@pytest.mark.parametrize(
    "value_type, initial_data, index, value, expected",
    [
        # Valid single index assignments
        (int, [1, 2, 3], 0, 42, [42, 2, 3]),
        (str, ["a", "b", "c"], 1, "x", ["a", "x", "c"]),
        (float, [1.1, 2.2, 3.3], 2, 4.4, [1.1, 2.2, 4.4]),
        # Invalid single index assignments
        (int, [1, 2, 3], 0, "string", TypeError),
        (str, ["a", "b", "c"], 1, 42, TypeError),
        (float, [1.1, 2.2, 3.3], 2, [4.4], TypeError),
    ],
)
def test_setitem_single_index(value_type, initial_data, index, value, expected):
    """
    Test `__setitem__` method of `TypeConstrainedList` for single index assignments.

    Arguments
    ---------
    value_type : type
        Type constraint for the list elements.
    initial_data : List[Any]
        Initial data for the list.
    index : int
        Index to assign the value to.
    value : Any
        Value to assign to the list.
    expected : List[Any] or TypeError
        Expected list data after the assignment.

    Notes
    -----
    Test cases:

    - Ensures valid values are assigned.
    - Raises TypeError when assigning an invalid value.
    """
    tc_list = TypeConstrainedList(value_type, initial_data)
    if expected == TypeError:
        with pytest.raises(TypeError):
            tc_list[index] = value
    else:
        tc_list[index] = value
        assert tc_list.data == expected


class MockBaseClass(ABC):
    """Mock abstract base class."""

    @abstractmethod
    def mock_method(self) -> str:
        """Abstract method to be implemented by subclasses."""
        pass


class MockConcreteClass(MockBaseClass):
    """Mock concrete class implementing class MockBaseClass(ABC)."""

    def mock_method(self) -> str:
        return "mock"


@pytest.mark.parametrize(
    "value_type, value, expected",
    [
        # Direct instance tests
        (MockConcreteClass, MockConcreteClass(), True),
        (MockConcreteClass, "invalid", False),
        # Abstract base class test
        (MockBaseClass, MockConcreteClass(), True),
        (MockBaseClass, "invalid", False),
        # Subclass tests
        (Type[MockBaseClass], MockConcreteClass, True),
        (Type[MockBaseClass], int, False),
    ],
)
def test_is_valid_custom_types(value_type, value, expected):
    """
    Test `is_valid` method of `TypeConstrainedList` with custom types.

    Arguments
    ---------
    value_type : type
        Type constraint for the list elements.
    value : Any
        Value to check for validity.
    expected : bool
        Expected result of the validity check.

    Notes
    -----
    Test cases:

    - Direct instance checking (isinstance equivalent): a MockConcreteClass instance should be
      valid.
    - Abstract base class validation: a subclass instance should be valid when constrained to base
      class, even if abstract.
    - Subclass validation (issubclass equivalent using `type[MockBaseClass]`): MockConcreteClass
      should be a valid subclass of MockBaseClass.
    """
    tc_list = TypeConstrainedList(value_type)
    assert tc_list.is_valid(value) == expected


@pytest.mark.parametrize(
    "value_type, initial_data, slice_obj, values, expected",
    [
        # Valid slice assignments
        (int, [1, 2, 3, 4], slice(1, 3), [42, 43], [1, 42, 43, 4]),
        (str, ["a", "b", "c", "d"], slice(0, 2), ["x", "y"], ["x", "y", "c", "d"]),
        (float, [1.1, 2.2, 3.3, 4.4], slice(2, 4), [5.5, 6.6], [1.1, 2.2, 5.5, 6.6]),
        # Invalid slice assignments (wrong types)
        (int, [1, 2, 3, 4], slice(1, 3), ["a", "b"], TypeError),
        (str, ["a", "b", "c", "d"], slice(0, 2), [1, 2], TypeError),
        (float, [1.1, 2.2, 3.3, 4.4], slice(2, 4), [5, "x"], TypeError),
        # Edge case: Assigning an empty slice should not fail
        (int, [1, 2, 3, 4], slice(1, 1), [], [1, 2, 3, 4]),
        # Edge case: Step value in slice assignment
        (int, [1, 2, 3, 4, 5, 6], slice(1, 6, 2), [42, 43, 44], [1, 42, 3, 43, 5, 44]),
    ],
)
def test_setitem_slice(value_type, initial_data, slice_obj, values, expected):
    """
    Test `__setitem__` method of `TypeConstrainedList` for slice assignments.

    Arguments
    ---------
    value_type : type
        Type constraint for the list elements.
    initial_data : List[Any]
        Initial data for the list.
    slice_obj : slice
        Slice object to assign the values to.
    values : List[Any]
        Values to assign to the list.
    expected : List[Any] or TypeError
        Expected list data after the assignment.

    Notes
    -----
    Test cases:

    - Ensures valid lists are assigned to slices.
    - Raises TypeError when assigning a list with invalid values.
    - Edge cases with empty slices and step values in slicing.
    """
    tc_list = TypeConstrainedList(value_type, initial_data)

    if expected == TypeError:
        with pytest.raises(TypeError):
            tc_list[slice_obj] = values
    else:
        tc_list[slice_obj] = values
        assert tc_list.data == expected


@pytest.mark.parametrize(
    "value_type, initial_data, new_value, expected",
    [
        # Valid append operations
        (int, [1, 2, 3], 4, [1, 2, 3, 4]),
        (str, ["a", "b"], "c", ["a", "b", "c"]),
        (float, [1.1, 2.2], 3.3, [1.1, 2.2, 3.3]),
        # Valid with Union type constraints
        (Union[int, float], [1, 2.5], 3, [1, 2.5, 3]),
        (Union[int, float], [1, 2], 3.14, [1, 2, 3.14]),
        (Union[str, List[str]], ["a"], ["b", "c"], ["a", ["b", "c"]]),
        # Edge case: Appending to an empty list
        (int, [], 42, [42]),
        (str, [], "hello", ["hello"]),
        # Edge case: Appending empty values (valid for some types)
        (str, ["x"], "", ["x", ""]),
    ],
)
def test_append_valid(value_type, initial_data, new_value, expected):
    """
    Test `append` method of `TypeConstrainedList` with valid values.

    Arguments
    ---------
    value_type : type
        Type constraint for the list elements.
    initial_data : List[Any]
        Initial data for the list.
    new_value : Any
        Value to append to the list.
    expected : List[Any]
        Expected list data after the append operation.

    Notes
    -----
    Test cases:

    - Ensures valid elements are appended (simple, unions).
    - Edge cases: append to an empty list, append an empty string.
    """
    tc_list = TypeConstrainedList(value_type, initial_data)
    tc_list.append(new_value)
    assert tc_list.data == expected


@pytest.mark.parametrize(
    "value_type, initial_data, new_value",
    [
        # Invalid type assignments
        (int, [1, 2, 3], "string"),
        (str, ["a", "b"], 42),
        (float, [1.1, 2.2], "not a float"),
        # Invalid with Union type constraints
        (Union[int, float], [1, 2.5], "string"),
        (Union[str, List[str]], ["a"], 3.14),
        # Edge case: Appending None
        (int, [1, 2, 3], None),
    ],
)
def test_append_invalid(value_type, initial_data, new_value):
    """
    Test `append` method of `TypeConstrainedList` with invalid values.

    Arguments
    ---------
    value_type : type
        Type constraint for the list elements.
    initial_data : List[Any]
        Initial data for the list.
    new_value : Any
        Value to append to the list.

    Notes
    -----
    Test cases:

    - Ensures TypeError is raised when appending an incorrect type(simple, unions).
    - Edge cases: appending None (should raise TypeError unless explicitly allowed).
    """
    tc_list = TypeConstrainedList(value_type, initial_data)
    with pytest.raises(TypeError):
        tc_list.append(new_value)


@pytest.mark.parametrize(
    "value_type, initial_data, new_values, expected",
    [
        # Valid extend operations
        (int, [1, 2, 3], [4, 5, 6], [1, 2, 3, 4, 5, 6]),
        (str, ["a", "b"], ["c", "d"], ["a", "b", "c", "d"]),
        (float, [1.1, 2.2], [3.3, 4.4], [1.1, 2.2, 3.3, 4.4]),
        # Valid with Union type constraints
        (Union[int, float], [1, 2.5], [3, 4.0], [1, 2.5, 3, 4.0]),
        (Union[str, List[str]], ["a"], [["b", "c"], "d"], ["a", ["b", "c"], "d"]),
        # Edge case: Extending an empty list
        (int, [], [1, 2, 3], [1, 2, 3]),
        (str, [], ["hello", "world"], ["hello", "world"]),
        # Edge case: Extending with an empty iterable
        (int, [1, 2, 3], [], [1, 2, 3]),
        (str, ["a", "b"], [], ["a", "b"]),
        # Edge case: Appending empty strings (valid for str type)
        (str, ["x"], [""], ["x", ""]),
    ],
)
def test_extend_valid(value_type, initial_data, new_values, expected):
    """
    Test `extend` method of `TypeConstrainedList` with valid values.

    Arguments
    ---------
    value_type : type
        Type constraint for the list elements.
    initial_data : List[Any]
        Initial data for the list.
    new_values : List[Any]
        Values to extend the list with.
    expected : List[Any]
        Expected list data after the extend operation.

    Notes
    -----
    Test cases:

    - Ensures valid elements are extended (simple, unions).
    - Edge cases: extend an initially empty list, extend with an empty iterable (should not change
      list), extend with empty strings (valid for str type).
    """
    tc_list = TypeConstrainedList(value_type, initial_data)
    tc_list.extend(new_values)
    assert tc_list.data == expected


@pytest.mark.parametrize(
    "value_type, initial_data, new_values",
    [
        # Invalid type assignments
        (int, [1, 2, 3], ["string"]),  # strings in an int-constrained list
        (str, ["a", "b"], [42]),  # integer in a string-constrained list
        (float, [1.1, 2.2], ["not a float"]),  # String in a float-constrained list
        # Invalid with Union type constraints
        (Union[int, float], [1, 2.5], ["string"]),  # string in an int/float list
        (Union[str, List[str]], ["a"], [3.14]),  # float in a str/List[str] list
        # Edge case: Extending with None
        (int, [1, 2, 3], None),
    ],
)
def test_extend_invalid(value_type, initial_data, new_values):
    """
    Test `extend` method of `TypeConstrainedList` with invalid values.

    Arguments
    ---------
    value_type : type
        Type constraint for the list elements.
    initial_data : List[Any]
        Initial data for the list.
    new_values : List[Any]
        Values to extend the list with.

    Notes
    -----
    Test cases:

    - Ensures TypeError is raised when extending with incorrect types.
    - Edge cases: extend with None (should raise TypeError unless explicitly allowed).
    """
    tc_list = TypeConstrainedList(value_type, initial_data)
    with pytest.raises(TypeError):
        tc_list.extend(new_values)


@pytest.mark.parametrize(
    "value_type, initial_data, expected",
    [
        # Valid initializations
        (int, [1, 2, 3], [1, 2, 3]),
        (str, ["a", "b", "c"], ["a", "b", "c"]),
        (float, [1.1, 2.2, 3.3], [1.1, 2.2, 3.3]),
        # Valid with Union type constraints
        (Union[int, float], [1, 2.5, 3], [1, 2.5, 3]),
        (Union[str, List[str]], ["a", ["b", "c"]], ["a", ["b", "c"]]),
        # Edge case: Initializing an empty list
        (int, [], []),
        (str, [], []),
        (Union[int, float], [], []),
        # Edge case: Deeply nested lists
        (List[int], [[1, 2], [3, 4]], [[1, 2], [3, 4]]),
    ],
)
def test_init_list_valid(value_type, initial_data, expected):
    """
    Test initialization of `TypeConstrainedList` with valid initial data.

    Arguments
    ---------
    value_type : type
        Type constraint for the list elements.
    initial_data : List[Any]
        Initial data for the list.
    expected : List[Any]
        Expected list data after initialization.

    Notes
    -----
    Test cases:

    - Ensures that elements conform to the type constraint.
    - Edge cases: initializing with an empty list, initializing with deeply nested lists (valid when
      explicitly allowed).
    """
    tc_list = TypeConstrainedList(value_type, initial_data)
    assert tc_list.data == expected


@pytest.mark.parametrize(
    "value_type, initial_data",
    [
        # Invalid type assignments
        (int, [1, 2, "three"]),  # string in an int-constrained list
        (str, ["a", "b", 42]),  # integer in a string-constrained list
        (float, [1.1, 2.2, "not a float"]),  # string in a float-constrained list
        # Invalid with Union type constraints
        (Union[int, float], [1, 2.5, "string"]),  # string in an int/float list
        (Union[str, List[str]], ["a", 3.14]),  # float in a str/List[str] list
        # Edge case: None in a list that does not allow it
        (int, [1, 2, None]),
    ],
)
def test_init_list_invalid(value_type, initial_data):
    """
    Test initialization of `TypeConstrainedList` with invalid initial data.

    Arguments
    ---------
    value_type : type
        Type constraint for the list elements.
    initial_data : List[Any]
        Initial data for the list.

    Notes
    -----
    Test cases:

    - Ensures that a `TypeError` is raised when initial data contains incorrect types.
    - Edge cases: initializing with `None` (should raise `TypeError` unless explicitly allowed).
    """
    with pytest.raises(TypeError):
        TypeConstrainedList(value_type, initial_data)


# --- Tests for TypeConstrainedDict ----------------------------------------------------------------


@pytest.mark.parametrize(
    "key_type, value_type, initial_data, expected",
    [
        # Valid initializations
        (str, int, {"a": 1, "b": 2}, {"a": 1, "b": 2}),
        (int, str, {1: "one", 2: "two"}, {1: "one", 2: "two"}),
        (Union[str, int], float, {"a": 1.1, 2: 2.2}, {"a": 1.1, 2: 2.2}),
        # Empty dictionary case
        (str, int, {}, {}),
    ],
)
def test_init_dict_valid(key_type, value_type, initial_data, expected):
    """Test initialization of `TypeConstrainedDict` with valid initial data."""
    tc_dict = TypeConstrainedDict(key_type, value_type, initial_data)
    assert tc_dict.data == expected


@pytest.mark.parametrize(
    "key_type, value_type, initial_data",
    [
        (str, int, {"a": 1, 2: 2}),  # Invalid key type (int)
        (int, str, {1: "one", "two": "two"}),  # Invalid key type (str)
        (str, int, {"a": "1"}),  # Invalid value type (str instead of int)
    ],
)
def test_init_dict_invalid(key_type, value_type, initial_data):
    """Test initialization of `TypeConstrainedDict` with invalid initial data."""
    with pytest.raises(TypeError):
        TypeConstrainedDict(key_type, value_type, initial_data)


@pytest.mark.parametrize(
    "key_type, value_type, key, value, expected",
    [
        (str, int, "c", 3, {"a": 1, "b": 2, "c": 3}),
        (int, str, 3, "three", {1: "one", 2: "two", 3: "three"}),
    ],
)
def test_setitem_valid(key_type, value_type, key, value, expected):
    """Test `__setitem__` method of `TypeConstrainedDict` with valid key-value pairs."""
    tc_dict = TypeConstrainedDict(
        key_type, value_type, {"a": 1, "b": 2} if key_type == str else {1: "one", 2: "two"}
    )
    tc_dict[key] = value
    assert tc_dict.data == expected


@pytest.mark.parametrize(
    "key_type, value_type, key, value",
    [
        (str, int, 3, 3),  # Invalid key type (int instead of str)
        (int, str, "c", "three"),  # Invalid key type (str instead of int)
        (str, int, "c", "three"),  # Invalid value type (str instead of int)
    ],
)
def test_setitem_invalid(key_type, value_type, key, value):
    """Test `__setitem__` method of `TypeConstrainedDict` with invalid key-value pairs."""
    tc_dict = TypeConstrainedDict(key_type, value_type)
    with pytest.raises(TypeError):
        tc_dict[key] = value


@pytest.mark.parametrize(
    "key_type, value_type, initial_data, update_data, expected",
    [
        # Updating with a dictionary
        (str, int, {"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        (int, str, {1: "one"}, {2: "two"}, {1: "one", 2: "two"}),
        # Updating with an iterable of key-value pairs
        (str, int, {"a": 1}, [("b", 2)], {"a": 1, "b": 2}),
        (int, str, {1: "one"}, [(2, "two")], {1: "one", 2: "two"}),
        # Updating with keyword arguments
        (str, int, {"a": 1}, {}, {"a": 1}),  # No-op
    ],
)
def test_update_valid(key_type, value_type, initial_data, update_data, expected):
    """Test `update`  method of `TypeConstrainedDict` with valid key-value pairs."""
    tc_dict = TypeConstrainedDict(key_type, value_type, initial_data)
    tc_dict.update(update_data)
    assert tc_dict.data == expected


@pytest.mark.parametrize(
    "key_type, value_type, update_data",
    [
        (str, int, {3: 2}),  # Invalid key type
        (int, str, {"c": "three"}),  # Invalid key type
        (str, int, {"c": "three"}),  # Invalid value type
        (str, int, [(3, 2)]),  # Invalid key type in iterable
    ],
)
def test_update_invalid(key_type, value_type, update_data):
    """Test `update` method of `TypeConstrainedDict` with invalid key-value pairs."""
    tc_dict = TypeConstrainedDict(key_type, value_type, {"a": 1} if key_type == str else {1: "one"})
    with pytest.raises(TypeError):
        tc_dict.update(update_data)
