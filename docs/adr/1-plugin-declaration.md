# ADR 0001: Plugin Declaration and Resources

**Status**: Proposed

---

## Problem Statement

Khimera provides **plugin discovery and management** for client applications. To enable **structured
and predictable communication** between plugins and the main application, plugins must declare
their existence and the resources they provide.

Central question to be addressed:

How should plugins declare themselves and their provided resources to enable efficient discovery,
structured metadata retrieval, and flexible resource registration?

Secondary considerations include:

1. What mechanism should be used for plugin discovery?
2. How should plugins specify different types of resources (commands, programmatic extensions,
   static files)?
3. Should resource metadata be retrievable without loading the plugin module?

---

## æDecision Drivers

- **Modularity**: The plugin system should allow independent extension of different aspects of the
  application.
- **Extensibility**: The declaration mechanism should support additional resource types without
  major refactoring.
- **Performance**: Discovery and metadata retrieval should be efficient, avoiding unnecessary file
  reads or imports.
- **Usability**: Plugin authors should be able to declare resources in a structured and predictable
  manner.
- **Separation of Concerns**: Plugin discovery, metadata retrieval, and resource registration should
  remain distinct processes.

---

## **Considered Options**

### Option 1: Declaration via Entry Points

- Plugins register themselves using Python’s `importlib.metadata.entry_points()`:

  ```toml
  [project.entry-points."khimera.plugins"]
  my_plugin = "my_plugin"
  ```

- The plugin module must define functions to expose resources dynamically:

  ```python
  def register_commands(cli):
      cli.command("my-command-1")(plugin_function)
  ```

- Resource metadata is only available after loading the module.

---

### Option 2: Declaration in `pyproject.toml`

- Plugins declare themselves under a dedicated metadata section in `pyproject.toml`:

  ```toml
  [tool.my_client_app]
  plugin_name = "my_plugin"
  commands = ["my-command-1", "my-command-2"]
  services = ["my_plugin.module.my_function"]
  config_files = ["config.yml"]
  templates = ["template.html"]
  ```

- No module import is required to retrieve metadata.
- Resource paths and registration methods are predefined.

---

### Option 3: Hybrid Approach (Entry Points + `pyproject.toml`)

- Entry points are used for plugin discovery, ensuring dynamic registration:

  ```toml
  [project.entry-points."khimera.plugins"]
  my_plugin = "my_plugin"
  ```

- Structured metadata is retrieved from `pyproject.toml`:

  ```toml
  [tool.my_client_app]
  commands = ["command_1"]
  services = ["service_1"]
  ```

- Resource registration functions (`register_commands()`, `register_services()`) are still available
  but not required for metadata retrieval.

---

## Analysis of Options

### Individual Assessment

#### Option 1: Entry Points

* **Pros**:
  - Efficient discovery (uses built-in Python mechanism).
  - Fully dynamic (detects installed plugins automatically).

* **Cons**:
  - No structured metadata before loading → The plugin must be imported to retrieve its
    resources.
  - No support for categorizing resources natively.

#### Option 2: `pyproject.toml`

* **Pros**:
  - All metadata is available without loading the plugin.
  - Client applications can define a structured schema for plugin metadata.

* **Cons**:
  - Slower than entry points (requires file reads and parsing).
  - Plugins must manually add metadata instead of automatic discovery.

#### Option 3: Hybrid Approach (Chosen Solution)

* **Pros**:
  - Combines efficient discovery (entry points) with structured metadata (`pyproject.toml`).
  - Client applications can enforce metadata validation.

* **Cons**:
  - Requires two steps (entry point lookup + metadata retrieval).

---

### **Summary: Comparison by Criteria**

| **Criteria** | **Option 1: Entry Points** | **Option 2: `pyproject.toml`** | **Option 3: Hybrid** |
|-------------|----------------------|----------------------|----------------------|
| **Modularity** |  High |  High |  High |
| **Extensibility** |  Low |  High |  High |
| **Performance** |  High |  Low |  High |
| **Usability** |  Medium |  High |  High |
| **Separation of Concerns** |  Medium |  High |  High |

---

## Conclusions

### Decision

**Chosen option**: Hybrid Approach (Entry Points + `pyproject.toml`)

**Justification**:

- Entry points ensure efficient discovery, enabling plugins to be found dynamically.
- Metadata in `pyproject.toml` provides structured resource declarations without needing to
  import the module.
- This approach balances performance, usability, and flexibility.

### Final Answers

1. **How should plugins declare themselves and their provided resources?**
   Plugins should be discovered via entry points (`khimera.plugins`), and structured metadata
   should be stored in `pyproject.toml` under `[tool.my_client_app]`.

2. **Should resource metadata be retrievable without loading the plugin module?**
   Yes, by reading `pyproject.toml`. Commands and services can still be registered dynamically
   after loading.

---

## Implications

- PluginFinder must support both entry point discovery and metadata retrieval.
- Client applications must define their expected metadata schema for plugin validation.
- Resource registration will be a two-step process:
  1. Discover plugins via entry points.
  2. Load metadata from `pyproject.toml` before importing the module.

---

## See Also

### References and Resources

- [Python Entry Points - Official Documentation](https://packaging.python.org/en/latest/specifications/entry-points/)
- [PEP 518 - `pyproject.toml` Specification](https://peps.python.org/pep-0518/)
