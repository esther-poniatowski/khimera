"""
khimera.management.register
========================

Registers plugins on the host application side.

Classes
-------
ConflictResolution (Protocol)
    Strategy interface for resolving naming conflicts during registration.
RaiseOnConflict
    Raises ``PluginConflictError`` when a conflict occurs.
OverrideOnConflict
    Replaces the existing element with the new one.
IgnoreOnConflict
    Keeps the existing element and discards the new one.
ConflictResolver
    Applies a ``ConflictResolution`` strategy to resolve conflicts.
PluginRegistry

See Also
--------
"""
from typing import Dict, List, TypeVar, Optional, Protocol, runtime_checkable
import warnings

from khimera.utils.factories import TypeConstrainedDict
from khimera.plugins.create import Plugin
from khimera.core.components import Component, ComponentSet
from khimera.management.validate import PluginValidator, ValidationResult
from khimera.exceptions import PluginConflictError, PluginValidationError, PluginNotFoundError

E = TypeVar("E", bound=Plugin | Component)
"""Type variable for elements in the registry."""


# --- Conflict Resolution Strategies ---------------------------------------------------------------


@runtime_checkable
class ConflictResolution(Protocol):
    """Protocol for conflict resolution strategies.

    Implementations decide what happens when a newly registered element has the same name as an
    existing one.
    """

    def resolve(self, new: Plugin | Component) -> Plugin | Component | None:
        """Resolve a naming conflict for *new*.

        Returns
        -------
        Plugin | Component | None
            The element to keep in the registry, or ``None`` to discard the new element.

        Raises
        ------
        PluginConflictError
            If the strategy forbids conflicts.
        """
        ...


class RaiseOnConflict:
    """Raises ``PluginConflictError`` when a conflict occurs."""

    def resolve(self, new: Plugin | Component) -> None:
        raise PluginConflictError(f"Aborted: name '{new.name}' already registered.")


class OverrideOnConflict:
    """Replaces the existing element with the new one, emitting a warning."""

    def resolve(self, new: Plugin | Component) -> Plugin | Component:
        warnings.warn(f"Overridden: name '{new.name}' already registered.", UserWarning)
        return new


class IgnoreOnConflict:
    """Keeps the existing element and discards the new one, emitting a warning."""

    def resolve(self, new: Plugin | Component) -> None:
        warnings.warn(f"Ignored: name '{new.name}' already registered.", UserWarning)
        return None


class ConflictResolver:
    """Applies a ``ConflictResolution`` strategy to resolve conflicts.

    Attributes
    ----------
    strategy : ConflictResolution
        Strategy to apply to resolve conflicts between plugins.
    """

    def __init__(self, strategy: ConflictResolution | None = None):
        self.strategy: ConflictResolution = strategy or RaiseOnConflict()

    def resolve(self, new: E) -> E | None:
        """Delegate conflict resolution to the configured strategy.

        Returns
        -------
        E | None
            Resolved element to register, or ``None`` to discard.
        """
        return self.strategy.resolve(new)


# --- Plugin Registry ------------------------------------------------------------------------------


