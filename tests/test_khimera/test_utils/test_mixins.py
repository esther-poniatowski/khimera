"""
test_khimera.test_utils.test_mixins
===================================

Tests for the mixin classes for common functionality in custom classes and objects with nested
components.

See Also
--------
khimera.utils.mixins
"""
# --- Silenced Errors ---
# pylint: disable=unused-variable
#   Test functions are used, but pylint does not detect it.
# pylint: disable=unused-import
#   Importing pytest is necessary for the tests.

import pytest

from khimera.utils.mixins import DeepCopyable, DeepComparable


# --- Mock Class for Testing Mixins ----------------------------------------------------------------


class NestedObject(DeepCopyable, DeepComparable):
    """Class for testing mixins with nested objects."""

    def __init__(self, value):
        self.value = value


class TestClass(DeepCopyable, DeepComparable):
    """Class which uses the DeepCopyable, DeepComparable, and DeepHashable mixins."""

    def __init__(self, nested, *args):
        self.mutable = [*args]
        self.nested = nested


# --- Tests for DeepCopyable -----------------------------------------------------------------------


def test_deep_copyable():
    """
    Test the `DeepCopyable` mixin.

    Expected Behavior:

    - The deep copy should be a new object, with a new mutable object and a new nested object.
    - The deep copy should have the same values as the original object.
    """
    old = TestClass(NestedObject(1), 1, 2, 3)
    new = old.copy()
    assert old is not new
    assert old.mutable is not new.mutable
    assert old.nested is not new.nested
    assert old.mutable == new.mutable
    assert old.nested.value == new.nested.value


# --- Tests for DeepComparable ---------------------------------------------------------------------


def test_deep_comparable():
    """
    Test the `DeepComparable` mixin.

    Expected Behavior:

    - The equality operators should be available.
    - It should return True for objects with the same values and False for objects with different
      values.
    """
    obj1 = TestClass(NestedObject(1), 1, 2, 3)
    obj2 = TestClass(NestedObject(1), 1, 2, 3)
    obj3 = TestClass(NestedObject(2), 1, 2, 3)
    assert obj1 == obj2
    assert obj1 != obj3
