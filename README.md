# Khimera

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](docs/guide/installation.md)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/khimera)](https://github.com/esther-poniatowski/khimera/commits/main)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.12-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Equips Python applications with a structured plugin system.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

### Motivation

A plugin system poses two tightly coupled challenges: implementing a structured and
extensible architecture on the host side, and conforming to a standardized interface
on the plugin side. Without a formalized framework, host
developers must manually discover, validate, and register plugins, while plugin
developers must reverse-engineer the host's expectations.

### Advantages

- **Host applications** — define plugin interfaces, discover and register plugins,
  and coordinate execution.
- **Plugin developers** — implement compliant modules with minimal boilerplate
  following validated specs.
- **End users** — install and activate plugins transparently.

---

## Features

- [X] **Plugin specification**: Define a common interface ensuring plugin compatibility
  with the host application.
- [ ] **Plugin discovery**: Locate plugins from multiple sources, triggered
  automatically or manually.
- [X] **Plugin validation**: Validate plugin schema conformance and host
  compatibility.
- [ ] **Plugin registration**: Enable, disable, and organize plugins for flexible
  host integration.
- [X] **Extensible CLI**: Extend the command-line interface with commands that plugins
  provide.

---

## Quick Start

Define a plugin model (host side):

```python
from khimera.plugins.declare import PluginModel
from khimera.core.specifications import FieldSpec

model = PluginModel(name="my_host", version="1.0")
model.add(FieldSpec(name="commands", unique=False))
```

Create a plugin (developer side):

```python
from khimera.plugins.create import Plugin

plugin = Plugin(model=model, name="my_plugin")
plugin.add("commands", my_command_component)
```

---

## Documentation

| Guide | Content |
| ----- | ------- |
| [Installation](docs/guide/installation.md) | Prerequisites, pip/conda/source setup |
| [Usage](docs/guide/usage.md) | Workflows and detailed examples |
| [Architecture](docs/architecture.md) | Design, module organization |
| [Dependencies](docs/dependencies.md) | Dependency graph |

Full API documentation and rendered guides are also available at
[esther-poniatowski.github.io/khimera](https://esther-poniatowski.github.io/khimera/).

---

## Contributing

Contribution guidelines are described in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Acknowledgments

### Authors

**Author**: @esther-poniatowski

For academic use, the GitHub "Cite this repository" feature generates citations in
various formats. The [citation metadata](CITATION.cff) file is also available.

---

## License

This project is licensed under the terms of the
[GNU General Public License v3.0](LICENSE).
