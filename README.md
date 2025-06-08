# Khimera

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2025)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/khimera)](https://github.com/esther-poniatowski/khimera/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Plugin system framework for automating development and integration of package extensions.

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

- On the host application side: implementing a structured and extensible architecture.
- On the plugin side: conforming to a standardized interface and integration protocol.

In the absence of a formalized framework, host developers must manually implement plugin discovery, validation, registration, and integration. Plugin developers, in turn, must reverse-engineer the host’s
expectations. This fragmented process increases complexity and hinders maintainability.

Furthermore, seamless plugin usage by end users requires reliable loading and execution mechanisms
at runtime, with limited visibility into internal plugin logic.

### Advantages

This framework provides a unified infrastructure to automate plugin management and decouple
architectural design from application-specific functionality.

It defines standardized procedures for all three actors in the plugin ecosystem:

- **Host applications**: Define and expose plugin interfaces, manage discovery and registration, and
  coordinate runtime execution.
- **Plugin developers**: Implement compliant modules with minimal boilerplate, following validated
  integration specifications.
- **End users**: Install and activate plugins transparently within the host application environment,
  without manual configuration.

---

## Features

- [X] **Plugin Specification**: Defines a common interface for plugins to ensure compatibility with
  the host application.
- [ ] **Plugin Discovery**: Offers various strategies to locate plugins from multiple sources, that
  can be automatically or manually triggered either by the host application or by the user.
- [X] **Plugin Validation**: Ensures that plugins conform to the expected schema and are compatible
  with the host application.
- [ ] **Plugin Registration**: Enable/disable plugins and organizes their resources to make them
  available to the host application flexibly.
- [X] **Extensible CLI Framework**: Provides a modular command-line interface (CLI) that can be
  extended with new commands provided by plugins. Commands and nested groups can be composed to
  assemble the main application.

---

## Installation

To install the package and its dependencies, use one of the following methods:

### Using Pip Installs Packages

Install the package from the GitHub repository URL via `pip`:

```bash
pip install git+https://github.com/esther-poniatowski/khimera.git
```

### Using Conda

Install the package from the private channel eresthanaconda:

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

To display the list of available commands and options:

```sh
khimera --help
```

### Programmatic Usage

To use the package programmatically in Python:

```python
import khimera
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
