<a id="exceptions"></a>

# Exceptions

Domain-specific exception hierarchy.

<a id="module-khimera.exceptions"></a>

<a id="khimera-exceptions"></a>

## khimera.exceptions

Domain-specific exception hierarchy for the khimera framework.

> **See also**
>
> [`khimera.management.validate`](management.md#module-khimera.management.validate)
> : Validation pipeline that produces ValidationResult.
>
> [`khimera.management.register`](management.md#module-khimera.management.register)
> : Registration pipeline that raises on conflicts.

<a id="khimera.exceptions.KhimeraError"></a>

### *exception* khimera.exceptions.KhimeraError

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)

Base exception for all khimera framework errors.

<a id="khimera.exceptions.PluginValidationError"></a>

### *exception* khimera.exceptions.PluginValidationError(result)

Bases: [`KhimeraError`](#khimera.exceptions.KhimeraError)

Raised when a plugin fails validation against its model.

<a id="khimera.exceptions.PluginValidationError.result"></a>

#### result

Structured diagnostics from the validation pipeline.

<a id="khimera.exceptions.PluginConflictError"></a>

### *exception* khimera.exceptions.PluginConflictError

Bases: [`KhimeraError`](#khimera.exceptions.KhimeraError)

Raised when a naming conflict occurs during plugin registration.

<a id="khimera.exceptions.PluginNotFoundError"></a>

### *exception* khimera.exceptions.PluginNotFoundError

Bases: [`KhimeraError`](#khimera.exceptions.KhimeraError)

Raised when a requested plugin cannot be found.

<a id="khimera.exceptions.ComponentError"></a>

### *exception* khimera.exceptions.ComponentError

Bases: [`KhimeraError`](#khimera.exceptions.KhimeraError)

Raised for component-level errors (duplicates, missing keys).

<a id="khimera.exceptions.AmbiguousLookupError"></a>

### *exception* khimera.exceptions.AmbiguousLookupError

Bases: [`KhimeraError`](#khimera.exceptions.KhimeraError)

Raised when a lookup matches multiple results where one was expected.
