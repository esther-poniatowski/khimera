#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.utils.factories
=======================

Utility classes and functions for creating default objects.
"""
from collections import UserDict, UserList
from typing import Generic, TypeVar, Type, Union, Optional, Iterable, Any, Dict, Tuple
from typing_extensions import get_origin, get_args


KT = TypeVar("KT")
"""Type variable for the key type of a dictionary."""

VT = TypeVar("VT")
"""Type variable for the value type of a dictionary or list."""


# --- Type Utilities -------------------------------------------------------------------------------


def get_union_types(tp: Type) -> Optional[Tuple[Type, ...]]:
    """
    Get the types of a Union type.

    Arguments
    ---------
    tp : Type
        Type to get the types of.

    Returns
    -------
    Optional[Tuple[Type, ...]]
        All the types if the type is a Union, otherwise None.

    See Also
    --------
    typing.get_origin
        Get the unsubscripted version of a type, which means the original type without any type
        arguments. Here, it is used on the expected type to check if it is a Union type.
    typing.get_args
        Get type arguments with all substitutions performed. For unions, basic simplifications used
        by Union constructor are performed. Here, it is used on the expected type to get the types
        of the Union.

    Examples
    --------
    Get the types of a Union type:

    >>> from typing import Union
    >>> get_union_types(Union[int, str])
    (int, str)

    Get the types of a non-Union type:

    >>> get_union_types(int)
    None
    """
    return tuple(get_args(tp)) if get_origin(tp) is Union else None


# --- Type-Constrained Containers ------------------------------------------------------------------


class TypeConstrainedDict(UserDict[KT, VT], Generic[KT, VT]):
    """
    Dictionary subclass that constrains the types of keys and values.

    Arguments
    ---------
    key_type : Type[KT]
        Type of the dictionary keys.
    value_type : Type[VT]
        Type of the dictionary values.
    data : Dict[KT, VT]
        Underlying dictionary data, inherited from `UserDict`.
    _key_union_types : Optional[List[Type]]
        Cache for the types of a Union type, if the key type is a Union.
    _value_union_types : Optional[List[Type]]
        Cache for the types of a Union type, if the value type is a Union.

    Examples
    --------
    Define an empty dictionary with string keys and integer values:

    >>> d = TypeConstrainedDict(str, int)
    >>> d['a'] = 1
    >>> d['b'] = '2'
    Traceback (most recent call last):
        ...
    TypeError: Value must be of type int, got str

    Define a directory with values directly:

    >>> d = TypeConstrainedDict(str, int, {'a': 1, 'b': 2})
    >>> d['c'] = 3.0
    Traceback (most recent call last):
        ...
    TypeError: Value must be of type int, got float

    See Also
    --------
    collections.UserDict
    """

    def __init__(
        self, key_type: Type[KT], value_type: Type[VT], data: Optional[Dict[KT, VT]] = None
    ):
        """
        Initialize the dictionary with the types of its keys and values.

        Arguments
        ---------
        key_type : Type[KT]
            Type of the dictionary keys.
        value_type : Type[VT]
            Type of the dictionary values.
        data : Dict[KT, VT], optional
            Initial dictionary data to populate the dictionary with.
        """
        self.key_type = key_type
        self.value_type = value_type
        self._key_union_types = get_union_types(key_type)
        self._value_union_types = get_union_types(value_type)
        super().__init__()
        if data:
            self.update(data)

    def is_valid_key_type(self, key: Any) -> bool:
        """Check if the key is of the correct type using the Union types if present."""
        return (
            any(isinstance(key, t) for t in self._key_union_types)
            if self._key_union_types
            else isinstance(key, self.key_type)
        )

    def is_valid_value_type(self, value: Any) -> bool:
        """Check if the value is of the correct type using the Union types if present."""
        return (
            any(isinstance(value, t) for t in self._value_union_types)
            if self._value_union_types
            else isinstance(value, self.value_type)
        )

    def error_message(self, item: Any, expected_type: Type, k_or_v: Optional[str] = None) -> str:
        """Return an error message for an invalid item."""
        actual_type = type(item).__name__
        if get_origin(expected_type) is Union:
            expected = f"Union[{", ".join(t.__name__ for t in get_args(expected_type))}]"
        else:
            expected = expected_type.__name__
        return f"Invalid {k_or_v} type: got {actual_type} instead of {expected}"

    def __setitem__(self, key: KT, value: VT) -> None:
        """Override `dict` setter method to constrain the types of the assigned key and value."""
        if not self.is_valid_key_type(key):
            raise TypeError(self.error_message(key, self.key_type, k_or_v="key"))
        if not self.is_valid_value_type(value):
            raise TypeError(self.error_message(value, self.value_type, k_or_v="value"))
        super().__setitem__(key, value)

    def update(self, other=(), /, **kwargs):
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
        keys, values = (), ()  # initialize containers for keys and values to check
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
            if not self.is_valid_key_type(key):
                raise TypeError(self.error_message(key, self.key_type, k_or_v="key"))
            if not self.is_valid_value_type(value):
                raise TypeError(self.error_message(value, self.value_type, k_or_v="value"))
        super().update(other, **kwargs)


# --- Type-Constrained List ------------------------------------------------------------------------


class TypeConstrainedList(UserList[VT], Generic[VT]):
    """
    List subclass that constrains the type of its elements.

    Arguments
    ---------
    value_type : Type[VT]
        Type of the list elements.
    data : List[VT]
        Underlying list data, inherited from `UserList`.
    _union_types : Optional[List[Type]]
        Cache for the types of a Union type, if the value type is a Union.

    Examples
    --------
    Define an empty list with integer elements:

    >>> l = TypeConstrainedList(int)
    >>> l.append(1)
    >>> l.append('2')
    Traceback (most recent call last):
        ...
    TypeError: Value must be of type int, got str

    Define a list with elements directly:

    >>> l = TypeConstrainedList(int, [1, 2, 3])
    >>> l.append(3.0)
    Traceback (most recent call last):
        ...
    TypeError: Value must be of type int, got float

    See Also
    --------
    collections.UserList
    """

    def __init__(self, value_type: Type[VT], data: Optional[Iterable[VT]] = None):
        """
        Initialize the list with the type of its elements.

        Arguments
        ---------
        value_type : Type[VT]
            Type of the list elements.
        data : Iterable[VT], optional
            Initial list data to populate the list with.
        """
        self.value_type = value_type
        self._union_types = get_union_types(value_type)
        super().__init__()
        if data:
            self.extend(data)

    def is_valid_type(self, value: Any) -> bool:
        """Check if the value is of the correct type, using the Union types if present."""
        if self._union_types:
            return any(isinstance(value, t) for t in self._union_types)
        return isinstance(value, self.value_type)

    def error_message(self, value: Any) -> str:
        """Return an error message for an invalid value."""
        if self._union_types:
            expected_type = f"Union[{", ".join(t.__name__ for t in self._union_types)}]"
        else:
            expected_type = self.value_type.__name__
        return f"Invalid value type: got {type(value).__name__} instead of {expected_type}"

    def __setitem__(self, index, value):
        """Override the setter method of `list` to constrain the type of the assigned value."""
        if isinstance(index, slice):
            if not all(self.is_valid_type(v) for v in value):
                raise TypeError(f"Invalid values, not all of type {self.value_type}")
        elif not self.is_valid_type(value):
            raise TypeError(self.error_message(value))
        super().__setitem__(index, value)

    def append(self, item: VT) -> None:
        """Override the append method of `list` to constrain the type of the appended value."""
        if not self.is_valid_type(item):
            raise TypeError(self.error_message(item))
        super().append(item)

    def extend(self, other: Iterable[VT]) -> None:
        """Override the extend method of `list` to constrain the types of the extended values."""
        for value in other:
            if not self.is_valid_type(value):
                raise TypeError(self.error_message(value))
        super().extend(other)
