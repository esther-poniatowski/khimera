# Khimera

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/khimera)](https://github.com/esther-poniatowski/khimera/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Plugin management framework for building extensible Python applications.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Support](#support)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

### Motivation

Designing a plugin system involves two tightly coupled challenges:

- On the host side: implementing a structured and extensible architecture.
- On the plugin side: conforming to a standardized interface and integration protocol.

Without a formalized framework, host developers must manually discover, validate, and register
plugins. Plugin developers must reverse-engineer the host’s expectations. End users need to load
and run plugins reliably at runtime with no visibility into plugin internals.

### Advantages

Khimera decouples plugin infrastructure from logic specific to each application and standardizes
interactions for all three actors in the plugin ecosystem:

- **Host applications**: Define plugin interfaces, discover and register plugins, and coordinate
  how plugins run.
- **Plugin developers**: Implement compliant modules with minimal boilerplate following validated
  specs.
- **End users**: Install and activate plugins transparently, without configuring manually.

---

## Features

- [X] **Plugin specification**: Common interface ensuring plugin compatibility with the host
  application.
- [ ] **Plugin discovery**: Locates plugins from multiple sources, triggered automatically or
  manually by the host or the end user.
- [X] **Plugin validation**: Validates plugin schema conformance and host compatibility.
- [ ] **Plugin registration**: Enables, disables, and organizes plugins for flexible host
  integration.
- [X] **Extensible CLI**: Modular command-line interface extensible with plugin-provided commands
  and composable command groups.

---

## Installation

### Using pip

Install from the GitHub repository:

```bash
pip install git+https://github.com/esther-poniatowski/khimera.git
```

### Using conda

Install from the eresthanaconda channel:

```bash
conda install khimera -c eresthanaconda
```

### From Source

1. Clone the repository:

      ```bash
      git clone https://github.com/esther-poniatowski/khimera.git
      ```

2. Create a dedicated virtual environment:

      ```bash
      cd khimera
      conda env create -f environment.yml
      ```

---

## Usage

### Command Line Interface (CLI)

Display version and platform diagnostics:

```sh
khimera info
```

### Programmatic Usage

Define a plugin model (host application side):

```python
from khimera.plugins.declare import PluginModel
from khimera.core.specifications import FieldSpec

# Define what plugins should provide
model = PluginModel(name="my_host", version="1.0")
model.add(FieldSpec(name="commands", unique=False))
model.add(FieldSpec(name="transforms", unique=True))
```

Create and populate a plugin (plugin developer side):

```python
from khimera.plugins.create import Plugin

plugin = Plugin(model=model, name="my_plugin")
plugin.add("commands", my_command_component)
plugin.add("transforms", my_transform_component)
```

---

## Configuration

### Environment Variables

|Variable|Description|Default|Required|
|---|---|---|---|
|`VAR_1`|Description 1|None|Yes|
|`VAR_2`|Description 2|`false`|No|

### Configuration File

Configuration options are specified in YAML files located in the `config/` directory.

The canonical configuration schema is provided in [`config/default.yaml`](config/default.yaml).

```yaml
var_1: value1
var_2: value2
```

---

## Documentation

- [User Guide](https://esther-poniatowski.github.io/khimera/guide/)
- [API Documentation](https://esther-poniatowski.github.io/khimera/api/)

> [!NOTE]
> Documentation can also be browsed locally from the [`docs/`](docs/) directory.

## Support

**Issues**: [GitHub Issues](https://github.com/esther-poniatowski/khimera/issues)

**Email**: `{{ contact@example.com }}`

---

## Contributing

Please refer to the [contribution guidelines](CONTRIBUTING.md).

---

## Acknowledgments

### Authors & Contributors

**Author**: @esther-poniatowski

**Contact**: `{{ contact@example.com }}`

For academic use, please cite using the GitHub "Cite this repository" feature to
generate a citation in various formats.

Alternatively, refer to the [citation metadata](CITATION.cff).

### Third-Party Dependencies

- **[Library A](link)** - Purpose
- **[Library B](link)** - Purpose

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
