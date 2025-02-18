
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.utils.factories
=======================

Utility classes and functions for creating default objects.
"""
from collections import UserDict
from typing import Generic, TypeVar, Dict, Type

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
        self.key_type = key_type
        self.value_type = value_type
        super().__init__(*args, **kwargs)

    def __setitem__(self, key: KT, value: VT) -> None:
        if not isinstance(key, self.key_type):
            raise TypeError(f"Key must be of type {self.key_type.__name__}, got {type(key).__name__}")
        if not isinstance(value, self.value_type):
            raise TypeError(f"Value must be of type {self.value_type.__name__}, got {type(value).__name__}")
        super().__setitem__(key, value)
