# ADR 0003: Resources Registration for Static Resources

**Status**: Proposed

---

## Problem Statement

Khimera enables **plugin discovery and resource management** for client applications. Plugins may
provide **static resources**, such as configuration files, templates, and data files. These
resources must be registered in a structured way to allow **retrieval, validation, and controlled
access** by the client application.

Central question to be addressed:

How should plugins register static resources in a structured, efficient, and maintainable
manner?

Secondary considerations include:

1. Should plugins declare static resources in metadata files (`pyproject.toml`, JSON) or register
   them via code?
2. How should paths to static resources be managed (relative, absolute, runtime resolution)?
3. Should static resources be immediately loaded into memory, or should they remain indexed until
   needed?

---

## Decision Drivers

- **Modularity**: Static resource registration should be independent of other plugin
  functionalities.
- **Extensibility**: The approach should support additional static resource types without major
  refactoring.
- **Performance**: Registration should avoid unnecessary I/O and memory usage.
- **Usability**: Plugin authors should be able to define static resources in a predictable and
  structured manner.
- **Separation of Concerns**: Static resources should be **tracked separately** from dynamic
  resources (commands, services).

---

## Considered Options

### Option 1: Metadata-Based Registration (`pyproject.toml` or JSON)

- Plugins declare static resources in `pyproject.toml` or a separate metadata file
  (`plugin_resources.json`):

  ```toml
  [tool.my_client_app]
  config_files = ["config.yml"]
  templates = ["templates/email.html"]
  ```

  or in `plugin_resources.json`:

  ```json
  {
    "config_files": ["config.yml"],
    "templates": ["templates/email.html"]
  }
  ```

- No need to execute plugin code to retrieve metadata.

---

### Option 2: Code-Based Registration Function (`register_static_resources()`)

- Plugins implement a function that registers static resources programmatically:

  ```python
  def register_static_resources(resource_registry):
      resource_registry.register("config", "config.yml")
      resource_registry.register("templates", "templates/email.html")
  ```

- Registration happens **at runtime** when the plugin is loaded.

---

### Option 3: Registration via a Khimera-Provided Registrator (Class-Based)

- Plugins import a resource registrator from Khimera and use it to register resources:

  ```python
  from khimera.registry import ResourceRegistrator

  registrator = ResourceRegistrator()
  registrator.register_config("config.yml")
  registrator.register_template("templates/email.html")
  ```

- This removes the need for manual function calls while keeping explicit control over resource
  registration.

---

## Analysis of Options

### Individual Assessment

#### Option 1: Metadata-Based Registration (`pyproject.toml` or JSON)

* **Pros**:
  - **No execution required** – Resources are declared in a structured file.
  - **Allows selective retrieval** – The application can index resources before loading.

* **Cons**:
  - **File I/O overhead** – Parsing metadata files adds an extra step.
  - **No validation at runtime** – If paths are incorrect, errors occur later when trying to access
    resources.

#### Option 2: Code-Based Registration Function (`register_static_resources()`)

* **Pros**:
  - **Explicit control** – The function ensures correct registration at runtime.
  - **Allows conditional logic** – Resources can be registered dynamically based on environment
    settings.

* **Cons**:
  - **Requires executing plugin code** – Plugins must be partially loaded before retrieving
    metadata.
  - **More boilerplate** – Every plugin must define a registration function.

#### Option 3: Registration via a Khimera-Provided Registrator (Class-Based)

* **Pros**:
  - **Centralized registration logic** – Plugins use a **consistent API** to declare resources.
  - **Prevents errors** – The registrator validates paths before adding resources.

* **Cons**:
  - **Slightly more coupling** – Plugins must import the registrator from Khimera.

---

### Summary: Comparison by Criteria

| **Criteria** | **Option 1: Metadata-Based** | **Option 2: Code-Based Function** | **Option 3: Khimera Registrator** |
|-------------|----------------------|----------------------|----------------------|
| **Modularity** | High | High | High |
| **Extensibility** | High | High | High |
| **Performance** | High (No execution required) | Medium (Requires execution) | High (Minimal execution overhead) |
| **Usability** | High (Declarative) | Medium (Function call required) | High (Simple API) |
| **Separation of Concerns** | High (Resources separate from code) | Medium (Execution required) | High (Explicit and structured) |

---

## Conclusions

### Decision

**Chosen option**: Registration via a Khimera-Provided Registrator (Class-Based)

**Justification**:

- **Standardized API**: Ensures consistent resource declaration across plugins.
- **Centralized validation**: Prevents incorrect paths from being registered.
- **Explicit but lightweight**: Combines the clarity of function-based registration with the
  flexibility of metadata-based registration.

**Discarded options**:

- **Metadata-Based Registration**: Requires additional parsing logic, increasing file I/O
  overhead.
- **Code-Based Function Registration**: Requires plugin execution before retrieving metadata,
  making discovery less efficient.

### Final Answers

1. **How should plugins register static resources?**
   Plugins should use `ResourceRegistrator` to declare static resources explicitly.

2. **How should paths to static resources be managed?**
   Paths should be stored relative to the plugin root and resolved dynamically.

3. **Should static resources be loaded into memory immediately?**
   No, only the paths should be indexed; content should be loaded on demand.

---

## Implications

- Implementation of `ResourceRegistrator` is required.
- Client applications must retrieve static resources via the resource registry instead of direct
  file access.
- Validation logic must be added to check registered paths.

---

## See Also

### Related Decisions

- [ADR-0001](./0001-plugin-declaration.md): **Plugin Declaration and Resources**
- [ADR-0002](./0002-resources-registration-commands-services.md): **Resources Registration for
  Commands and Services**

### References and Resources

- [PEP 518 - `pyproject.toml` Specification](https://peps.python.org/pep-0518/)
