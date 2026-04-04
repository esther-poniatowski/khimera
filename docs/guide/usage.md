# Usage

Khimera structures the interaction between three actors: host applications that
declare plugin interfaces, plugin developers that implement those interfaces,
and end users that install and activate plugins.

## Define a Plugin Model

A host application declares what plugins can provide through a `PluginModel`.
Each field in the model pairs a name with a concrete `FieldSpec` subclass that
constrains the corresponding component type.

```python
from khimera.plugins.declare import PluginModel
from khimera.components.metadata import MetaDataSpec
from khimera.components.commands import CommandSpec
from khimera.components.hooks import HookSpec
from khimera.components.assets import AssetSpec
from khimera.components.api import APIExtensionSpec

model = PluginModel(name="my_host", version="1.0")
```

### Metadata Fields

`MetaDataSpec` constrains a metadata value to a specific Python type. Metadata
fields are unique by default (one value per plugin).

```python
model.add(MetaDataSpec(name="author", valid_type=str, required=True))
model.add(MetaDataSpec(name="license", valid_type=str))
```

### Command Fields

`CommandSpec` constrains CLI commands contributed by plugins. Commands can be
organized into sub-command groups.

```python
model.add(CommandSpec(
    name="commands",
    groups={"setup", "run"},
    admits_new_groups=True,
    admits_top_level=False,
    unique=False,
))
```

- `groups` -- allowed sub-command group names.
- `admits_new_groups` -- whether plugins may create new groups beyond those listed.
- `admits_top_level` -- whether plugins may add top-level commands.

### Hook Fields

`HookSpec` enforces a strict function signature contract: argument names, types,
ordering, and return type must match exactly.

```python
from collections import OrderedDict

model.add(HookSpec(
    name="on_start",
    arg_types=OrderedDict({"config": dict, "verbose": bool}),
    return_type=bool,
    required=True,
    unique=True,
))
```

### Asset Fields

`AssetSpec` constrains static resources (files) contributed by plugins. The
`file_ext` parameter restricts accepted file formats.

```python
model.add(AssetSpec(
    name="stylesheet",
    file_ext=(".css", ".scss"),
    unique=True,
))
```

### API Extension Fields

`APIExtensionSpec` constrains functions or classes that extend the host API. The
`valid_types` parameter restricts accepted object types; `check_inheritance`
switches between `isinstance` and `issubclass` checks.

```python
from types import FunctionType

model.add(APIExtensionSpec(
    name="transforms",
    valid_types=(FunctionType,),
    check_inheritance=False,
    unique=False,
))
```

### Dependency Specifications

`PredicateDependency` enforces cross-field constraints. A predicate function
receives `ComponentSet` arguments keyed by field name and returns a boolean.

```python
from khimera.core.dependencies import PredicateDependency

def hook_requires_asset(on_start, stylesheet):
    """A hook must be paired with a stylesheet."""
    return bool(on_start) == bool(stylesheet)

model.add(PredicateDependency(
    name="hook_asset_link",
    predicate=hook_requires_asset,
    fields=("on_start", "stylesheet"),
))
```

### Filter Model Fields

`PluginModel.filter` selects fields by category, uniqueness, or requirement
status.

```python
from khimera.components.hooks import Hook

hook_fields = model.filter(category=Hook)
required_fields = model.filter(required=True)
multi_fields = model.filter(unique=False)
```

## Create a Plugin

A plugin developer imports the model from the host application and populates
fields with concrete `Component` subclasses.

```python
from khimera.plugins.create import Plugin
from khimera.components.metadata import MetaData
from khimera.components.commands import Command
from khimera.components.hooks import Hook
from khimera.components.assets import Asset

plugin = Plugin(model=model, name="my_plugin", version="0.2.0")
```

### Add Components

`Plugin.add` accepts a field key and a component instance. The `add` method
supports chaining.

```python
plugin.add("author", MetaData(name="author", value="Alice"))

def setup_env(config: dict, verbose: bool) -> bool:
    print("Setting up environment")
    return True

plugin.add("on_start", Hook(name="setup_hook", func=setup_env))

def greet():
    print("Hello from plugin")

plugin.add("commands", Command(name="greet", func=greet, group="run"))

plugin.add("stylesheet", Asset(
    name="dark_theme",
    file_path="assets/dark.css",
    package="my_plugin_pkg",
))
```

### Remove Components

`Plugin.remove` drops a single component by name, or all components under a
field key when no component name is given.

```python
plugin.remove("commands", comp_name="greet")
plugin.remove("stylesheet")
```

### Retrieve Plugin Components

`Plugin.get` returns a `ComponentSet` (list of components) for a given field
key. `Plugin.filter` narrows results by component category.

```python
hooks = plugin.get("on_start")
all_commands = plugin.filter(category=Command)
```

## Validate a Plugin

`PluginValidator` checks a plugin instance against its model. The `validate`
method returns a `ValidationResult` dataclass with five diagnostic fields.

