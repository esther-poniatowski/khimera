<a id="components"></a>

# Components

Specific plugin component types that contribute to a host application.

<a id="module-khimera.components.metadata"></a>

<a id="metadata"></a>

## Metadata

<a id="khimera-components-metadata"></a>

### khimera.components.metadata

Classes defining metadata components in plugin models and instances.

### Notes

Metadata is typically used to store additional information about a plugin that is not directly
related to its functionality: configuration parameters (plugin settings), author and repository
information…

Exceptions: name and version are specified outside of metadata, as top-level plugin attributes,
since they are common to all plugins and are used to identify and manage plugins in the host
application.

For simplicity and consistency, metadata it is treated as a special type of ‘component’, although it
is not an active contribution to the host application. However, this approach is useful to define,
access and validate metadata fields in a plugin model similarly to other components.

> **See also**
>
> [`khimera.core.components.Component`](core.md#khimera.core.components.Component)
> : Abstract base class representing a component to a plugin instance.
>
> [`khimera.core.specifications.FieldSpec`](core.md#khimera.core.specifications.FieldSpec)
> : Abstract base class for defining constraints and validations for components in a plugin model.

<a id="khimera.components.metadata.MetaData"></a>

### *class* khimera.components.metadata.MetaData(name, value, description=None)

Bases: [`Component`](core.md#khimera.core.components.Component)

Represents metadata specified in a plugin instance.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the metadata field.
  * **value** (*Any*) – Value of the metadata.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description.

<a id="khimera.components.metadata.MetaDataSpec"></a>

### *class* khimera.components.metadata.MetaDataSpec(name, valid_type, required=False, unique=True, description=None)

Bases: [`FieldSpec`](core.md#khimera.core.specifications.FieldSpec)[[`MetaData`](#khimera.components.metadata.MetaData)]

Declare metadata expected by the host application in the plugin model.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the metadata field.
  * **valid_type** ([*type*](https://docs.python.org/3/library/functions.html#type)) – Type of the metadata value expected by the host application.
  * **required** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the metadata is required.
  * **unique** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the metadata admits a single value. Defaults to `True`.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description.

### Notes

Metadata provided in the plugin must exactly match the field (key) and type expected by the host
application.

Usually, the unique attribute is automatically set to True since each metadata admits a
single value. This can be overridden for metadata fields that accept multiple values by setting
the unique attribute to False.

<a id="khimera.components.metadata.MetaDataSpec.COMPONENT_TYPE"></a>

#### COMPONENT_TYPE

alias of [`MetaData`](#khimera.components.metadata.MetaData)

<a id="khimera.components.metadata.MetaDataSpec.validate"></a>

#### validate(obj)

Check if the metadata value is of the expected type.

<a id="module-khimera.components.commands"></a>

<a id="commands"></a>

## Commands

<a id="khimera-components-commands"></a>

### khimera.components.commands

Classes defining new commands in plugin models and instances.

> **See also**
>
> [`khimera.core.components.Component`](core.md#khimera.core.components.Component)
> : Abstract base class representing a component to a plugin instance.
>
> [`khimera.core.specifications.FieldSpec`](core.md#khimera.core.specifications.FieldSpec)
> : Abstract base class for defining constraints and validations for components in a plugin model.

<a id="khimera.components.commands.Command"></a>

### *class* khimera.components.commands.Command(name, func, group=None, description=None)

Bases: [`Component`](core.md#khimera.core.components.Component)

Represents a command in the host application’s CLI, optionally nested in a predefined
sub-command group.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the command.
  * **func** (*Callable*) – Function or method to be executed when the command is invoked.
  * **group** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Name of the sub-command group where the command will be nested.
    If not provided, the command will be a top-level command, if allowed by the host
    application.
    If the group names does not match any predefined group in the host application, a new group
    will be created, if allowed by the host application.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description.

<a id="khimera.components.commands.CommandSpec"></a>

### *class* khimera.components.commands.CommandSpec(name, groups=None, admits_new_groups=True, admits_top_level=True, required=False, unique=False, description=None)

Bases: [`FieldSpec`](core.md#khimera.core.specifications.FieldSpec)[[`Command`](#khimera.components.commands.Command)]

Declare constraints that the commands of the plugins must satisfy to be accepted by the host
application’s CLI.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the field.
  * **groups** (*Set* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]* *,* *optional*) – Allowed sub-command groups where new commands can be nested.
  * **admits_new_groups** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the plugin can add new sub-command groups. Defaults to `True`.
  * **admits_top_level** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the plugin can add top-level commands. Defaults to `True`.
  * **required** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the field is required.
  * **unique** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the field admits a single command. Defaults to `False`.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description.

### Notes

Because new commands are not involved in the host application’s execution flow, the constraints
are related to the general CLI structure rather than to strict predefined properties of the
commands themselves.

Usually the unique attribute is set to False since multiple commands can be nested in a
single field collecting commands for a specific sub-command group.

<a id="khimera.components.commands.CommandSpec.COMPONENT_TYPE"></a>

#### COMPONENT_TYPE

alias of [`Command`](#khimera.components.commands.Command)

<a id="khimera.components.commands.CommandSpec.validate"></a>

#### validate(obj)

Check if the command group is allowed by the host application.

<a id="module-khimera.components.api"></a>

<a id="api"></a>

## API

<a id="khimera-components-api"></a>

### khimera.components.api

Classes defining API extensions in plugin models and instances.

> **See also**
>
> [`khimera.core.components.Component`](core.md#khimera.core.components.Component)
> : Abstract base class representing a component to a plugin instance.
>
> [`khimera.core.specifications.FieldSpec`](core.md#khimera.core.specifications.FieldSpec)
> : Abstract base class for defining constraints and validations for components in a plugin model.

<a id="khimera.components.api.APIExtension"></a>

### *class* khimera.components.api.APIExtension(name, extension, description=None)

Bases: [`Component`](core.md#khimera.core.components.Component)

Represents an API extension (function, class) to enrich the host application.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the extension.
  * **extension** (*Callable* *or* *Type*) – Function or class to extend the host application’s API.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description.

<a id="khimera.components.api.APIExtensionSpec"></a>

### *class* khimera.components.api.APIExtensionSpec(name, valid_types=None, check_inheritance=False, required=False, unique=False, description=None)

Bases: [`FieldSpec`](core.md#khimera.core.specifications.FieldSpec)[[`APIExtension`](#khimera.components.api.APIExtension)]

Declare an API extension allowed in the host application.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the field.
  * **valid_types** (*Tuple* *of* *Types* *,* *optional*) – Type(s) of the extension expected by the host application. If a tuple is provided, the
    extension must be an instance of one of the types. If not provided, any type is accepted.
  * **check_inheritance** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Determines the type of check to perform relative to the valid type.
    If True, check whether the extension is a subclass of the valid class.
    If False (default), check whether the extension is an instance of the valid class.
  * **required** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the field is required.
  * **unique** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the field admits a single extension. Defaults to `False`.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description.

### Examples

Declare an API extension spec for a function:

```pycon
>>> from types import FunctionType
>>> api_extension_spec = APIExtensionSpec(
...         name="test_spec", valid_types=(FunctionType,),
...         check_inheritance=False
...     )
>>> api_extension_spec.valid_types
(<class 'types.FunctionType'>,)
>>> api_extension_spec.validate(APIExtension(name="test_extension", extension=lambda: None))
True
```

Declare an API extension spec for a sub-class of a base class:

```pycon
>>> class BaseClass:
...     pass
>>> api_extension_spec = APIExtensionSpec(
...         name="test_spec",
...         valid_types=(BaseClass,),
...         check_inheritance=True
...     )
>>> api_extension_spec.valid_types
(<class '__main__.BaseClass'>,)
>>> class DerivedClass(BaseClass):
...    pass
>>> api_extension_spec.validate(APIExtension(name="test_extension", extension=DerivedClass))
True
```

### Notes

Because new extensions are not involved in the host application’s execution flow, the
constraints are related to the general structure of the API rather than to strict predefined
properties of the extensions themselves.

Usually the unique attribute is set to False since multiple extensions can be provided for a
single general field which collects extensions.

<a id="khimera.components.api.APIExtensionSpec.COMPONENT_TYPE"></a>

#### COMPONENT_TYPE

alias of [`APIExtension`](#khimera.components.api.APIExtension)

<a id="khimera.components.api.APIExtensionSpec.validate"></a>

#### validate(obj)

Check if the extension is of the expected types or subclasses.

<a id="module-khimera.components.hooks"></a>

<a id="hooks"></a>

## Hooks

<a id="khimera-components-hooks"></a>

### khimera.components.hooks

Classes defining hooks in plugin models and instances.

> **See also**
>
> [`khimera.core.components.Component`](core.md#khimera.core.components.Component)
> : Abstract base class representing a component to a plugin instance.
>
> [`khimera.core.specifications.FieldSpec`](core.md#khimera.core.specifications.FieldSpec)
> : Abstract base class for defining constraints and validations for components in a plugin model.

<a id="khimera.components.hooks.HookParameter"></a>

### *class* khimera.components.hooks.HookParameter(name, annotation)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Normalized description of one positional hook parameter.

<a id="khimera.components.hooks.HookParameter.name"></a>

#### name *: [str](https://docs.python.org/3/library/stdtypes.html#str)*

<a id="khimera.components.hooks.HookParameter.annotation"></a>

#### annotation *: [Any](https://docs.python.org/3/library/typing.html#typing.Any)*

<a id="khimera.components.hooks.HookSignature"></a>

### *class* khimera.components.hooks.HookSignature(positional, keyword_only, has_var_positional, has_var_keyword, return_annotation)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Stable hook-signature contract used during validation.

<a id="khimera.components.hooks.HookSignature.positional"></a>

#### positional *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[HookParameter](#khimera.components.hooks.HookParameter), ...]*

<a id="khimera.components.hooks.HookSignature.keyword_only"></a>

#### keyword_only *: [tuple](https://docs.python.org/3/library/stdtypes.html#tuple)[[str](https://docs.python.org/3/library/stdtypes.html#str), ...]*

<a id="khimera.components.hooks.HookSignature.has_var_positional"></a>

#### has_var_positional *: [bool](https://docs.python.org/3/library/functions.html#bool)*

<a id="khimera.components.hooks.HookSignature.has_var_keyword"></a>

#### has_var_keyword *: [bool](https://docs.python.org/3/library/functions.html#bool)*

<a id="khimera.components.hooks.HookSignature.return_annotation"></a>

#### return_annotation *: [Any](https://docs.python.org/3/library/typing.html#typing.Any)*

<a id="khimera.components.hooks.Hook"></a>

### *class* khimera.components.hooks.Hook(name, func, description=None)

Bases: [`Component`](core.md#khimera.core.components.Component)

Represents a hook to be executed by the host application.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the hook.
  * **func** (*Callable*) – Function or method to be executed when the hook is triggered.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description.

#### WARNING
The hook function must be annotated with type hints. This is necessary to match the expected
signature defined by the corresponding HookSpec.

<a id="khimera.components.hooks.HookSpec"></a>

### *class* khimera.components.hooks.HookSpec(name, arg_types, allow_var_args=False, allow_var_kwargs=False, return_type=None, required=False, unique=True, description=None)

Bases: [`FieldSpec`](core.md#khimera.core.specifications.FieldSpec)[[`Hook`](#khimera.components.hooks.Hook)]

Declare a hook expected by the host application.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the hook field.
  * **arg_types** (*OrderedDict* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *Type* *]*) – Expected names and types of positional arguments, in order.
    If the argument passed at initialization is a bare dictionary, it will be converted to an
    OrderedDict to ensure consistent ordering.
  * **allow_var_args** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Allow arbitrary positional arguments.
  * **allow_var_kwargs** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Allow arbitrary keyword arguments.
  * **return_type** (*Type* *or* *Tuple* *[**Type* *,*  *...* *]* *,* *optional*) – Expected return type(s). If None, the function should not return anything.
  * **required** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the hook is required.
  * **unique** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the field admits a single hook. Defaults to `True`.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description.

### Notes

Hooks must exactly match the expected function signature in terms of argument names, types,
and return type.

### Examples

Declare a hook field with expected inputs and output type:

```pycon
>>> hook_spec = HookSpec(name="on_event",
...                      arg_types={"name": str, "value": int},
...                      output_type=bool)
```

Create valid and invalid hook components:

```pycon
>>> def valid_hook(name: str, value: int) -> bool:
...     return isinstance(value, int)
>>> def invalid_hook(value: str, name: str) -> bool:
...     return True
>>> valid_comp = Hook(name="valid_hook", callable=valid_hook)
>>> invalid_comp = Hook(name="invalid_hook", callable=invalid_hook)
```

Validate the components against the hook field:

```pycon
>>> print(hook_spec.validate(valid_comp))
True
>>> print(hook_spec.validate(invalid_comp))
False
```

<a id="khimera.components.hooks.HookSpec.COMPONENT_TYPE"></a>

#### COMPONENT_TYPE

alias of [`Hook`](#khimera.components.hooks.Hook)

<a id="khimera.components.hooks.HookSpec.validate"></a>

#### validate(obj)

Validate that the hook function matches the expected signature.

<a id="khimera.components.hooks.HookSpec.describe_signature"></a>

#### *static* describe_signature(fn)

Describe the signature of a function or method.

* **Parameters:**
  **fn** (*Callable*) – Function or method to describe.
* **Returns:**
  * **positional** (*tuple[HookParameter, …]*) – Names and types of positional arguments, in order.
  * **keyword_only** (*tuple[str, …]*) – Names of keyword-only arguments.
  * **has_var_positional** (*bool*) – True if the function has \*args.
  * **has_var_keyword** (*bool*) – True if the function has \*\*kwargs.
  * **return_annotation** (*Any*) – Return type annotation of the function. If None, the return type is not annotated.
* **Return type:**
  [*HookSignature*](#khimera.components.hooks.HookSignature)

<a id="khimera.components.hooks.HookSpec.check_inputs"></a>

#### check_inputs(signature)

Validate if a function matches the signature constraints.

* **Returns:**
  True if the function matches the constraints, False otherwise.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="khimera.components.hooks.HookSpec.check_output"></a>

#### check_output(return_annotation)

Check if the hook function has the expected return type.

<a id="module-khimera.components.assets"></a>

<a id="assets"></a>

## Assets

<a id="khimera-components-assets"></a>

### khimera.components.assets

Classes defining static resources (assets) in plugin models and instances.

> **See also**
>
> [`khimera.core.components.Component`](core.md#khimera.core.components.Component)
> : Abstract base class representing a component to a plugin instance.
>
> [`khimera.core.specifications.FieldSpec`](core.md#khimera.core.specifications.FieldSpec)
> : Abstract base class for defining constraints and validations for components in a plugin model.
>
> [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path)
> : Object-oriented filesystem paths.

<a id="khimera.components.assets.Asset"></a>

### *class* khimera.components.assets.Asset(name, file_path, package=None, description=None)

Bases: [`Component`](core.md#khimera.core.components.Component)

Represents a static resource to provide to the host application.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the asset.
  * **file_path** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Path to the resource file, relative to the package root.
  * **package** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *|* *ModuleType* *,* *optional*) – 

    Name of the package where the resource is located. It can be either a string representing a
    package name or a module object (e.g., \_\_name_\_).

    Common scenarios:
    - If resources are directly in the package root, use the package name as specified in
      pyproject.toml (e.g.  “my_package”).
    - If resources are in a subdirectory, use dot notation to specify the subdirectory (e.g.
      “my_package.resources”).

    If not provided, the package is inferred from the caller’s module where the Asset
    instance is created (\_\_module_\_ attribute), which is assumed to be the file where the
    plugin is defined.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description.

### Notes

Resources cannot be loaded directly by resolving their absolute path on the client’s filesystem.
Indeed, during the installation of the plugin, the storage of the package resources depend on
the packaging tool used (e.g., setuptools). The importlib.resources module provides a way to
access the resources in a platform-independent way.

### Examples

Consider the following directory structure for the plugin package:

```none
my_package/
├── __init__.py
├── assets/
│   └── logo.png
└── plugin.py
```

In the plugin specification, add a component for the logo.png file in the assets
directory:

```pycon
>>> asset = Asset(name="logo", package="my_package", file_path="assets/logo.png")
```

In the host application, access the resource file:

```pycon
>>> with asset.get_path() as path:
...     print(path)
...     # Use the path to access the resource file
```

> **See also**
>
> [`importlib.resources`](https://docs.python.org/3/library/importlib.resources.html#module-importlib.resources)

<a id="khimera.components.assets.Asset.from_caller"></a>

#### *classmethod* from_caller(name, file_path, description=None, stacklevel=1)

Build an asset using the caller module as the package anchor.

<a id="khimera.components.assets.Asset.infer_caller_package"></a>

#### *static* infer_caller_package(stacklevel=1)

Infer the package anchor from the call site rather than the framework module.

<a id="khimera.components.assets.Asset.get_path"></a>

#### get_path()

Create a context manager to access the resource file. When used in a with statement, it
provides a pathlib.Path object representing the resource.

* **Returns:**
  Path to the resource file.
* **Return type:**
  Path

### Notes

This implementation ensures that :

- If the resource is already on the file system, it is accessed directly.
- If the resource is not on the file system (e.g., in a zip file), it is extracted to a
  temporary location, and the context manager cleans up any temporary files or directories
  after the resource was extracted.

<a id="khimera.components.assets.AssetSpec"></a>

### *class* khimera.components.assets.AssetSpec(name, file_ext=None, required=False, unique=True, description=None)

Bases: [`FieldSpec`](core.md#khimera.core.specifications.FieldSpec)[[`Asset`](#khimera.components.assets.Asset)]

Declare an asset expected by the host application.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the field.
  * **file_ext** (*Tuple* *of* [*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Allowed file extensions for the asset, corresponding to file formats that are supported by
    the host application. If not provided, any extension is accepted.
  * **required** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the field is required.
  * **unique** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the field admits a single asset. Defaults to `True`.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description.

### Notes

By default, assets are not required but they are unique, implying that the host application
expects a single asset per name.

<a id="khimera.components.assets.AssetSpec.COMPONENT_TYPE"></a>

#### COMPONENT_TYPE

alias of [`Asset`](#khimera.components.assets.Asset)

<a id="khimera.components.assets.AssetSpec.validate"></a>

#### validate(obj)

Check if the asset file extension is allowed.
