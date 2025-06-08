"""
khimera.core
============

Core classes and interfaces for defining the building blocks of plugin models and instances.

Modules
-------
components
    Base classes for defining components in plugin models and instances.
specifications
    Base classes for defining constraints specifications for components within a plugin model.
dependencies
    Base and concrete classes for defining dependencies between components in a plugin model.

Notes
-----
**Components and Specifications**

Each specification defines constraints that plugin components should satisfy to be supported by the
host application.

The association between specifications in a model and components in actual plugin instances occurs
at two levels:

1. At the class level, each `FieldSpec` sub-class references a `Component` sub-class on which the
   constraints apply (via the `COMPONENT_TYPE` class attribute).
2. At the plugin instance level (during the plugin creation process), each candidate component is
   stored in the plugin instance under a key corresponding to a `FieldSpec` instance's name in the
   model. This mapping ensures that each component can be validated against the corresponding
   specification in the model and be recognized by the host application.

**Extensibility**

The system provides multiple strategies for defining custom components and extending validation
constraints, ranging from simple type checks to complex structural validations.

Extension Strategies:

1. Using Predefined Component and Specification Types: The `khimera.components` module provides
  built-in components and their associated specification rules (e.g. `MetaData`/`MetaDataSpec`,
  `APIExtension`/`APIExtensionSpec`, `Command`/`MCommandSpec`, `Hook`/`HookSpec`,
  `Asset`/`AssetSpec`). These components include default validation logic tailored to common plugin
  elements.

2. Extending Component and Specification Classes: The base class interfaces allow the host
  application to define new types of constraints that are not covered by the built-in
  specifications:

  - The `FieldSpec` and `Component` classes can be subclassed to implement new component categories
    or to override validation rules for existing ones.
  - The `Spec` class can be subclassed to establish complex relational constraints between
    components that depend on each other to be meaningful in the host application's context.

**Validation Strategies**

By balancing strict integration constraints and general-purpose validations, the system supports a
broad range of plugin architectures, ensuring both flexibility and maintainability.

Specifically, the host application can enforce constraints at varying levels of strictness and
granularity, depending on how components integrate into its execution flow:

- Strict Constraints for Integration Points: Components that interact directly with the host
  application (e.g. hooks, assets) require precise constraints to integrate seamlessly with the host
  application's logics. For instance, the host application may require that each plugin provides a
  single hook with determined inputs and outputs.
- General Constraints for Client-Facing Components: Components used primarily by client code or end
  users (e.g., commands, API extensions) may follow more flexible constraints. For instance, the
  host application may require that all plugin-provided commands reside within a specific namespace.

"""
