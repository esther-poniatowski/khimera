"""
khimera.utils.mixins
====================

Mixin classes for common functionality in custom classes and objects with nested components.

Classes
-------
DeepCopyable
    Mixin class for creating deep copies of objects.
DeepComparable
    Mixin class for comparing objects by deep comparison.
"""
import copy
from typing import Self

from deepdiff import DeepDiff


class DeepCopyable:
    """
    Mixin class for creating deep copies of objects.

    Methods
    -------
    copy() -> Self
        Create a deep copy of the object.

    See Also
    --------
    copy.deepcopy
    """

    def copy(self) -> Self:
        """Create a deep copy of the object, creating copies of all its nested components."""
        return copy.deepcopy(self)


class DeepComparable:
    """
    Mixin class for comparing objects by deep comparison.

    Methods
    -------
    __eq__(other: Self) -> bool
        Compare the object with another object by deep comparison.

    See Also
    --------
    deepdiff.DeepDiff
    """

    def __eq__(self, other):
        """Compare the object with another object by deep comparison."""
        if not isinstance(other, self.__class__):
            return False
        diff = DeepDiff(self.__dict__, other.__dict__, ignore_order=True)
        return not diff  # True if no differences
