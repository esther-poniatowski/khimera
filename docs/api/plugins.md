<a id="plugins"></a>

# Plugins

Factories to declare plugin models and create plugin instances.

<a id="module-khimera.plugins.declare"></a>

<a id="declare"></a>

## Declare

<a id="khimera-plugins-declare"></a>

### khimera.plugins.declare

Standardized interface for declaring plugin models (on the host application side).

> **See also**
>
> [`khimera.core.specifications.FieldSpec`](core.md#khimera.core.specifications.FieldSpec)
> : Base class for defining constraints specifications for components within a plugin model.
>
> [`khimera.core.dependencies.DependencySpec`](core.md#khimera.core.dependencies.DependencySpec)
> : Base class for defining dependencies between components in a plugin model.
>
> [`khimera.utils.mixins.DeepCopyable`](utils.md#khimera.utils.mixins.DeepCopyable)
> : Mixin class for creating deep copies of objects.
>
> [`khimera.utils.mixins.DeepComparable`](utils.md#khimera.utils.mixins.DeepComparable)
> : Mixin class for comparing objects by deep comparison.

<a id="khimera.plugins.declare.PluginModel"></a>

### *class* khimera.plugins.declare.PluginModel(name, version=None)

Bases: [`DeepCopyable`](utils.md#khimera.utils.mixins.DeepCopyable), [`DeepComparable`](utils.md#khimera.utils.mixins.DeepComparable)

Represents a plugin model specifying the expected structure and components of a plugin.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the model.
  * **version** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Version of the model.

### Examples

Create a plugin model with a name and version:

```pycon
>>> model = PluginModel(name='my_plugin', version='1.0.0')
```

Declare a metadata field in the plugin model:

```pycon
>>> model.add(MetaDataSpec(name='author', required=True, description="Author of the plugin"))
```

Allow integrating new commands in the host application’s CLI, in sub-command groups:

```pycon
>>> model.add(CommandSpec(name='commands',
...                       required=False,
...                       unique=False,
...                       groups={'setup', 'run'},
...                       admits_new_groups=True,
...                       description="New commands for the CLI"))
```

Allow extending the host application with new API functions:

```pycon
>>> model.add(APIExtensionSpec(name='api-functions',
...                            required=False,
...                            unique=False,
...                            description="New functions for the API"))
```

Declare a named hook to use at a specific integration point in the host application:

```pycon
>>> model.add(HookSpec(name='on_start',
                      required=False,
                      unique=True,
                      description="Hook to run on application start"))
```

Declare a static resource processed by the host application:

```pycon
>>> model.add(AssetSpec(name='input_file',
...                     file_ext={'txt', 'csv'},
...                     required=False,
...                     unique=True,
...                     description="File to process"))
```

Get all the metadata fields in the plugin model:

```pycon
>>> model.get(category=MetaData)
{'author': MetaDataSpec(name='author', required=True, description="Author of the plugin")}
```

### Notes

Modular plugin models can be created using the add and remove methods to compose
specifications with dynamic overrides.

<a id="implementation"></a>

### Implementation

Dependency specifications are treated separately from fields specifications (two distinct
attributes) since they do not share the same properties and constraints. However, they can be
declared via the same add method and retrieved via the same get method.

<a id="khimera.plugins.declare.PluginModel.specs"></a>

#### *property* specs *: [Dict](https://docs.python.org/3/library/typing.html#typing.Dict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [Spec](core.md#khimera.core.specifications.Spec)]*

All specifications in the plugin model (combined category and dependency fields).

<a id="khimera.plugins.declare.PluginModel.add"></a>

#### add(spec)

Declares a Spec in the plugin model.

* **Parameters:**
  **spec** ([*Spec*](core.md#khimera.core.specifications.Spec)) – Specification to declare in the plugin model. The name is used as the key in the model.
* **Returns:**
  Updated plugin model instance, for method chaining.
* **Return type:**
  Self
* **Raises:**
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If the spec is not a subclass of Spec supported by the plugin model (either
        FieldSpec or DependencySpec).
  * [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If a field with the same name is already declared in the plugin model
        (category and dependency specs are unique by name).

<a id="khimera.plugins.declare.PluginModel.remove"></a>

#### remove(name)

Remove a spec from the plugin model by name.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Key of the spec to remove from the plugin model.
* **Returns:**
  Updated plugin model instance, for method chaining.
* **Return type:**
  Self
* **Raises:**
  [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If the spec with the given name is not found in the plugin model.

<a id="khimera.plugins.declare.PluginModel.get"></a>

#### get(name)

Get a Spec from the plugin model by name. None if not present in the model.

<a id="khimera.plugins.declare.PluginModel.filter"></a>

#### filter(category=None, unique=None, required=None, custom_filter=None)

Filter the fields in the plugin model based on various criteria.

* **Parameters:**
  * **category** (*Type* *[*[*Component*](core.md#khimera.core.components.Component) *]* *,* *optional*) – Category of the fields to retain. If not provided, all categories are considered.
  * **unique** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – If True, retain only fields that admit a unique component.
    If False, retain only fields that admit multiple components.
    If None (default), this criterion is not applied.
  * **required** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – If True, retain only required fields.
    If False, retain only optional fields.
    If None (default), this criterion is not applied.
  * **custom_filter** (*Callable* *[* *[*[*FieldSpec*](core.md#khimera.core.specifications.FieldSpec) *]* *,* [*bool*](https://docs.python.org/3/library/functions.html#bool) *]* *,* *optional*) – Custom function for more complex filtering logic.
    It should take a FieldSpec and returns a boolean.
* **Returns:**
  Fields that meet all the specified criteria.
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), [FieldSpec](core.md#khimera.core.specifications.FieldSpec)]

### Examples

Filter with a custom function:

```pycon
>>> def custom_filter(field: FieldSpec) -> bool:
...     return field.name.startswith('test_')
>>> model.filter(custom_filter=custom_filter)
```

### Notes

Dependency specs are not considered since they do not share the same filtering properties as
category specs.

<a id="module-khimera.plugins.create"></a>

<a id="create"></a>

## Create

<a id="khimera-plugins-create"></a>

### khimera.plugins.create

Standardized interface for creating plugins (on the plugin provider side).

> **See also**
>
> `khimera.core`, [`khimera.plugins.declare`](#module-khimera.plugins.declare)

<a id="khimera.plugins.create.Plugin"></a>

### *class* khimera.plugins.create.Plugin(model, name, version=None, \*\*kwargs)

Bases: [`DeepCopyable`](utils.md#khimera.utils.mixins.DeepCopyable), [`DeepComparable`](utils.md#khimera.utils.mixins.DeepComparable)

Represents the components provided by a plugin to the host application.

* **Parameters:**
  * **model** ([*PluginModel*](#khimera.plugins.declare.PluginModel)) – Plugin model specifying the expected structure and components of the plugin.
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the plugin.
  * **version** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Version of the plugin.
  * **\*\*kwargs** – Initial components to add to the plugin, keyed by field name.

### Examples

Import a plugin model from the host application:

```pycon
>>> from host_app.plugins.models import example_model
```

Create a plugin with a name and version metadata for this model:

```pycon
>>> plugin = Plugin(model=example_model, name='my_plugin', version='1.0.0')
```

Provide a command within a predefined sub-command group of the host application (‘commands’
field key in the model):

```pycon
>>> def my_command():
...     print("Plugin command executed")
>>> plugin.add('commands', Command(name='my_cmd', callable=my_command, group='sub-command'))
```

Provide a function to extend the host application’s API (‘api-functions’ field key in the
model):

```pycon
>>> def my_function():
...     print("Plugin function executed")
>>> plugin.add('api-functions', APIExtension(name='my_func', callable=my_function))
```

Provide a specific static resource processed by the host application (‘input_file’ field key in
the model):

```pycon
>>> plugin.add('input_file', Asset(name='my_input', package="my_pkg", file_path="assets/logo.png"))
```

### Notes

No validation of the components is performed when adding them to the plugin. The components are
validated against the plugin model by the PluginValidator class in the module
khimera.management.validate.

Implications:

- New fields (keys) can be added to the plugin, regardless of the presence of the corresponding
  field in the model.
- Multiple components can be added to the same field, regardless of the uniqueness constraints
  set by the corresponding FieldSpec in the model.
- Any type of component can be provided to the plugin, regardless of the expected category of
  the corresponding FieldSpec in the model.

<a id="khimera.plugins.create.Plugin.add"></a>

#### add(key, comp)

Add a component to one of the specified fields in the plugin model.

* **Parameters:**
  * **key** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Key of the field as defined in the plugin model.
  * **comp** ([*Component*](core.md#khimera.core.components.Component)) – Component to add to the plugin.
* **Returns:**
  Updated plugin instance, for method chaining.
* **Return type:**
  Self
* **Raises:**
  * [**ComponentError**](exceptions.md#khimera.exceptions.ComponentError) – If a component with the same name already exists for the given key.
  * [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If the comp argument is not a subclass of Component. Automatically raised by the
        TypeConstrainedList class when adding the component to the list of components.

<a id="khimera.plugins.create.Plugin.remove"></a>

#### remove(key, comp_name=None)

Remove a component or all components for a specific key from the plugin.

* **Parameters:**
  * **key** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Key of the field as defined in the plugin model.
  * **comp_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Name of the specific component to remove. If not provided, all components for the
    key are removed.
* **Returns:**
  Updated plugin instance, for method chaining.
* **Return type:**
  Self
* **Raises:**
  [**ComponentError**](exceptions.md#khimera.exceptions.ComponentError) – If the key is not found in the plugin’s components, or if the specified component is
      not found for the given key.

<a id="khimera.plugins.create.Plugin.get"></a>

#### get(key)

Get the components of the plugin for a specific field.

* **Parameters:**
  **key** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Key of the field in the plugin instance.
* **Returns:**
  Components of the plugin stored for the specified field.
* **Return type:**
  [ComponentSet](core.md#khimera.core.components.ComponentSet)

<a id="khimera.plugins.create.Plugin.get_names"></a>

#### get_names(key)

Get the names of the components for a specific field.

* **Parameters:**
  **key** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Key of the field in the plugin instance.
* **Returns:**
  Names of the components stored for the specified field.
* **Return type:**
  [list](https://docs.python.org/3/library/stdtypes.html#list)[[str](https://docs.python.org/3/library/stdtypes.html#str)]

<a id="khimera.plugins.create.Plugin.filter"></a>

#### filter(category=None)

Get the components of the plugin, optionally filtered by category.

* **Parameters:**
  **category** (*Type* *[*[*Component*](core.md#khimera.core.components.Component) *]*) – Category of the components to filter. If not provided, all components are returned.
* **Returns:**
  Components of the plugin, filtered by category if provided.
* **Return type:**
  [TypeConstrainedDict](utils.md#khimera.utils.factories.TypeConstrainedDict)[[str](https://docs.python.org/3/library/stdtypes.html#str), [ComponentSet](core.md#khimera.core.components.ComponentSet)]
