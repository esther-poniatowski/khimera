#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

from collections import UserDict
import re
from typing import Union, List, Dict, Any

import pytest

from khimera.utils.factories import TypeConstrainedList, TypeConstrainedDict, get_union_types


# --- Type Utilities -------------------------------------------------------------------------------


def test_get_union_types_with_simple_union():
    assert get_union_types(Union[int, str]) == (int, str)


def test_get_union_types_with_complex_union():
    assert get_union_types(Union[List[float], Dict[str, Any]]) == (
        List[float],
        Dict[str, Any],
    )


def test_get_union_types_with_nested_union():
    assert get_union_types(Union[int, Union[str, float]]) == (int, str, float)


def test_get_union_types_with_non_union():
    assert get_union_types(int) is None


def test_get_union_types_with_list():
    assert get_union_types(List[int]) is None


def test_get_union_types_with_dict():
    assert get_union_types(Dict[str, int]) is None


def test_get_union_types_with_any():
    assert get_union_types(Any) is None


# --- Tests for TypeConstrainedList ----------------------------------------------------------------


def test_type_constrained_list_is_valid_type():
    """Test the `is_valid_type` method of TypeConstrainedList."""
    l = TypeConstrainedList(int)
    assert l.is_valid_type(1)
    assert not l.is_valid_type("2")


def test_type_constrained_list_error_message():
    """Test the error_message method of TypeConstrainedList."""
    l = TypeConstrainedList(int)
    assert l.error_message("2") == "Invalid value type: got str instead of int"


def test_type_constrained_list_union_type_error_message():
    """Test the error_message method of TypeConstrainedList with Union type."""
    l = TypeConstrainedList(Union[int, str])
    assert l.error_message(3.0) == "Invalid value type: got float instead of Union[int, str]"


def test_type_constrained_list_init_with_valid_elements():
    """Test initializing TypeConstrainedList with valid elements."""
    l = TypeConstrainedList(int, [1, 2])
    assert l == [1, 2]


def test_type_constrained_list_init_with_invalid_elements():
    """Test initializing TypeConstrainedList with invalid elements."""
    with pytest.raises(TypeError, match="Invalid value type: got str instead of int"):
        TypeConstrainedList(int, [1, "2"])


def test_type_constrained_list_append_valid():
    """Test appending valid elements to TypeConstrainedList."""
    l = TypeConstrainedList(int)
    l.append(1)
    l.append(2)
    assert l == [1, 2]


def test_type_constrained_list_append_invalid():
    """Test appending invalid elements to TypeConstrainedList."""
    l = TypeConstrainedList(int)
    with pytest.raises(TypeError, match="Invalid value type: got str instead of int"):
        l.append("2")


def test_type_constrained_list_union_type():
    """Test TypeConstrainedList with Union type."""
    l = TypeConstrainedList(Union[int, str])
    l.append(1)
    l.append("2")
    assert l == [1, "2"]
    with pytest.raises(
        TypeError, match=re.escape("Invalid value type: got float instead of Union[int, str]")
    ):
        l.append(3.0)


def test_type_constrained_list_extend_valid():
    """Test extending TypeConstrainedList with valid elements."""
    l = TypeConstrainedList(int, [1])
    l.extend([2, 3])
    assert l == [1, 2, 3]


def test_type_constrained_list_extend_invalid():
    """Test extending TypeConstrainedList with invalid elements."""
    l = TypeConstrainedList(int, [1])
    with pytest.raises(TypeError, match="Invalid value type: got str instead of int"):
        l.extend([2, "3"])


def test_type_constrained_list_setitem_valid():
    """Test setting valid items in TypeConstrainedList."""
    l = TypeConstrainedList(int, [1, 2, 3])
    l[1] = 4
    assert l == [1, 4, 3]


def test_type_constrained_list_setitem_invalid():
    """Test setting invalid items in TypeConstrainedList."""
    l = TypeConstrainedList(int, [1, 2, 3])
    with pytest.raises(TypeError, match="Invalid value type: got str instead of int"):
        l[1] = "4"


def test_type_constrained_list_slice_assignment_valid():
    """Test slice assignment with valid items in TypeConstrainedList."""
    l = TypeConstrainedList(int, [1, 2, 3, 4])
    l[1:3] = [5, 6]
    assert l == [1, 5, 6, 4]


def test_type_constrained_list_slice_assignment_invalid():
    """Test slice assignment with invalid items in TypeConstrainedList."""
    l = TypeConstrainedList(int, [1, 2, 3, 4])
    with pytest.raises(TypeError, match="Invalid values, not all of type"):
        l[1:3] = [5, "6"]