class PluginRegistry:
    """
    Stores and manage plugins, resolve conflicts and provide components retrieval.

    Attributes
    ----------
    resolver : ConflictResolver
        Applies a ``ConflictResolution`` strategy to resolve conflicts when registering plugins.
    validator_type : Type[PluginValidator], default=PluginValidator
        Validator class to check the plugin structure and components against its model.
    enable_by_default : bool
        Whether to enable plugins by default when registering them.
    plugins : Dict[str, Plugin]
        Registered plugins by name.
    enabled : List[str]
        List of enabled plugins, whose components are available directly via the `get` method.
    components : Dict[str, ComponentSet]
        Mapping of fields' keys (from the model) to the actual components provided by the plugins.
        Keys: Field for a type of components specified in the model.
        Values: All the components registered under this key across the validated plugins.

    Examples
    --------
    Initialize a plugin registry:

    >>> registry = PluginRegistry()

    Define a plugin with two components:

    >>> plugin = Plugin('my_plugin', '1.0.0')
    >>> def plugin_hook(arg) -> bool:
    ...     print(arg)
    >>> plugin.add('hook', Hook(name="my_hook", callable=plugin_hook))
    >>> plugin.add('input_file', Asset(name="logo", package="my_package", file_path="assets/logo.png"))

    Register the plugin in the registry:

    >>> registry.register(plugin)
    >>> print(registry.plugins)
    {'my_plugin': Plugin(name='my_plugin', version='1.0.0', ...)}

    Get all the components under a specific key:

    >>> hooks = registry.get('hook')
    >>> print(hooks)
    [Hook(name='my_hook')]

    Disable the plugin:

    >>> registry.disable('my_plugin')
    >>> print(registry.enabled)
    []

    Notes
    -----
    So far, a single version per plugin is allowed in the registry.

    Enabling and disabling plugins is a way to control which components are available for retrieval.
    However, the components are not actually moved within the registry, but are simply filtered out
    when retrieving them through the `get` method. Disabled components are still accessible through
    the `components` attribute of the registry, or by setting the `enabled_only` argument to `False`
    in the `get` method.
    """

    def __init__(
        self,
        resolver=None,
        validator_type=PluginValidator,
        enable_by_default=True,
    ):
        self.resolver = resolver or ConflictResolver()
        self.validator_type = validator_type
        self.enable_by_default = enable_by_default
        self.plugins = TypeConstrainedDict(str, Plugin)
        self.enabled: List[str] = []
        self.components = TypeConstrainedDict(str, ComponentSet)

    def get(self, key: str, name: Optional[str], enabled_only=True) -> List[Component]:
        """
        Retrieve all the components under a specific key, optionally by name and enabled status.

        Arguments
        ---------
        key : str
            Field containing the component(s) to retrieve (i.e. as specified in the model).
        name : str, optional
            Name of one specific component to retrieve (i.e. as registered in the plugin).
        enabled_only : bool, default=True
            Whether to retrieve only components from enabled plugins.

        Returns
        -------
        ComponentSet
            All the components registered under this key, matching the name if provided, and
            enabled if requested.
        """
        comps = self.components.get(key)  # None if key not found
        if not comps:
            return []
        if name:
            comps = [comp for comp in comps if comp.name == name]
        if enabled_only:
            comps = [comp for comp in comps if comp.plugin in self.enabled]
        return comps

    def enable(self, name: str) -> None:
        """
        Enable a plugin to make all its components available via the `get` method.

        Arguments
        ---------
        name : str
            Name of the plugin to enable.

        Raises
        ------
        PluginNotFoundError
            If the plugin is not registered (i.e. cannot be enabled).
        """
        if not name in self.plugins:
            raise PluginNotFoundError(f"No plugin '{name}' in register.")
        if name not in self.enabled:
            self.enabled.append(name)

    def disable(self, name: str) -> None:
        """
        Disable a plugin to prevent its components from being retrieved via the `get` method.

        Arguments
        ---------
        name : str
            Name of the plugin to disable.
        """
        if name in self.enabled:
            self.enabled.remove(name)

    def register(self, plugin: Plugin) -> None:
        """
        Default registering behavior. Override this method to customize the registration process.

        Arguments
        ---------
        plugin : Plugin
            Plugin instance to register.

        Raises
        ------
        PluginValidationError
            If the plugin is invalid (carries the full ``ValidationResult`` diagnostics).
        PluginConflictError
            If conflicts occur and the conflict resolution strategy raises.
        """
        validator = self.validator_type(plugin)  # fresh validator for the plugin
        result = validator.validate()
        if result.is_valid:
            new = plugin
            if plugin.name in self.plugins:  # trigger conflict resolution
                new = self.resolver.resolve(plugin)
            if new:  # resolver may return None
                self.plugins[plugin.name] = plugin  # save the full plugin
                self.unpack(plugin)  # organize its components
                if self.enable_by_default:
                    self.enable(plugin.name)
        else:
            raise PluginValidationError(result)

    def unpack(self, plugin: Plugin) -> None:
        """
        Unpack and organize all the components provided by a plugin.

        Notes
        -----
        Each component provided by the plugin is stored in the registry under the key corresponding
        to its nature (i.e. the field's key under which it was added to the plugin). If a key
        already exists in the registry (e.g. other plugins have already registered components for
        this field), the new component is added among the already registered components. If a key
        does not exist yet in the registry (i.e. the plugin is the first to provide components for
        this field), a new key is created and the component is stored under it.

        For each key, if the field is not contained to `unique` in the model (i.e. unique component
        by plugin), a plugin can provide multiple components (under the form of a `ComponentSet`).
        """
        for key, comps in plugin.components.items():  # key: field name, comps: ComponentSet
            if key not in self.components:
                self.components[key] = ComponentSet()
            self.components[key].extend(comps)
