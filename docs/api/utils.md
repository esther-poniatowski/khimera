<a id="utils"></a>

# Utils

Utility classes and mixins.

<a id="module-khimera.utils.factories"></a>

<a id="factories"></a>

## Factories

<a id="khimera-utils-factories"></a>

### khimera.utils.factories

Utility classes and functions for creating default objects.

#### WARNING
When using VT as a generic type in Type[VT], it is assumed to represent a *concrete* class.
Abstract base classes (ABCs) do not qualify because they are not instantiable.

> **See also**
>
> `beartype.door.is_bearable`, `hint`
>
> `Strategies`
> : The tradeoff between overhead and completeness is governed by a sampling approach for type checking containers. The type-checking strategy (i.e., BeartypeStrategy) dictates how many items are type-checked at each nesting level of each container. - BeartypeStrategy.01 (default): Constant-time strategy (O(1)), type-checking a single randomly selected item of each container. - BeartypeStrategy.0n: Linear-time strategy (O(n)), type-checking all items of a container. Here, the default strategy is used, which implies that containers should have homogeneous elements when nested in TypeConstrainedList or TypeConstrainedDict instances. Erroneous mixed types might not be detected.

<a id="khimera.utils.factories.KT"></a>

### *class* khimera.utils.factories.KT

Type variable for the key type of a dictionary.

alias of TypeVar(‘KT’)

<a id="khimera.utils.factories.VT"></a>

### *class* khimera.utils.factories.VT

Type variable for the value type of a dictionary or list.

alias of TypeVar(‘VT’)

<a id="khimera.utils.factories.error_message"></a>

### khimera.utils.factories.error_message(item, expected_type, spec=None)

Generate an error message for an invalid item.

