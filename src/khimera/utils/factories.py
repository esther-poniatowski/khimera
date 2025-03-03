#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.utils.factories
=======================

Utility classes and functions for creating default objects.

Warning
-------
When using `VT` as a generic type in `Type[VT]`, it is assumed to represent a *concrete* class.
Abstract base classes (ABCs) do not qualify because they are not instantiable.

See Also
--------
beartype.door.is_bearable(obj: object, hint: object) -> bool
    Performs runtime type checking against the specified type hint, including nested structures. It
    checks both the overall structure and the types of the items within that structure.

    It can be safely called in place of the following builtins, with type hints instead of types:

    - `isinstance()`, with the same exact parameters in the same exact order.
    - `issubclass()`, by replacing the superclass(es) to be tested against with `type[{cls}]` type
      hint.

    Strategies: The tradeoff between overhead and completeness is governed by a sampling approach
    for type checking containers. The type-checking strategy (i.e., `BeartypeStrategy`) dictates how
    many items are type-checked at each nesting level of each container.

    - `BeartypeStrategy.01` (default): Constant-time strategy (O(1)), type-checking a single
      randomly selected item of each container.
    - `BeartypeStrategy.0n`: Linear-time strategy (O(n)), type-checking all items of a container.

    Here, the default strategy is used, which implies that containers should have homogeneous
    elements when nested in `TypeConstrainedList` or `TypeConstrainedDict` instances. Erroneous
    mixed types might not be detected.
