# ADR 0002: Resources Registration for Commands and Services

**Status**: Proposed

---

## Problem Statement

Khimera provides a **plugin discovery and resource management system** for client applications.
Plugins may extend the application by **registering commands and programmatic services**, which
should be integrated into the main application dynamically.

Central question to be addressed:

How should plugins register commands and services in a structured, flexible, and maintainable
manner?

Secondary considerations include:

1. Should plugins register their resources via explicit function calls or declarative
   decorators?
2. How should the registration process interact with the main application and Khimera?
3. How can multiple plugins register similar resources without conflicts?

---

## Decision Drivers

- **Modularity**: The registration mechanism should allow plugins to define independent extensions
  without modifying the core system.
- **Extensibility**: The approach should support future adaptations, including additional types of
  registrable resources.
- **Usability**: Plugin authors should be able to define resources in an intuitive and predictable
  manner.
- **Separation of Concerns**: The registration logic should be independent of plugin discovery and
  execution.
- **Correctness**: The system should prevent registration conflicts and ensure deterministic
  behavior.

---

## Considered Options

### Option 1: Function-Based Registration (Explicit)

- Plugins implement explicit registration functions that must be called after discovery.
- Each function receives a registration interface (e.g., `cli`, `service_registry`) and adds its
  resources.

  ```python
  def register_commands(cli):
      @cli.command(name="plugin-cmd")
      def plugin_command():
          print("Plugin Message")

  def register_services(service_registry):
      service_registry.register("plugin-function", plugin_function)
  ```

### Option 2: Decorator-Based Registration (Declarative)

- Plugins use predefined decorators imported from Khimera to register resources.
- The decorators automatically execute registration when the module is loaded.

  ```python
  from khimera.decorators import command, service

  @command("plugin-cmd")
  def plugin_command():
      print("Plugin Message")

  @service("plugin-function")
  def plugin_function(text):
      return f"Processed: {text}"
  ```

- No explicit registration function is required.

### Option 3: Registration via a Khimera-Provided Registrator

- Plugins import a registration function or class from Khimera and use it explicitly.
- The registrator stores the registered resources in a structured way, instead of relying on
  decorators or explicit function calls.

#### Approach 1: Function-Based Registrator

```python
from khimera.registry import register_command, register_service

register_command("plugin-cmd", plugin_command)
register_service("plugin-function", plugin_function)
```

- Commands and services are explicitly registered using Khimera’s registrator.
- This removes the need for decorators or explicit registration functions inside plugins.

#### Approach 2: Class-Based Registrator

```python
from khimera.registry import PluginRegistrator

registrator = PluginRegistrator()

registrator.register_command("plugin-cmd", plugin_command)
registrator.register_service("plugin-function", plugin_function)
```

- A dedicated object manages plugin resources, allowing additional control over registration.

---

## Analysis of Options

### Individual Assessment

#### Option 1: Function-Based Registration (Explicit)

* **Pros**:
  - **Separation of concerns**: Registration happens explicitly in a dedicated function.
  - **Control**: Plugins can define **when and how** their resources are registered.

* **Cons**:
  - **Requires explicit calls**: Plugins must manually invoke `register_commands()` and
    `register_services()`.
  - **Boilerplate code**: Every plugin must define registration functions.

#### Option 2: Decorator-Based Registration (Declarative)

* **Pros**:
  - **Minimal boilerplate**: Resources are automatically registered when the module is loaded.
  - **Simplicity**: Functions are marked as commands or services declaratively.

* **Cons**:
  - **Implicit behavior**: Registration happens as a side effect of module loading.
  - **Potential conflicts**: Multiple plugins registering the same function name may lead to
    unintended overrides.

#### Option 3: Registration via a Khimera-Provided Registrator

* **Pros**:
  - **Modularity and Structure**: Plugin authors do not need to define custom registration logic.
  - **Expliciteness$*: No hidden side effects upon module import.
  - **Standardization**, ensuring a consistent API.

* **Cons**:
  - Plugins must import and use Khimera’s registrator.
  - Less flexible than a function-based approach, as it relies on a pre-defined registration API.

---

### **Summary: Comparison by Criteria**

| **Criteria** | **Option 1: Function-Based** | **Option 2: Decorator-Based** | **Option 3: Khimera Registrator** |
|-------------|----------------------|----------------------|----------------------|
| **Modularity** | High | High | High |
| **Extensibility** | High | High | High |
| **Usability** | Medium (manual function calls) | High (automatic registration) | High (clear API) |
| **Separation of Concerns** | High (explicit process) | Medium (implicit behavior) | High (centralized registry) |
| **Correctness** | High (clear execution order) | Medium (potential conflicts) | High (structured validation) |

---

## Conclusions

### Decision

**Chosen option**: Registration via a Khimera-Provided Registrator (Class-Based)

**Justification**:

- **Standardized approach**: Ensures a consistent API for plugins, making extensions easier to
  manage.
- **No hidden side effects**: Unlike decorators, plugins must explicitly register their resources,
  reducing accidental overrides.
- **Centralized control**: The registrator can validate, track, and resolve conflicts during
  registration.

**Discarded options**:

- **Function-Based Registration**: Requires explicit calls for every plugin, leading to unnecessary
  complexity.
- **Decorator-Based Registration**: Implicit behavior leads to conflicts, making debugging harder.

### Final Answers

1. **How should plugins register their resources?**
   Plugins should import `PluginRegistrator` from Khimera and use its `register_command()` and
   `register_service()` methods to register their resources.

2. **How should the registration process interact with the main application and Khimera?**
   The registrator stores registered resources centrally, allowing the main application to retrieve
   and manage them.

3. **How can multiple plugins register similar resources without conflicts?**
   The registrator validates and resolves conflicts before adding resources. If multiple versions
   exist, they can be stored as alternatives.

---

## Implications

- Implementation of `PluginRegistrator` is required.
- Conflict resolution must be handled during registration.
- Documentation must clearly define how plugins use the registrator.
- Existing function-based and decorator-based registration should be deprecated in favor of this
  approach.

---

## See Also

### Related Decisions

- [ADR-0001](./0001-plugin-declaration.md): Plugin Declaration and Resources

### References and Resources

- [Python Decorators - Official Documentation](https://docs.python.org/3/library/functools.html)
- [Typer Documentation](https://typer.tiangolo.com/)
