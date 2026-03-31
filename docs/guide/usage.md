# Usage

Khimera provides a structured plugin system for Python applications. The
framework addresses three actors: host applications that define plugin
interfaces, plugin developers that implement compliant modules, and end users
that install and activate plugins.

## Defining a Plugin Model (Host Side)

A plugin model declares what plugins must provide. Each field specification
defines a named slot with uniqueness constraints:

```python
from khimera.plugins.declare import PluginModel
from khimera.core.specifications import FieldSpec

model = PluginModel(name="my_host", version="1.0")
model.add(FieldSpec(name="commands", unique=False))
model.add(FieldSpec(name="transforms", unique=True))
```

The `unique=True` constraint ensures that only one plugin can register a
component for that slot, preventing conflicts.

## Creating a Plugin (Developer Side)

A plugin implements the model's interface by populating the declared slots:

```python
from khimera.plugins.create import Plugin

plugin = Plugin(model=model, name="my_plugin")
plugin.add("commands", my_command_component)
plugin.add("transforms", my_transform_component)
```

## Validating a Plugin

Validation checks schema conformance and host compatibility before
registration:

```python
from khimera.core.validation import validate_plugin

result = validate_plugin(plugin, model)
if not result.is_valid:
    for error in result.errors:
        print(error)
```

## Extending the CLI

Plugin-provided commands integrate into the host application's CLI through
composable command groups:

```python
from khimera.cli import PluginCommandGroup

group = PluginCommandGroup(model=model)
group.register(plugin)
```

## Next Steps

- [Architecture](../architecture.md) — Design, module organization.
- [API Reference](../api/index.md) — Python API documentation.