```python
from khimera.management.validate import PluginValidator

validator = PluginValidator(plugin)
result = validator.validate()

if not result.is_valid:
    print("Missing required fields:", result.missing)
    print("Unknown fields:", result.unknown)
    print("Non-unique fields:", result.not_unique)
    print("Invalid components:", result.invalid)
    print("Unsatisfied dependencies:", result.deps_unsatisfied)
```

### Extract Valid Components

`PluginValidator.extract` returns a copy of the plugin with invalid, unknown,
and non-unique components removed.

```python
clean_plugin = validator.extract()
```

## Discover Plugins

Discovery strategies locate plugin instances before registration.

### From Installed Packages

`FromInstalledFinder` scans `importlib.metadata` entry points. Plugin providers
declare entry points in `pyproject.toml`:

```toml
[project.entry-points.'my_host.plugins']
my_plugin = "my_plugin_pkg.plugins:plugin"
```

The host application discovers all installed plugins:

```python
from khimera.discovery.strategies import FromInstalledFinder

finder = FromInstalledFinder(app_name="my_host")
finder.discover()
```

### Query Discovered Plugins

`PluginFinder.get` returns all matches by name; `PluginFinder.get_one` returns
exactly one match or raises `PluginNotFoundError` / `AmbiguousLookupError`.
`PluginFinder.filter` narrows by model.

```python
all_matches = finder.get("my_plugin")
exact = finder.get_one("my_plugin", version="0.2.0")
model_plugins = finder.filter(model=model)
```

### From the API

`FromAPIFinder` accepts `PluginEntryPoint` objects for local development
scenarios where plugins are not yet packaged.

```python
from khimera.discovery.find import PluginEntryPoint
from khimera.discovery.strategies import FromAPIFinder

ep = PluginEntryPoint(name="dev_plugin", value="my_pkg.plugins:plugin")
finder = FromAPIFinder(ep)
```

## Register Plugins

`PluginRegistry` stores validated plugins and exposes their components.

```python
from khimera.management.register import PluginRegistry

registry = PluginRegistry()
registry.register(plugin)
```

`register` validates the plugin first. If validation fails, a
`PluginValidationError` carries the full `ValidationResult`.

### Retrieve Registered Components

`PluginRegistry.get` retrieves components by field key, optionally filtered by
component name and enabled status.

```python
hooks = registry.get("on_start", name=None)
specific = registry.get("commands", name="greet")
```

### Enable and Disable Plugins

Plugins registered with `enable_by_default=True` (the default) are immediately
active. `disable` hides a plugin's components from `get` queries without
removing the plugin from the registry.

```python
registry.disable("my_plugin")
registry.enable("my_plugin")
```

### Conflict Resolution

When a newly registered plugin shares a name with an existing one, the registry
delegates to a `ConflictResolution` strategy.

| Strategy            | Behavior                                               |
|---------------------|--------------------------------------------------------|
| `RaiseOnConflict`   | Raises `PluginConflictError` (default).                |
| `OverrideOnConflict`| Replaces the existing plugin, emits a warning.         |
| `IgnoreOnConflict`  | Keeps the existing plugin, discards the new one.       |

```python
from khimera.management.register import PluginRegistry, OverrideOnConflict, ConflictResolver

registry = PluginRegistry(
    resolver=ConflictResolver(strategy=OverrideOnConflict()),
)
```

## Integrate with a CLI

`CliApp` extends `typer.Typer` with structured command and group registration.
Host applications use `CliApp` to build a CLI that plugins can extend through
`Command` components.

```python
from khimera.cli.app import CliApp

cli = CliApp()
cli.add_group("run", help_msg="Run commands")

def hello():
    print("Hello")

cli.add_command(name="hello", function=hello, in_group="run")
```

### Register Plugin Commands

After registration, the host application iterates over registered `Command`
components and wires each into the CLI.

```python
for cmd in registry.get("commands", name=None):
    cli.add_command(name=cmd.name, function=cmd.func, in_group=cmd.group)
```

### Query the CLI

`CliApp.has_group` and `CliApp.has_command` check whether groups or commands
exist. `CliApp.get_group` retrieves a group as a `CliApp` instance.

```python
assert cli.has_group("run")
assert cli.has_command("hello", in_group="run")

run_group = cli.get_group("run")
```

## Exception Hierarchy

All khimera exceptions inherit from `KhimeraError`.

| Exception                | Raised when                                             |
|--------------------------|---------------------------------------------------------|
| `PluginValidationError`  | A plugin fails validation; carries `ValidationResult`.  |
| `PluginConflictError`    | A naming conflict occurs during registration.           |
| `PluginNotFoundError`    | A requested plugin cannot be found.                     |
| `ComponentError`         | A component-level error occurs (duplicate, missing key).|
| `AmbiguousLookupError`   | A lookup matches multiple results where one is expected.|

```python
from khimera.exceptions import (
    KhimeraError,
    PluginValidationError,
    PluginConflictError,
    PluginNotFoundError,
    ComponentError,
    AmbiguousLookupError,
)
```

## Next Steps

- [Architecture](../architecture.md) -- Design and module organization.
- [API Reference](../api/index.md) -- Full Python API documentation.
