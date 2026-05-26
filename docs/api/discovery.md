<a id="discovery"></a>

# Discovery

Discovery of plugins and their components in the host application.

<a id="module-khimera.discovery.find"></a>

<a id="find"></a>

## Find

<a id="khimera-discovery-find"></a>

### khimera.discovery.find

Discovers plugins on the host application side.

<a id="khimera.discovery.find.PluginEntryPoint"></a>

### *class* khimera.discovery.find.PluginEntryPoint(name, value)

Bases: [`object`](https://docs.python.org/3/library/functions.html#object)

Represents an entry point for a plugin in the host application, inspired by the EntryPoint
class from importlib.metadata.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the entry point.
  * **value** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Reference pointing to a Plugin instance. Format: `package.module:object`.

### Examples

Consider the following plugin package structure:

```none
path/to/project/
├── my_package/
│   ├── __init__.py
│   └── plugins.py
└── ...
```

The plugins.py module contains the following Plugin object:

```python
from khimera.plugins.create import Plugin
from host_app.models import MyPluginModel

my_plugin = Plugin(
    name='my_plugin',
    version='0.1.0',
    model=MyPluginModel,
    ...
)
```

Create a plugin entry point for this plugin:

```pycon
>>> entry_point = PluginEntryPoint(path='path/to/package', value='my_package.plugins:MyPlugin')
```

Load the referenced plugin object:

```pycon
>>> plugin = entry_point.load()
>>> print(plugin)
Plugin(name='my_plugin', version='0.1.0', model=MyPluginModel, ...)
```

### Notes

This class is inspired by the EntryPoint class from the importlib.metadata module.

- Shared attributes: name, value, module, attr, load.
- Omitted attributes: name, group (relevant for entry points specified in pyproject.toml).
- New attributes: path (custom directory path to the plugin package).

<a id="khimera.discovery.find.PluginEntryPoint.load"></a>

#### load()

Dynamically imports and returns the referenced Plugin object.

* **Returns:**
  Referenced Plugin object.
* **Return type:**
  [Plugin](plugins.md#khimera.plugins.create.Plugin)

<a id="khimera.discovery.find.PluginFinder"></a>

### *class* khimera.discovery.find.PluginFinder

Bases: [`ABC`](https://docs.python.org/3/library/abc.html#abc.ABC)

Abstract base class for plugins discovery strategies for the host application.

### Examples

Initialize a plugin finder to discover plugins from the pyproject.toml files:

```pycon
>>> finder = FromInstalledFinder(app_name='myapp')
```

Discover the plugins provided by the installed packages for the host application:

```pycon
>>> finder.discover()
```

Filter the discovered plugins by model:

```pycon
>>> plugins = finder.filter(model=MyPluginModel)
>>> print(plugins)
[Plugin(name='my_plugin', version='0.1.0', ...), ...]
```

Get a specific plugin by name and version:

```pycon
>>> plugin = finder.get(name='my_plugin', version='0.1.0')
>>> print(plugin)
Plugin(name='my_plugin', version='0.1.0', ...)
```

### Notes

The plugin discovery mechanism is designed to be comprehensive and to collect as many plugins as
possible before selecting them, validating them, or resolving conflicts between them.

To do so, all the plugins are stored in a list rather than a dictionary. Thus, plugins are not
named, which allows to store multiple plugins of the same name but different versions.

<a id="khimera.discovery.find.PluginFinder.plugins"></a>

#### plugins

All the discovered plugins.

<a id="khimera.discovery.find.PluginFinder.discover"></a>

#### *abstractmethod* discover()

Discovers plugins by implementing the discovery strategy.

<a id="khimera.discovery.find.PluginFinder.store"></a>

#### store(plugin)

Stores a discovered plugin.

### Notes

Type checking is performed automatically by the TypeConstrainedList class.

<a id="khimera.discovery.find.PluginFinder.get"></a>

#### get(name, version=None)

Get all plugins matching *name* and optionally *version*.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the plugin to get.
  * **version** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Version of the plugin to get.
* **Returns:**
  Plugins matching the criteria (may be empty).
* **Return type:**
  List[[Plugin](plugins.md#khimera.plugins.create.Plugin)]

<a id="khimera.discovery.find.PluginFinder.get_one"></a>

#### get_one(name, version=None)

Get exactly one plugin matching *name* and optionally *version*.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the plugin to get.
  * **version** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Version of the plugin to get.
* **Returns:**
  The single matching plugin.
* **Return type:**
  [Plugin](plugins.md#khimera.plugins.create.Plugin)
* **Raises:**
  * [**PluginNotFoundError**](exceptions.md#khimera.exceptions.PluginNotFoundError) – If no plugin matches.
  * [**AmbiguousLookupError**](exceptions.md#khimera.exceptions.AmbiguousLookupError) – If multiple plugins match.

<a id="khimera.discovery.find.PluginFinder.filter"></a>

#### filter(model)

Filter the discovered plugins by model.

* **Parameters:**
  **model** ([*PluginModel*](plugins.md#khimera.plugins.declare.PluginModel)) – Plugin model specifying the expected structure and components of the plugins.
  If not provided, all the plugins are considered regardless of the model they adhere to.

<a id="module-khimera.discovery.strategies"></a>

<a id="strategies"></a>

## Strategies

<a id="khimera-discovery-strategies"></a>

### khimera.discovery.strategies

Concrete discovery strategies for plugins in the host application.

> **See also**
>
> [`khimera.discovery.find`](#module-khimera.discovery.find)
> : Base classes for plugin discovery.

<a id="khimera.discovery.strategies.FromInstalledFinder"></a>

### *class* khimera.discovery.strategies.FromInstalledFinder(app_name, entry_point_group=None)

Bases: [`PluginFinder`](#khimera.discovery.find.PluginFinder)

Discovers plugins for the host application from entry points declared in pyproject.toml of the
installed packages.

Typically, this strategy is triggered automatically by the host application itself in its
\_\_init_\_.py file or by a CLI command that initializes the application.

* **Parameters:**
  * **app_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the application requiring plugin discovery.
  * **entry_point_group** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Entry point group where external packages declare their entry points to plugins for the host
    application. Defaults to `{app_name}.plugins`.

### Examples

On the plugin provider side, entry points for the host application are declared in the
pyproject.toml file of the provider’s package:

```toml
[project.entry-points.'host_name.plugins']
plugin1 = "my_package.plugins:Plugin1"
plugin2 = "my_package.plugins:Plugin2"
```

On the host application side, external plugins can be discovered by triggering the
FromInstalledFinder in the host application’s \_\_init_\_.py file (to ensure plugins are
discovered at import time):

```python
from khimera.discovery.strategies import FromInstalledFinder

finder = FromInstalledFinder(app_name="host_name")
finder.discover()
```

### Notes

The discovery mechanism does not differentiate between ‘internal’ plugins (packaged with the
host application) and ‘external’ plugins (installed as third-party packages), as long as the
host application itself defines its own plugins entry points in its pyproject.toml file. All
plugins are treated similarly as entry points regardless of their sources by the importlib
library since their metadata is registered during the packages’ installation in the user’s
environment.

<a id="khimera.discovery.strategies.FromInstalledFinder.discover"></a>

#### discover()

Discovers plugins from entry points in the pyproject.toml files of plugin packages.

* **Raises:**
  [**KhimeraError**](exceptions.md#khimera.exceptions.KhimeraError) – If a plugin loaded from an entry point is not an instance of Plugin.

<a id="khimera.discovery.strategies.FromInstalledFinder.get_entry_points"></a>

#### get_entry_points()

Finds all installed plugins that declare entry points for the host application.

* **Returns:**
  Entry points for the host application.
* **Return type:**
  List[[importlib.metadata.EntryPoint](https://docs.python.org/3/library/importlib.metadata.html#importlib.metadata.EntryPoint)]
* **Raises:**
  [**RuntimeError**](https://docs.python.org/3/library/exceptions.html#RuntimeError) – If entry points retrial fails.

<a id="khimera.discovery.strategies.FromAPIFinder"></a>

### *class* khimera.discovery.strategies.FromAPIFinder(\*args)

Bases: [`PluginFinder`](#khimera.discovery.find.PluginFinder)

Discovers plugins for the host application specified at import time by the user through the API.

Typically, this strategy is triggered by the user in a main.py file which imports the host
application, when the user develops plugins locally.

* **Parameters:**
  **\*args** ([*PluginEntryPoint*](#khimera.discovery.find.PluginEntryPoint)) – Entry points for the plugins specified by the user.

### Examples

Any user can develop plugins for the host application, for instance in distinct modules stored
in a specific directory of the  user’s project:

```plaintext
.
├── main.py
└── plugins/
    ├── __init__.py
    ├── plugin1.py
    └── plugin2.py
```

In the main.py file, the user can import the host application (if it is installed in the
user’s environment) and specify the plugins entry points that should be discovered:

```python
import host_name
from khimera.discovery.strategies import FromAPIFinder
from plugins.plugin1 import Plugin1
from plugins.plugin2 import Plugin2
```

<a id="khimera.discovery.strategies.FromAPIFinder.discover"></a>

#### discover()

Discovers plugins specified by the user through the API.

* **Raises:**
  [**TypeError**](https://docs.python.org/3/library/exceptions.html#TypeError) – If a plugin loaded from the API is not an instance of Plugin.
