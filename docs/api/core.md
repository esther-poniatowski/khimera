<a id="core"></a>

# Core

Core classes and interfaces for plugin models and instances.

<a id="module-khimera.core.components"></a>

<a id="components"></a>

## Components

<a id="khimera-core-components"></a>

### khimera.core.components

Base classes for defining components in plugin models and instances.

> **See also**
>
> `khimera.components`
> : Module defining specialized components for plugins.
>
> [`khimera.utils.mixins.DeepCopyable`](utils.md#khimera.utils.mixins.DeepCopyable)
> : Mixin class for creating deep copies of objects.
>
> [`khimera.utils.mixins.DeepComparable`](utils.md#khimera.utils.mixins.DeepComparable)
> : Mixin class for comparing objects by deep comparison.

<a id="khimera.core.components.Component"></a>

### *class* khimera.core.components.Component(name, description=None)

Bases: [`ABC`](https://docs.python.org/3/library/abc.html#abc.ABC), [`DeepCopyable`](utils.md#khimera.utils.mixins.DeepCopyable), [`DeepComparable`](utils.md#khimera.utils.mixins.DeepComparable)

Base class representing a component in a plugin, i.e. a unit of functionality or data that is
supported by the host application.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Unique name of the component in the plugin instance.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Description of the component (e.g. purpose, usage).

<a id="khimera.core.components.Component.plugin"></a>

#### plugin *: [str](https://docs.python.org/3/library/stdtypes.html#str) | [None](https://docs.python.org/3/library/constants.html#None)*

Plugin instance name to which the component is attached, once registered.

<a id="khimera.core.components.Component.category"></a>

#### *property* category *: [Type](https://docs.python.org/3/library/typing.html#typing.Type)*

Category of the component.

<a id="khimera.core.components.Component.attach"></a>

#### attach(plugin_name)

Attach the component to a plugin instance.

<a id="khimera.core.components.ComponentSet"></a>

### *class* khimera.core.components.ComponentSet(data=None)

Bases: [`TypeConstrainedList`](utils.md#khimera.utils.factories.TypeConstrainedList)[[`Component`](#khimera.core.components.Component)]

Container of components in a plugin instance, behaving like a type constrained list.

### Examples

Create a component set with a list of components:

```pycon
>>> comp1 = Command(name='cmd1', func=lambda: print("Command 1"))
>>> comp2 = Command(name='cmd2', func=lambda: print("Command 2"))
>>> comp_set = ComponentSet([comp1, comp2])
>>> comp_set
ComponentSet([Command('cmd1'), Command('cmd2')])
>>> comp_set[0]
Command('cmd1')
```

Create an empty component set and add components to it:

```pycon
>>> comp_set = ComponentSet()
>>> comp_set
ComponentSet([])
>>> comp_set.append(Command(name='cmd3', func=lambda: print("Command 3")))
>>> comp_set
ComponentSet([Command('cmd3')])
>>> comp_set.extend([Command(name='cmd4', func=lambda: print("Command 4")),
...                  Command(name='cmd5', func=lambda: print("Command 5")])
>>> comp_set
ComponentSet([Command('cmd3'), Command('cmd4'), Command('cmd5')])
```

> **See also**
>
> [`khimera.utils.factories.TypeConstrainedList`](utils.md#khimera.utils.factories.TypeConstrainedList)
> : Factory class for creating type constrained lists.

<a id="module-khimera.core.specifications"></a>

<a id="specifications"></a>

## Specifications

<a id="khimera-core-specifications"></a>

### khimera.core.specifications

Base classes representing constraints specifications for components within a plugin model.

> **See also**
>
> `khimera.components`
> : Module defining base and specialized components for plugins.
>
> [`khimera.core.dependencies`](#module-khimera.core.dependencies)
> : Module defining dependency specifications for plugin components.
>
> [`khimera.plugins.declare.PluginModel`](plugins.md#khimera.plugins.declare.PluginModel)
> : Class defining the structure of a plugin model, including its fields and dependencies.
>
> [`khimera.plugins.create.Plugin`](plugins.md#khimera.plugins.create.Plugin)
> : Class representing a plugin instance, which is a collection of components that adhere to a plugin model.
>
> [`khimera.utils.mixins.DeepCopyable`](utils.md#khimera.utils.mixins.DeepCopyable)
> : Mixin class for creating deep copies of objects.
>
> [`khimera.utils.mixins.DeepComparable`](utils.md#khimera.utils.mixins.DeepComparable)
> : Mixin class for comparing objects by deep comparison.

<a id="khimera.core.specifications.O"></a>

### *class* khimera.core.specifications.O

Type variable for an object to be validated (component, full plugin…).

alias of TypeVar(‘O’)

<a id="khimera.core.specifications.Spec"></a>

### *class* khimera.core.specifications.Spec(name, description=None)

Bases: [`ABC`](https://docs.python.org/3/library/abc.html#abc.ABC), [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic)[[`O`](#khimera.core.specifications.O)], [`DeepCopyable`](utils.md#khimera.utils.mixins.DeepCopyable), [`DeepComparable`](utils.md#khimera.utils.mixins.DeepComparable)

Base class representing constraints specifications for plugin components within a plugin model.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Unique name of the Spec in the plugin model.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Description of the Spec.

<a id="khimera.core.specifications.Spec.validate"></a>

#### *abstractmethod* validate(obj)

Validates a candidate object against the Spec. To be implemented by subclasses.

* **Parameters:**
  **obj** ([*O*](#khimera.core.specifications.O)) – Candidate object to validate (usually, single component or full plugin, depending on the
  subclass).
* **Returns:**
  Whether the candidate object satisfies the specification.
* **Return type:**
  [bool](https://docs.python.org/3/library/functions.html#bool)

<a id="khimera.core.specifications.C"></a>

### *class* khimera.core.specifications.C

Type variable for a component to a plugin instance.

alias of TypeVar(‘C’, bound=[`Component`](#khimera.core.components.Component))

<a id="khimera.core.specifications.FieldSpec"></a>

### *class* khimera.core.specifications.FieldSpec(name, required=False, unique=False, description=None)

Bases: [`Spec`](#khimera.core.specifications.Spec)[[`C`](#khimera.core.specifications.C)], [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic)[[`C`](#khimera.core.specifications.C)]

Specification of a field in the plugin that is supported by the host application.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Unique name of the field.
  * **required** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether at least one component is required in the plugin under this name.
  * **unique** ([*bool*](https://docs.python.org/3/library/functions.html#bool) *,* *optional*) – Whether the component must be unique in the plugin.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description of the field.

<a id="khimera.core.specifications.FieldSpec.COMPONENT_TYPE"></a>

#### COMPONENT_TYPE *: [Type](https://docs.python.org/3/library/typing.html#typing.Type)[[C](#khimera.core.specifications.C)]*

Type of the component associated with the specification.

<a id="khimera.core.specifications.FieldSpec.validate"></a>

#### *abstractmethod* validate(obj)

Validate one component against the specification (narrower signature).

<a id="khimera.core.specifications.FieldSpec.category"></a>

#### *property* category *: [Type](https://docs.python.org/3/library/typing.html#typing.Type)[[Component](#khimera.core.components.Component)] | [None](https://docs.python.org/3/library/constants.html#None)*

Category of the specification.

* **Return type:**
  Type[[Component](#khimera.core.components.Component)] or None

### Notes

The category property is used during filtering and validation processes. For consistency
across the Spec classes, it returns None if the COMPONENT_TYPE class attribute is not
set by the subclass.

<a id="module-khimera.core.dependencies"></a>

<a id="dependencies"></a>

## Dependencies

<a id="khimera-core-dependencies"></a>

### khimera.core.dependencies

Base and concrete classes for dependency specifications in plugin models.

> **See also**
>
> `khimera.core.components.Spec`
> : Base class representing constraints specifications for plugin components within a plugin model.
>
> [`khimera.plugins.create.Plugin`](plugins.md#khimera.plugins.create.Plugin)
> : Class representing a plugin instance, which is a collection of components that adhere to a plugin model.

<a id="khimera.core.dependencies.DependencySpec"></a>

### *class* khimera.core.dependencies.DependencySpec(name, fields, description=None)

Bases: [`Spec`](#khimera.core.specifications.Spec)[`Plugin`]

Specification enforcing dependencies between several components in the plugin.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the specification.
  * **fields** (*Iterable* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Arbitrary number of field names in the model that are involved in the dependency
    relationship.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description of the specification.

<a id="khimera.core.dependencies.DependencySpec.validate"></a>

#### *abstractmethod* validate(obj)

Validate the dependencies globally in the plugin instance.

<a id="khimera.core.dependencies.PredicateDependency"></a>

### *class* khimera.core.dependencies.PredicateDependency(name, predicate, fields, description=None)

Bases: [`DependencySpec`](#khimera.core.dependencies.DependencySpec)

Default dependency specification for a single dependent and dependency component.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the dependency specification.
  * **predicate** (*Callable* *[* *...* *,* [*bool*](https://docs.python.org/3/library/functions.html#bool) *]*) – Validation rule, that admits any number of ComponentSet (named by their fields) and
    returns a boolean indicating whether the dependencies are satisfied.
  * **fields** (*Iterable* *[*[*str*](https://docs.python.org/3/library/stdtypes.html#str) *]*) – Arbitrary number of field names in the model that contain dependent and dependency
    components.
  * **description** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Human-readable description of the dependency.

### Examples

Define a predicate that checks that is a hook is provided, it is paired with an asset (assuming
a unique component in both fields):

```pycon
>>> def hook_asset_dependency(hook: ComponentSet[Hook], asset: ComponentSet[Asset]) -> bool:
...     return bool(hook) == bool(asset)
```

Define the dependency specification:

```pycon
>>> hook_asset_spec = PredicateDependency(
...     name="hook_asset",
...     predicate=hook_asset_dependency,
...     fields=("hook", "asset")
... )
```

#### WARNING
The predicate function should handle the case where the fields admit multiple components. For
instance, it could iterate over the components in several fields in parallel and check the
dependencies for each combination.

<a id="khimera.core.dependencies.PredicateDependency.validate"></a>

#### validate(obj)

Validate the dependencies globally in the plugin instance.
