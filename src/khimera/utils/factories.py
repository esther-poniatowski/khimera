
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.utils.factories
=======================

Utility classes and functions for creating default objects.
"""
from collections import UserDict, UserList
from typing import Generic, TypeVar, Type

KT = TypeVar('KT')
VT = TypeVar('VT')


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
    def __init__(self, key_type: Type[KT], value_type: Type[VT], *args, **kwargs):
        """
        Initialize the dictionary with the types of its keys and values.

        Arguments
        ---------
        key_type : Type[KT]
            Type of the dictionary keys.
        value_type : Type[VT]
            Type of the dictionary values.
        *args, **kwargs
            Additional arguments to pass to the `UserDict` constructor.
        """
        self.key_type = key_type
        self.value_type = value_type
        super().__init__(*args, **kwargs)

    def __setitem__(self, key: KT, value: VT) -> None:
        """Override the `dict` setter method to constrain the types of keys and values."""
        if not isinstance(key, self.key_type):
            raise TypeError(f"Invalid key type: got {type(key).__name__} instead of {self.key_type.__name__}")
        if not isinstance(value, self.value_type):
            raise TypeError(f"Invalid value type: got {type(value).__name__} instead of {self.value_type.__name__}")
        super().__setitem__(key, value)


class TypeConstrainedList(UserList[VT], Generic[VT]):
    """
    List subclass that constrains the type of its elements.

    Arguments
    ---------
    value_type : Type[VT]
        Type of the list elements.
    data : List[VT]
        Underlying list data, inherited from `UserList`.

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
    def __init__(self, value_type: Type[VT], *args, **kwargs):
        """
        Initialize the list with the type of its elements.

        Arguments
        ---------
        value_type : Type[VT]
            Type of the list elements.
        *args, **kwargs
            Additional arguments to pass to the `UserList` constructor.
        """
        self.value_type = value_type
        super().__init__(*args, **kwargs)

    def append(self, value: VT) -> None:
        if not isinstance(value, self.value_type):
            raise TypeError(f"Invalid value type: got {type(value).__name__} instead of {self.value_type.__name__}")
        super().append(value)