"""
from collections import UserDict, UserList
from typing import Generic, TypeVar, Optional, Iterable, Any, Dict, Tuple, SupportsIndex, overload

from beartype.door import is_bearable


KT = TypeVar("KT")
"""Type variable for the key type of a dictionary."""

VT = TypeVar("VT")
"""Type variable for the value type of a dictionary or list."""


# --- Type Utilities -------------------------------------------------------------------------------


def error_message(item: Any, expected_type: object, spec: Optional[str] = None) -> str:
    """Generate an error message for an invalid item.

    Arguments
    ---------
    item : Any
        Item to check the type of.
    expected_type : object
        Expected type for the item, under the form of a single type or a complex type hint.
    spec : str, optional
        Specification of the item, used to generate a more informative error message.
    """
    actual_type = type(item).__name__
    expected = (
        expected_type.__name__
        if hasattr(expected_type, "__name__")  # class type
        else str(expected_type)  # complex type hint
    )
    return f"Invalid {spec} type: got {actual_type} instead of {expected}"


# --- Type-Constrained List ------------------------------------------------------------------------


class TypeConstrainedList(UserList[VT], Generic[VT]):
    """
    List subclass that constrains the type of its elements.

    Arguments
    ---------
    value_type : object
        Allowed type(s) for the list elements, under the form of a single type of a complex type
        hint. Multiple types can be allowed using a Union type.
    data : List[VT]
        Underlying list data, inherited from `UserList`.

    Examples
    --------
    Create an empty list constrained to contain only integers:

    >>> l = TypeConstrainedList(int)
    >>> l.append(1)
    >>> l.append('2')
    Traceback (most recent call last):
        ...
    TypeError: Value must be of type int, got str

    Create a type contained list directly populated with elements:

    >>> l = TypeConstrainedList(int, [1, 2, 3])
    >>> l.append(3.0)
    Traceback (most recent call last):
        ...
    TypeError: Value must be of type int, got float

    Allowing multiple types:

    >>> from typing import Union
    >>> l = TypeConstrainedList(Union[int, float], [1, 2.0, 3])

    Allow complex types with expressive type hints:

    >>> from typing import Union
    >>> l = TypeConstrainedList(Union[str, List[str]], ['a', ['b', 'c']])

    See Also
    --------
    collections.UserList
    """

    def __init__(self, value_type: object, data: Iterable[VT] = ()):
        """
        Initialize the list with the type of its elements.

        Arguments
        ---------
        value_type : object
            Expected type(s) or type hint (including Union types) for the list elements.
        data : Iterable[VT], optional
            Initial data to populate the list with.
        """
        self.value_type = value_type
        super().__init__()  # initialize with empty list
        if data:  # populate with initial data
            self.extend(data)

    def is_valid(self, value: Any) -> bool:
        """
        Check if the value is of the correct type, matched against the `value_type` attribute.

        See Also
        --------
        beartype.door.is_bearable(obj: object, hint: object) -> bool
        """
        return is_bearable(value, self.value_type)

    @overload
    def __setitem__(self, key: SupportsIndex, value: VT) -> None: ...

    @overload
    def __setitem__(self, key: slice, value: Iterable[VT]) -> None: ...

    def __setitem__(self, key, value) -> None:
        """
        Override the `list` setter method to constrain the type of the assigned value.

        Arguments
        ---------
        key : Union[SupportsIndex, slice]
            Index or slice to assign the value to.
        value : Union[VT, Iterable[VT]]
            Value to assign to the index or slice.
        """
        if isinstance(key, slice):  # check values in slice
            if not isinstance(value, Iterable):
                raise TypeError("For slice assignment, value must be an iterable")
            for item in value:
                if not self.is_valid(item):
                    raise TypeError(self.error_message(item))
        else:  # check single item
            if not self.is_valid(value):
                raise TypeError(self.error_message(value))
        super().__setitem__(key, value)  # call superclass method

    def append(self, item: VT) -> None:
        """Override the append method of `list` to constrain the type of the appended value."""
        if not self.is_valid(item):
            raise TypeError(self.error_message(item))
        super().append(item)

    def extend(self, other: Iterable[VT]) -> None:
        """Override the extend method of `list` to constrain the types of the extended values."""
        for value in other:
            if not self.is_valid(value):
                raise TypeError(self.error_message(value))
        super().extend(other)

    def error_message(self, item: Any) -> str:
        """Generate an error message for an invalid item."""
        return error_message(item, self.value_type, spec="value")


# --- Type-Constrained Containers ------------------------------------------------------------------


class TypeConstrainedDict(UserDict[KT, VT], Generic[KT, VT]):
    """
    Dictionary subclass that constrains the types of keys and values.

    Arguments
    ---------
    key_type : object
        Allowed type(s) for the dictionary keys, under the form of a single type of a complex type
        hint. Multiple types can be allowed using a Union type.
    value_type : object
        Allowed type(s) for the dictionary values.
    data : Dict[KT, VT]
        Underlying dictionary data, inherited from `UserDict`.

    Examples
    --------
    Create an empty dictionary with string keys and integer values:

    >>> d = TypeConstrainedDict(str, int)
    >>> d['a'] = 1
    >>> d['b'] = '2'
    Traceback (most recent call last):
        ...
    TypeError: Value must be of type int, got str

    Create a dictionary directly populated with elements:

    >>> d = TypeConstrainedDict(str, int, {'a': 1, 'b': 2})
    >>> d['c'] = 3.0
    Traceback (most recent call last):
        ...
    TypeError: Value must be of type int, got float

    Allow multiple types for keys and values:

    >>> from typing import Union
    >>> d = TypeConstrainedDict(Union[str, int], Union[int, float], {'a': 1, 2: 2.0})

    See Also
    --------
    collections.UserDict
    """

    def __init__(self, key_type: object, value_type: object, data: Optional[Dict[KT, VT]] = None):
        """
        Initialize the dictionary with the types of its keys and values.

        Arguments
        ---------
        key_type : object
            Expected type(s) or type hint (including Union types) for the dictionary keys.
        value_type : object
            Expected type(s) or type hint (including Union types) for the dictionary values.
        data : Dict[KT, VT], optional
            Initial data to populate the dictionary with.
        """
        self.key_type = key_type
        self.value_type = value_type
        super().__init__()  # initialize with empty dictionary
        if data:  # populate with initial data
            self.update(data)

    def is_valid_key(self, key: Any) -> bool:
        """
        Check if the key is of the correct type, matched against the `key_type` attribute.

        See Also
        --------
        beartype.door.is_bearable(obj: object, hint: object) -> bool
        """
        return is_bearable(key, self.key_type)

    def is_valid_value(self, value: Any) -> bool:
        """Check if the value is of the correct type, matched against the `value_type` attribute."""
        return is_bearable(value, self.value_type)

    def __setitem__(self, key: KT, value: VT) -> None:
        """Override `dict` setter method to constrain the types of the assigned key and value."""
        if not self.is_valid_key(key):
            raise TypeError(self.error_message_key(key))
        if not self.is_valid_value(value):
            raise TypeError(self.error_message_value(value))
        super().__setitem__(key, value)

    def update(self, other=(), /, **kwargs) -> None:
        """Override `dict` update method to constrain the types of the updated keys and values.

        Arguments
        ---------
        other : Union[Dict[KT, VT], Iterable[Tuple[KT, VT]]], optional
            Dictionary or iterable of key-value pairs to update the dictionary with.
        **kwargs : Dict[KT, VT]
            Key-value pairs to update the dictionary with.

        See Also
        --------
        collections.MutableMapping.update
            Original method documentation, using `overload` to provide various type signatures.
            See mypy issue  #1430.
        """
        keys: Tuple[Any, ...] = ()  # initialize containers for keys and values to check
        values: Tuple[Any, ...] = ()
        if isinstance(other, dict):  # `other` is dict: check types for each (key, value) pair
            keys += tuple(other.keys())
            values += tuple(other.values())
        elif isinstance(other, Iterable):  # `other` is iterable: check types for each pair
            keys += tuple(k for k, _ in other)
            values += tuple(v for _, v in other)
        if kwargs:  # `kwargs` is dict: add keys and values to the existing ones
            keys += tuple(kwargs.keys())
            values += tuple(kwargs.values())
        for key, value in zip(keys, values):
            if not self.is_valid_key(key):
                raise TypeError(self.error_message_key(key))
            if not self.is_valid_value(value):
                raise TypeError(self.error_message_value(value))
        super().update(other, **kwargs)

    def error_message_key(self, item: Any) -> str:
        """Generate an error message for an invalid key."""
        return error_message(item, self.key_type, spec="key")

    def error_message_value(self, item: Any) -> str:
        """Generate an error message for an invalid value."""
        return error_message(item, self.value_type, spec="value")