* **Parameters:**
  * **item** (*Any*) – Item to check the type of.
  * **expected_type** ([*object*](https://docs.python.org/3/library/functions.html#object)) – Expected type for the item, under the form of a single type or a complex type hint.
  * **spec** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Specification of the item, used to generate a more informative error message.

<a id="khimera.utils.factories.TypeConstrainedList"></a>

### *class* khimera.utils.factories.TypeConstrainedList(value_type, data=())

Bases: [`UserList`](https://docs.python.org/3/library/collections.html#collections.UserList)[[`VT`](#khimera.utils.factories.VT)], [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic)[[`VT`](#khimera.utils.factories.VT)]

List subclass that constrains the type of its elements.

* **Parameters:**
  * **value_type** ([*object*](https://docs.python.org/3/library/functions.html#object)) – Allowed type(s) for the list elements, under the form of a single type of a complex type
    hint. Multiple types can be allowed using a Union type.
  * **data** (*List* *[*[*VT*](#khimera.utils.factories.VT) *]*) – Underlying list data, inherited from UserList.

### Examples

Create an empty list constrained to contain only integers:

```pycon
>>> l = TypeConstrainedList(int)
>>> l.append(1)
>>> l.append('2')
Traceback (most recent call last):
    ...
TypeError: Value must be of type int, got str
```

Create a type contained list directly populated with elements:

```pycon
>>> l = TypeConstrainedList(int, [1, 2, 3])
>>> l.append(3.0)
Traceback (most recent call last):
    ...
TypeError: Value must be of type int, got float
```

Allowing multiple types:

```pycon
>>> from typing import Union
>>> l = TypeConstrainedList(Union[int, float], [1, 2.0, 3])
```

Allow complex types with expressive type hints:

```pycon
>>> from typing import Union
>>> l = TypeConstrainedList(Union[str, List[str]], ['a', ['b', 'c']])
```

> **See also**
>
> [`collections.UserList`](https://docs.python.org/3/library/collections.html#collections.UserList)

<a id="khimera.utils.factories.TypeConstrainedList.__init__"></a>

#### \_\_init_\_(value_type, data=())

Initialize the list with the type of its elements.

* **Parameters:**
  * **value_type** ([*object*](https://docs.python.org/3/library/functions.html#object)) – Expected type(s) or type hint (including Union types) for the list elements.
  * **data** (*Iterable* *[*[*VT*](#khimera.utils.factories.VT) *]* *,* *optional*) – Initial data to populate the list with.

<a id="khimera.utils.factories.TypeConstrainedList.is_valid"></a>

#### is_valid(value)

Check if the value is of the correct type, matched against the value_type attribute.

> **See also**
>
> `beartype.door.is_bearable`, `hint`

<a id="khimera.utils.factories.TypeConstrainedList.append"></a>

#### append(item)

Override the append method of list to constrain the type of the appended value.

<a id="khimera.utils.factories.TypeConstrainedList.extend"></a>

#### extend(other)

Override the extend method of list to constrain the types of the extended values.

<a id="khimera.utils.factories.TypeConstrainedList.error_message"></a>

#### error_message(item)

Generate an error message for an invalid item.

<a id="khimera.utils.factories.TypeConstrainedDict"></a>

### *class* khimera.utils.factories.TypeConstrainedDict(key_type, value_type, data=None)

Bases: [`UserDict`](https://docs.python.org/3/library/collections.html#collections.UserDict)[[`KT`](#khimera.utils.factories.KT), [`VT`](#khimera.utils.factories.VT)], [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic)[[`KT`](#khimera.utils.factories.KT), [`VT`](#khimera.utils.factories.VT)]

Dictionary subclass that constrains the types of keys and values.

* **Parameters:**
  * **key_type** ([*object*](https://docs.python.org/3/library/functions.html#object)) – Allowed type(s) for the dictionary keys, under the form of a single type of a complex type
    hint. Multiple types can be allowed using a Union type.
  * **value_type** ([*object*](https://docs.python.org/3/library/functions.html#object)) – Allowed type(s) for the dictionary values.
  * **data** (*Dict* *[*[*KT*](#khimera.utils.factories.KT) *,* [*VT*](#khimera.utils.factories.VT) *]*) – Underlying dictionary data, inherited from UserDict.

### Examples

Create an empty dictionary with string keys and integer values:

```pycon
>>> d = TypeConstrainedDict(str, int)
>>> d['a'] = 1
>>> d['b'] = '2'
Traceback (most recent call last):
    ...
TypeError: Value must be of type int, got str
```

Create a dictionary directly populated with elements:

```pycon
>>> d = TypeConstrainedDict(str, int, {'a': 1, 'b': 2})
>>> d['c'] = 3.0
Traceback (most recent call last):
    ...
TypeError: Value must be of type int, got float
```

Allow multiple types for keys and values:

```pycon
>>> from typing import Union
>>> d = TypeConstrainedDict(Union[str, int], Union[int, float], {'a': 1, 2: 2.0})
```

> **See also**
>
> [`collections.UserDict`](https://docs.python.org/3/library/collections.html#collections.UserDict)

<a id="khimera.utils.factories.TypeConstrainedDict.__init__"></a>

#### \_\_init_\_(key_type, value_type, data=None)

Initialize the dictionary with the types of its keys and values.

* **Parameters:**
  * **key_type** ([*object*](https://docs.python.org/3/library/functions.html#object)) – Expected type(s) or type hint (including Union types) for the dictionary keys.
  * **value_type** ([*object*](https://docs.python.org/3/library/functions.html#object)) – Expected type(s) or type hint (including Union types) for the dictionary values.
  * **data** (*Dict* *[*[*KT*](#khimera.utils.factories.KT) *,* [*VT*](#khimera.utils.factories.VT) *]* *,* *optional*) – Initial data to populate the dictionary with.

<a id="khimera.utils.factories.TypeConstrainedDict.is_valid_key"></a>

#### is_valid_key(key)

Check if the key is of the correct type, matched against the key_type attribute.

> **See also**
>
> `beartype.door.is_bearable`, `hint`

<a id="khimera.utils.factories.TypeConstrainedDict.is_valid_value"></a>

#### is_valid_value(value)

Check if the value is of the correct type, matched against the value_type attribute.

<a id="khimera.utils.factories.TypeConstrainedDict.update"></a>

#### update(other=(), /, \*\*kwargs)

Override dict update method to constrain the types of the updated keys and values.

* **Parameters:**
  * **other** (*Union* *[**Dict* *[*[*KT*](#khimera.utils.factories.KT) *,* [*VT*](#khimera.utils.factories.VT) *]* *,* *Iterable* *[**Tuple* *[*[*KT*](#khimera.utils.factories.KT) *,* [*VT*](#khimera.utils.factories.VT) *]* *]* *]* *,* *optional*) – Dictionary or iterable of key-value pairs to update the dictionary with.
  * **\*\*kwargs** (*Dict* *[*[*KT*](#khimera.utils.factories.KT) *,* [*VT*](#khimera.utils.factories.VT) *]*) – Key-value pairs to update the dictionary with.

> **See also**
>
> `collections.MutableMapping.update`
> : Original method documentation, using overload to provide various type signatures. See mypy issue  #1430.

<a id="khimera.utils.factories.TypeConstrainedDict.error_message_key"></a>

#### error_message_key(item)

Generate an error message for an invalid key.

<a id="khimera.utils.factories.TypeConstrainedDict.error_message_value"></a>

#### error_message_value(item)

Generate an error message for an invalid value.

<a id="module-khimera.utils.mixins"></a>

<a id="mixins"></a>

## Mixins

<a id="khimera-utils-mixins"></a>

### khimera.utils.mixins

Mixin classes for common functionality in custom classes and objects with nested components.

<a id="khimera.utils.mixins.DeepCopyable"></a>

### *class* khimera.utils.mixins.DeepCopyable

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Mixin class for creating deep copies of objects.

> **See also**
>
> [`copy.deepcopy`](https://docs.python.org/3/library/copy.html#copy.deepcopy)

<a id="khimera.utils.mixins.DeepCopyable.copy"></a>

#### copy()

Create a deep copy of the object, creating copies of all its nested components.

<a id="khimera.utils.mixins.DeepComparable"></a>

### *class* khimera.utils.mixins.DeepComparable

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Mixin class for comparing objects by deep comparison.

> **See also**
>
> `deepdiff.DeepDiff`