# --- Tests for TypeConstrainedDict ----------------------------------------------------------------


def test_type_constrained_dict_is_valid_key_type():
    """Test `is_valid_key_type` method."""
    d = TypeConstrainedDict(Union[str, int], Any)
    assert d.is_valid_key_type("a")
    assert d.is_valid_key_type(1)
    assert not d.is_valid_key_type(1.0)


def test_type_constrained_dict_is_valid_value_type():
    """Test `is_valid_value_type` method."""
    d = TypeConstrainedDict(str, Union[int, str])
    assert d.is_valid_value_type(1)
    assert d.is_valid_value_type("a")
    assert not d.is_valid_value_type(1.0)


def test_type_constrained_dict_error_message():
    """Test error_message method."""
    d = TypeConstrainedDict(str, int)
    assert d.error_message(1.0, int, "value") == "Invalid value type: got float instead of int"
    assert d.error_message("a", int, "key") == "Invalid key type: got str instead of int"


def test_type_constrained_dict_init():
    """Test initialization of TypeConstrainedDict."""
    d = TypeConstrainedDict(str, int)
    assert isinstance(d, UserDict)
    assert d.key_type == str
    assert d.value_type == int
    assert not d  # len(d) == 0


def test_type_constrained_dict_init_with_valid_data():
    """Test initialization of TypeConstrainedDict with initial data."""
    d = TypeConstrainedDict(str, int, {"a": 1, "b": 2})
    assert d == {"a": 1, "b": 2}


def test_type_constrained_dict_init_with_invalid_data():
    """Test initialization of TypeConstrainedDict with invalid initial data."""
    with pytest.raises(TypeError, match="Invalid value type: got str instead of int"):
        TypeConstrainedDict(str, int, {"a": 1, "b": "2"})


def test_type_constrained_dict_setitem_valid():
    """Test setting valid items in TypeConstrainedDict."""
    d = TypeConstrainedDict(str, int)
    d["a"] = 1
    assert d == {"a": 1}


def test_type_constrained_dict_setitem_invalid_key():
    """Test setting items with invalid key type in TypeConstrainedDict."""
    d = TypeConstrainedDict(str, int)
    with pytest.raises(TypeError, match="Invalid key type: got int instead of str"):
        d[1] = 1


def test_type_constrained_dict_setitem_invalid_value():
    """Test setting items with invalid value type in TypeConstrainedDict."""
    d = TypeConstrainedDict(str, int)
    with pytest.raises(TypeError, match="Invalid value type: got str instead of int"):
        d["a"] = "1"


def test_type_constrained_dict_union_type():
    """Test TypeConstrainedDict with Union types."""
    d = TypeConstrainedDict(str, Union[int, str])
    d["a"] = 1
    d["b"] = "2"
    assert d == {"a": 1, "b": "2"}
    with pytest.raises(
        TypeError, match=re.escape("Invalid value type: got float instead of Union[int, str]")
    ):
        d["c"] = 3.0


def test_type_constrained_dict_update_valid():
    """Test updating TypeConstrainedDict with valid items."""
    d = TypeConstrainedDict(str, int)
    d.update({"a": 1, "b": 2})
    assert d == {"a": 1, "b": 2}


def test_type_constrained_dict_update_invalid():
    """Test updating TypeConstrainedDict with invalid items."""
    d = TypeConstrainedDict(str, int)
    with pytest.raises(TypeError, match="Invalid value type: got str instead of int"):
        d.update({"a": 1, "b": "2"})


def test_type_constrained_dict_update_kwargs():
    """Test updating TypeConstrainedDict using keyword arguments."""
    d = TypeConstrainedDict(str, int)
    d.update(a=1, b=2)
    assert d == {"a": 1, "b": 2}


def test_type_constrained_dict_update_with_iterable():
    """Test updating TypeConstrainedDict with an iterable of key-value pairs."""
    d = TypeConstrainedDict(str, int)
    d.update([("a", 1), ("b", 2)])
    assert d == {"a": 1, "b": 2}


def test_type_constrained_dict_update_with_custom_object():
    """Test updating TypeConstrainedDict with a custom object that has a keys method."""

    class CustomDict:
        """Custom dictionary-like object."""

        def keys(self):
            return ["a", "b"]

        def __getitem__(self, key):
            return 1 if key == "a" else 2

    d = TypeConstrainedDict(str, int)
    d.update(CustomDict())
    assert d == {"a": 1, "b": 2}
