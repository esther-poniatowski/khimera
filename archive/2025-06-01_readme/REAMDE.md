# Khimera

Python library for automating plugin system development and usage.

This utility provides standardized procedures for:

1. Host applications that need to support plugins.
2. Plugin providers that develop and distribute plugins.
3. Final users who install and use plugins when they import the host application.

## Features

- [X] **Plugin Specification**: Defines a common interface for plugins to ensure compatibility with
  the host application.
- [ ] **Plugin Discovery**: Offers various strategies to locate plugins from multiple sources, that
  can be automatically or manually triggered either by the host application or by the user.
- [X] **Plugin Validation**: Ensures that plugins conform to the expected schema and are compatible
  with the host application.
- [ ] **Plugin Registration**: Enable/disable plugins and organizes their resources to make them
  available to the host application flexibly.
- [X] **Extensible CLI Framework**: Provides a modulat command-line interface (CLI) that can be
  extended with new commands provided by plugins. Commands and nested groups can be composed to
  assemble the main application.

## Installation

Khimera is a standalone package that can be installed either by a host application and by plugin
providers for a host application (that uses `khimera`).

Usually, users interact directly with the host application and the plugin resources without being
aware of their internal use of the `khimera` library. Optionally, they can also install `khimera` if
needed for advanced management.

Khimera is currently available for installation directly from its GitHub repository.

To install the package and its dependencies in an activated virtual environment:

```sh
pip install git+https://github.com/esther-poniatowski/khimera.git
```

To install a specific version, specify the version tag in the URL:

```sh
pip install git+https://github.com/esther-poniatowski/khimera.git@v0.1.0
```

## Usage

### Declaring a Plugin Model

Any host application that supports plugins must define a plugin model that plugins must adhere to:

```python
from khimera.plugins.declare import PluginModel

model = PluginModel(name='my_plugin', version='1.0.0')
```

The host application specifies its expectations by adding named fields to the plugin model, each
associated with a specific type of plugin component (see below). Fields can be required or optional
in the actual plugin instances, and admit a unique or multiple values.

The `khimera` library standardizes plugins' structure by defining a set of default components that
satisfy various need of the host application. Each type of component is characterized by its own
properties and constraints.

- **Metadata**: General information about the plugin.
- **Commands**: New commands to integrate to the CLI of the host application.
- **API Extensions**: New functions to enrich the API of the host application.
- **Hooks**: Functions to be executed at specific points in the application lifecycle.
- **Assets**: Files to be processed by the host application.

See the documentation of each component for more details about their attributes.

```python
from khimera.plugins.declare import MetaDataSpec, CommandSpec, APIExtensionSpec, HookSpec, AssetSpec

model.add(MetaDataSpec(name='author', required=True, description="Author of the plugin"))

model.add(CommandSpec(name='commands',
                      required=False,
                      unique=False,
                      groups={'setup', 'run'},
                      admits_new_groups=True,
                      description="New commands for the CLI"))

model.add(APIExtensionSpec(name='api-functions',
                           required=False,
                           unique=False,
                           description="New functions for the API"))

model.add(HookSpec(name='on_start',
                   required=False,
                   unique=True,
                   description="Hook to run on application start"))

model.add(AssetSpec(name='input_file',
                    file_ext={'txt', 'csv'},
                    required=False,
                    unique=True,
                    description="File to process"))
```

In addition, the host application can specify dependencies between plugin components, such as
requiring a command to be associated with an asset.

```python
### Creating a Plugin
```

A plugin provider creates a plugin instance that conforms to the plugin model:

```python
from khimera.plugins.declare import Plugin
from host_app import model
```

Initialize the main application:

```python
# cli.py
from khimera import CliApp

app = CliApp()
```

Register a command group:

```python
setup_group = app.add_group("setup", help="Setup project components.")

@setup_group.command("init")
def setup_project():
    print("Project initialized!")

if __name__ == "__main__":
    app()
```

Run:

```sh
python cli.py setup init
```

### Plugin Discovery & Dynamic Registration

Plugins register their commands using the `@register_plugin_command` decorator:

```python
# external_plugin.py
from khimera import register_plugin_command

@register_plugin_command("setup", "custom-tool")
def custom_setup():
    print("Custom setup logic executed!")
```

The main application scans installed plugins and registers their commands automatically:

```python
# cli.py
from khimera.plugin_loader import discover_plugins

discover_plugins()
```

## Plugin System

The application can integrate both internal and external plugins uniformly.

### Internal (Built-in) Plugins

Built-in plugins can be disabled or replaced at runtime:

```python
from khimera import disable_plugin

disable_plugin("setup")
```

### External Plugins

Third-party plugins register themselves via `pyproject.toml`:

```toml
[project.entry-points."khimera.plugins"]
my_plugin = "my_plugin.commands"
```

Once installed:

```sh
pip install my_plugin
```

The plugin will be discovered automatically.

## License

Khimera is licensed under the [GNU License](LICENSE).

## WIP

### Use Cases for Each Discovery Strategy

#### Standard Entry Point Strategy from Installed Pacakages (`importlib.metadata.entry_points`)

- **Purpose:** Automatically discover plugins installed as standard Python packages that declare
  entry points in `pyproject.toml`.
- **Execution:** Executed *automatically* when the host application is imported by the user. Handled
  by the standard package management system for packages installed by the user.
- **Reasoning:**
  - The host application knows in advance which entry point group to scan (`{app_name}.plugins`).
  - Installed plugins are immediately discoverable at runtime without extra configuration.
- **Best suited for:** Users who rely on packaged and installed plugins.

#### Custom Directory Strategy (User-Specified Search Paths)

- **Purpose:** Discover plugins that are not installed as Python packages but are located in
  user-defined directories.
- **Execution:** *Explicitly* triggered by the *user* when using the host application. Manual
  specification of the directories where plugin modules reside.
- **Reasoning:**
  - The host application cannot predict the locations of user-specific plugins.
  - Different projects may be stored at different custom paths on the user's system.
  - Users may want to include or exclude specific directories dynamically.
- **Best suited for:** Advanced use cases where users develop or manage plugins outside of standard
  packaging and installation workflows.

### Additional Considerations

- **Compatible Supports** If both strategies are used, the discovered plugins are **aggregated** by
  the host application. Plugins from different sources are treated uniformly via common interfaces
  (e.g., a `Plugin`, `PluginEntryPoint`, `PluginRegistry`).

### Future Improvements

- **Plugin Caching**: Reduces startup time by avoiding redundant discovery operations in each
  application call.

Forcing a manual refresh:

```sh
python cli.py --reload-plugins
```
