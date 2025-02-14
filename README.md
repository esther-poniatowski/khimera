# Climera

**Climera** is a Python library designed for structured CLI management with modular and dynamic command registration, nested CLI structures, and automatic discovery of internal and external plugins.

## Key Features

- **Structured CLI Framework**: Allows nested command groups, extending the `Typer` library.
- **Dynamic Command Registery**: Commands and groups can be composed and retrieved modularly at runtime to assemble the main application. 
- **Automatic Plugin Discovery**: Supports internal (built-in) and external (third-party) plugins in a uniform process.  
- **Plugin Caching**: Reduces startup time by avoiding redundant discovery operations in each application call.  


## Installation

Climera is a standalone package that can be installed via pip:
```sh
pip install climera
```

## Usage

### Creating a CLI

Initialize the main application:

```python
# cli.py
from climera import CliApp

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
from climera import register_plugin_command

@register_plugin_command("setup", "custom-tool")
def custom_setup():
    print("Custom setup logic executed!")
```

The main application scans installed plugins and registers their commands automatically: 

```python
# cli.py
from climera.plugin_loader import discover_plugins

discover_plugins()
```


## Plugin System

The application can integrate both internal and external plugins uniformly.

### Internal (Built-in) Plugins

Built-in plugins can be disabled or replaced at runtime:

```python
from climera import disable_plugin

disable_plugin("setup")
```

### External Plugins

Third-party plugins register themselves via `pyproject.toml`:

```toml
[project.entry-points."climera.plugins"]
my_plugin = "my_plugin.commands"
```

Once installed:
```sh
pip install my_plugin
```

The plugin will be discovered automatically.


## Plugin Caching

To prevent unnecessary rediscovery each time the applicaiton is called, plugins are cached.  

Forcing a manual refresh:

```sh
python cli.py --reload-plugins
```


## License
Climera is licensed under the GNU [License](LICENSE).
 

