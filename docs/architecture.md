# Project Structure

## Top-level Directory

```tree
khimera/
├── archive/
├── config/
├── docs/
├── src/
├── tests/
├── environment.yml
├── pyproject.toml
├── khimera.code-workspace
├── LICENSE
├── README.md
└── ROADMAP.md
```

- `archive/`: Archived files and logs.
- `config/`: Configuration files for various tools.
- `docs/`: Documentation files in Markdown for direct access, source files and configuration for
  Sphinx.
- `src/`: Source code of the project.
- `tests/`: Unit tests for the project.

For configuration files (e.g. `pyproject.toml`, `khimera.code-workspace`), refer to [the respective
  documentation](docs/configuration.md) for details on their content and purpose.

## Source Code Directory

```tree
src/
└── khimera/
    ├── __init__.py
    ├── core/
    |   ├── __init__.py
    |   ├── components.py
    |   ├── dependencies.py
    |   └── specifications.py
    ├── components/
    |   ├── __init__.py
    |   ├── api.py
    |   ├── assets.py
    |   ├── commands.py
    |   ├── hooks.py
    |   └── metadata.py
    ├── plugins/
    |   ├── __init__.py
    |   ├── create.py
    |   └── declare.py
    ├── management/
    |   ├── __init__.py
    |   ├── register.py
    |   └── validate.py
    ├── discovery/
    |   ├── __init__.py
    |   ├── find.py
    |   └── strategies.py
    └── utils/
```

- `core/`: Core classes and interfaces for defining the building blocks of plugin models and
  instances.
- `components/`: Specific plugin components that typically contribute to a host application
  (metadata, commands, API, hooks, assets).
- `plugins/`: Factories to declare plugin models and create plugin instances.
- `management/`: Management of the plugins across their lifecycle in the host application.
- `discovery/`: Discovery of plugins and their components in the host application.
- `utils/`: Utility functions and classes used across the project.
