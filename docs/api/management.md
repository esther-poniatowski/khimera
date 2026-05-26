<a id="management"></a>

# Management

Management of plugins across their lifecycle.

<a id="module-khimera.management.validate"></a>

<a id="validate"></a>

## Validate

<a id="khimera-management-validate"></a>

### khimera.management.validate

Validate the components of a plugin against its model.

> **See also**
>
> `khimera.core`, [`khimera.plugins.declare`](plugins.md#module-khimera.plugins.declare), [`khimera.plugins.create`](plugins.md#module-khimera.plugins.create)

<a id="khimera.management.validate.ValidationResult"></a>

### *class* khimera.management.validate.ValidationResult(missing=<factory>, unknown=<factory>, not_unique=<factory>, invalid=<factory>, deps_unsatisfied=<factory>)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Structured diagnostics produced by [`PluginValidator`](#khimera.management.validate.PluginValidator).

<a id="khimera.management.validate.ValidationResult.missing"></a>

#### missing *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Required fields absent from the plugin instance.

<a id="khimera.management.validate.ValidationResult.unknown"></a>

#### unknown *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Fields present in the plugin but not declared in the model.

<a id="khimera.management.validate.ValidationResult.not_unique"></a>

#### not_unique *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Fields constrained to a unique component that contain more than one.

<a id="khimera.management.validate.ValidationResult.invalid"></a>

#### invalid *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [list](https://docs.python.org/3/library/stdtypes.html#list)]*

Mapping of field names to lists of components that failed rule validation.

<a id="khimera.management.validate.ValidationResult.deps_unsatisfied"></a>

#### deps_unsatisfied *: [List](https://docs.python.org/3/library/typing.html#typing.List)[[str](https://docs.python.org/3/library/stdtypes.html#str)]*

Dependency specifications that the plugin does not satisfy.

<a id="khimera.management.validate.ValidationResult.is_valid"></a>

#### *property* is_valid *: [bool](https://docs.python.org/3/library/functions.html#bool)*

Whether the validation passed with no diagnostics.

<a id="khimera.management.validate.PluginValidator"></a>

### *class* khimera.management.validate.PluginValidator(plugin)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Validates the components of a plugin instance against its model.

* **Parameters:**
  **plugin** ([*Plugin*](plugins.md#khimera.plugins.create.Plugin)) – Plugin instance to validate. The plugin’s model is used as the validation reference.

<a id="khimera.management.validate.PluginValidator.check_required"></a>

#### check_required()

Check if all required components are present in the plugin instance.

<a id="khimera.management.validate.PluginValidator.check_unique"></a>

#### check_unique()

Check if components are unique where required.

<a id="khimera.management.validate.PluginValidator.check_unknown"></a>

#### check_unknown()

Check if components are unknown.

<a id="khimera.management.validate.PluginValidator.check_rules"></a>

#### check_rules()

Validate the components of the plugin instance against the rules of the model.

<a id="khimera.management.validate.PluginValidator.check_dependencies"></a>

#### check_dependencies()

Check if all dependencies are satisfied in the plugin instance.

<a id="khimera.management.validate.PluginValidator.validate"></a>

#### validate()

Validate the components of the plugin instance against its model.

* **Returns:**
  Frozen dataclass containing all diagnostics, with an `is_valid` property.
* **Return type:**
  [ValidationResult](#khimera.management.validate.ValidationResult)

<a id="khimera.management.validate.PluginValidator.extract"></a>

#### extract()

Extract the valid components from the plugin instance.

* **Returns:**
  **valid_plugin** – Plugin instance containing only the valid components.
* **Return type:**
  [Plugin](plugins.md#khimera.plugins.create.Plugin)

#### WARNING
This correction does not guarantee that the resulting plugin instance is valid, as it does
not provide missing components nor satisfy the dependencies.

<a id="module-khimera.management.register"></a>

<a id="register"></a>

## Register

<a id="khimera-management-register"></a>

### khimera.management.register

Registers plugins on the host application side.

<a id="khimera.management.register.E"></a>

### *class* khimera.management.register.E

Type variable for elements in the registry.

alias of TypeVar(‘E’, bound=[`Plugin`](plugins.md#khimera.plugins.create.Plugin) | [`Component`](core.md#khimera.core.components.Component))

<a id="khimera.management.register.ConflictResolution"></a>

### *class* khimera.management.register.ConflictResolution(\*args, \*\*kwargs)

Bases: [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol)

Protocol for conflict resolution strategies.

Implementations decide what happens when a newly registered element has the same name as an
existing one.

<a id="khimera.management.register.ConflictResolution.resolve"></a>

#### resolve(new)

Resolve a naming conflict for *new*.

* **Returns:**
  The element to keep in the registry, or `None` to discard the new element.
* **Return type:**
  [Plugin](plugins.md#khimera.plugins.create.Plugin) | [Component](core.md#khimera.core.components.Component) | None
* **Raises:**
  [**PluginConflictError**](exceptions.md#khimera.exceptions.PluginConflictError) – If the strategy forbids conflicts.

<a id="khimera.management.register.RaiseOnConflict"></a>

### *class* khimera.management.register.RaiseOnConflict

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Raises `PluginConflictError` when a conflict occurs.

<a id="khimera.management.register.RaiseOnConflict.resolve"></a>

#### resolve(new)

<a id="khimera.management.register.OverrideOnConflict"></a>

### *class* khimera.management.register.OverrideOnConflict

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Replaces the existing element with the new one, emitting a warning.

<a id="khimera.management.register.OverrideOnConflict.resolve"></a>

#### resolve(new)

<a id="khimera.management.register.IgnoreOnConflict"></a>

### *class* khimera.management.register.IgnoreOnConflict

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Keeps the existing element and discards the new one, emitting a warning.

<a id="khimera.management.register.IgnoreOnConflict.resolve"></a>

#### resolve(new)

<a id="khimera.management.register.ConflictResolver"></a>

### *class* khimera.management.register.ConflictResolver(strategy=None)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Applies a `ConflictResolution` strategy to resolve conflicts.

* **Parameters:**
  **strategy** ([*ConflictResolution*](#khimera.management.register.ConflictResolution) *,* *optional*) – Strategy to apply to resolve conflicts between plugins. Defaults to
  `RaiseOnConflict`.

<a id="khimera.management.register.ConflictResolver.resolve"></a>

#### resolve(new)

Delegate conflict resolution to the configured strategy.

* **Returns:**
  Resolved element to register, or `None` to discard.
* **Return type:**
  [E](#khimera.management.register.E) | None

<a id="khimera.management.register.PluginRegistry"></a>

### *class* khimera.management.register.PluginRegistry(resolver=None, validator_type=<class 'khimera.management.validate.PluginValidator'>, enable_by_default=True)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Stores and manage plugins, resolve conflicts and provide components retrieval.

* **Parameters:**
  * **resolver** ([*ConflictResolver*](#khimera.management.register.ConflictResolver) *,* *optional*) – Applies a `ConflictResolution` strategy to resolve conflicts when registering plugins.
  * **validator_type** (*Type* *[*[*PluginValidator*](#khimera.management.validate.PluginValidator) *]* *,* *optional*) – Validator class to check the plugin structure and components against its model.
    Defaults to `PluginValidator`.
  * **enable_by_default** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether to enable plugins by default when registering them. Defaults to `True`.

### Examples

Initialize a plugin registry:

```pycon
>>> registry = PluginRegistry()
```

Define a plugin with two components:

```pycon
>>> plugin = Plugin('my_plugin', '1.0.0')
>>> def plugin_hook(arg) -> bool:
...     print(arg)
>>> plugin.add('hook', Hook(name="my_hook", callable=plugin_hook))
>>> plugin.add('input_file', Asset(name="logo", package="my_package", file_path="assets/logo.png"))
```

Register the plugin in the registry:

```pycon
>>> registry.register(plugin)
>>> print(registry.plugins)
{'my_plugin': Plugin(name='my_plugin', version='1.0.0', ...)}
```

Get all the components under a specific key:

```pycon
>>> hooks = registry.get('hook')
>>> print(hooks)
[Hook(name='my_hook')]
```

Disable the plugin:

```pycon
>>> registry.disable('my_plugin')
>>> print(registry.enabled)
[]
```

### Notes

So far, a single version per plugin is allowed in the registry.

Enabling and disabling plugins is a way to control which components are available for retrieval.
However, the components are not actually moved within the registry, but are simply filtered out
when retrieving them through the get method. Disabled components are still accessible through
the components attribute of the registry, or by setting the enabled_only argument to False
in the get method.

<a id="khimera.management.register.PluginRegistry.get"></a>

#### get(key, name, enabled_only=True)

Retrieve all the components under a specific key, optionally by name and enabled status.

* **Parameters:**
  * **key** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Field containing the component(s) to retrieve (i.e. as specified in the model).
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Name of one specific component to retrieve (i.e. as registered in the plugin).
  * **enabled_only** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *default=True*) – Whether to retrieve only components from enabled plugins.
* **Returns:**
  All the components registered under this key, matching the name if provided, and
  enabled if requested.
* **Return type:**
  [ComponentSet](core.md#khimera.core.components.ComponentSet)

<a id="khimera.management.register.PluginRegistry.enable"></a>

#### enable(name)

Enable a plugin to make all its components available via the get method.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the plugin to enable.
* **Raises:**
  [**PluginNotFoundError**](exceptions.md#khimera.exceptions.PluginNotFoundError) – If the plugin is not registered (i.e. cannot be enabled).

<a id="khimera.management.register.PluginRegistry.disable"></a>

#### disable(name)

Disable a plugin to prevent its components from being retrieved via the get method.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the plugin to disable.

<a id="khimera.management.register.PluginRegistry.register"></a>

#### register(plugin)

Default registering behavior. Override this method to customize the registration process.

* **Parameters:**
  **plugin** ([*Plugin*](plugins.md#khimera.plugins.create.Plugin)) – Plugin instance to register.
* **Raises:**
  * [**PluginValidationError**](exceptions.md#khimera.exceptions.PluginValidationError) – If the plugin is invalid (carries the full `ValidationResult` diagnostics).
  * [**PluginConflictError**](exceptions.md#khimera.exceptions.PluginConflictError) – If conflicts occur and the conflict resolution strategy raises.

<a id="khimera.management.register.PluginRegistry.unpack"></a>

#### unpack(plugin)

Unpack and organize all the components provided by a plugin.

### Notes

Each component provided by the plugin is stored in the registry under the key corresponding
to its nature (i.e. the field’s key under which it was added to the plugin). If a key
already exists in the registry (e.g. other plugins have already registered components for
this field), the new component is added among the already registered components. If a key
does not exist yet in the registry (i.e. the plugin is the first to provide components for
this field), a new key is created and the component is stored under it.

For each key, if the field is not contained to unique in the model (i.e. unique component
by plugin), a plugin can provide multiple components (under the form of a ComponentSet).
