"""
test_khimera.test_management.test_register
==========================================

Test suite for the `khimera.management.register` module.

Notes
-----
Mocking Strategy:

- PluginValidator: Mocked to avoid dependencies on validation logic and focus on registry behavior.
- Component Instances: Mocked to isolate registry operations from specific component
  implementations.
- Plugin Instances: Instantiated using the real class to preserve expected attribute behavior and
  type constraints. Only its `components` attribute is mocked to control test conditions without
  affecting registry logic.

Mocking strategy:

- Component: Fully mocked to isolate registry operations from specific component implementations.
  Mocked attributes: `name` and `plugin` (attached to the plugin name).
- ComponentSet: Not mocked, as it is a simple container class.
- Plugin: Mocked to isolate registry operations from specific plugin implementations. Mocked
  attributes: `name` and `components` (used in the test) and `model` (required by the validator).
- PluginValidator: Mocked to avoid dependencies on validation logic and focus on registry behavior.
  Only the `validate` method is patched to return the desired validation result, since the validator
  is not passed by dependency injection and its method is called internally in the registry.

Warning
-------
The `Mock` class has a `name` attribute that conflicts with the `name` attributes of the `Component`
and `Plugin` classes if it is passed as keyword argument to the `Mock` constructor. Therefore, the
`name` attribute of the mocked instances is set after creating the mock objects.

See Also
--------
khimera.management.register
    Module under test.
pytest_mock.MockFixture
    Mocking fixture for Pytest.
"""
from typing import List, Dict, Optional

import pytest
import pytest_mock

from khimera.management.register import ConflictResolver, PluginRegistry
from khimera.plugins.create import Plugin
from khimera.plugins.declare import PluginModel
from khimera.core.components import Component, ComponentSet
from khimera.management.validate import PluginValidator


# --- Fixtures and Utilities -----------------------------------------------------------------------


def mock_component(mocker: pytest_mock.MockFixture, name: str, plugin: Optional[str] = None):
    """
    Create a mock `Component` instance with a specified name and an optional plugin attribute.

    Arguments
    ---------
    name : str
        Name of the component.
    plugin : str, optional
        Name of the plugin that provides this component.

    Returns
    -------
    Mocked Component
    """
    component = mocker.Mock(spec=Component)
    component.configure_mock(name=name, plugin=plugin)  # outside of the constructor
    return component


def mock_plugin(
    mocker: pytest_mock.MockFixture,
    name: str = "mock_plugin",
    components: Optional[Dict[str, List[str]]] = None,
):
    """
    Create a mock `Plugin` instance with a specified name and components.

    Arguments
    ---------
    name : str, default="mock_plugin"
        Name of the plugin.
    components : dict, optional
        Names of the components provided by the plugin, mapped to field names. Those components will
        be mocked and stored in a `ComponentSet` instance. If None, a single component is created
        under the key "key1".

    Returns
    -------
    Plugin
        Sample plugin instance with the specified name and components and a mocked model (required
        by the validator).
    """
    if components:
        plugin_comps = {
            key: ComponentSet([mock_component(mocker, name) for name in names])
            for key, names in components.items()
        }
    else:
        plugin_comps = {"key1": ComponentSet([mocker.Mock(spec=Component, name="compA")])}
    plugin = mocker.Mock(spec=Plugin)
    plugin.configure_mock(name=name, model=mocker.Mock(spec=PluginModel), components=plugin_comps)
    return plugin


def patch_validator(mocker: pytest_mock.MockFixture, output: bool = True):
    """
    Patch the `validate` method of the `PluginValidator` class to return a specified output.

    Arguments
    ---------
    output : bool, default=True
        Desired output of the `validate` method.

    Returns
    -------
    None
    """
    mocker.patch.object(PluginValidator, "validate", return_value=output)


# --- Tests for ConflictResolver -------------------------------------------------------------------


def test_conflict_resolver(mocker: pytest_mock.MockFixture):
    """
    Test the conflict resolution strategy in 'RAISE_ERROR' mode.

    Expected Behavior: Raises a ValueError.
    """
    resolver = ConflictResolver(mode="RAISE_ERROR")
    plugin = mock_plugin(mocker)
    with pytest.raises(ValueError):
        resolver.resolve(plugin)


def test_conflict_resolver_override(mocker: pytest_mock.MockFixture):
    """
    Test the conflict resolution strategy in 'OVERRIDE' mode.

    Expected Behavior: Returns the plugin instance. Raise a UserWarning.
    """
    resolver = ConflictResolver(mode="OVERRIDE")
    plugin = mock_plugin(mocker)
    with pytest.warns(UserWarning, match="Overridden"):
        assert resolver.resolve(plugin) is plugin


def test_conflict_resolver_ignore(mocker: pytest_mock.MockFixture):
    """
    Test the conflict resolution strategy in 'IGNORE' mode.

    Expected Behavior: Returns None. Raise a UserWarning.
    """
    sample_plugin = mock_plugin(mocker)
    resolver = ConflictResolver(mode="IGNORE")
    with pytest.warns(UserWarning, match="Ignored"):
        assert resolver.resolve(sample_plugin) is None


# --- Tests for PluginRegistry ---------------------------------------------------------------------


def test_plugin_registry_init():
    """Test initializing a PluginRegistry instance."""
    registry = PluginRegistry()
    assert len(registry.plugins) == 0
    assert len(registry.components) == 0
    assert len(registry.enabled) == 0
    assert hasattr(registry, "validator_type")
    assert hasattr(registry, "enable_by_default")


@pytest.mark.parametrize(
    "query_field, query_name, enabled_only, expected_components",
    [
        # Case 1: Retrieve no specific component under a valid key -> Expect all components
        ("test_key", None, False, ["comp1", "comp2", "comp3"]),
        # Case 2: Retrieve only enabled components under a -> Expect only enabled components
        ("test_key", None, True, ["comp1", "comp2"]),
        # Case 3: Retrieve a named component under a valid key -> Expect a single component
        ("test_key", "comp1", False, ["comp1"]),
        # Case 4: Retrieve a named component that is not enabled -> Expect an empty list
        ("test_key", "comp3", True, []),
        # Case 5: Retrieve a nonexistent component under a valid key -> Expect an empty list
        ("test_key", "nonexistent", False, []),
        # Case 6: Retrieve from a nonexistent key -> Expect an empty list
        ("nonexistent_key", None, False, []),
    ],
)
def test_plugin_registry_get(
    mocker: pytest_mock.MockFixture,
    query_field: str,
    query_name: str,
    enabled_only: bool,
    expected_components: List[str],
):
    """
    Parametric test for the `get` method and its different retrieval scenarios.

    Test Cases:

    - Retrieve no specific component under a valid key -> Expect all components.
    - Retrieve only enabled components under a -> Expect only enabled components.
    - Retrieve a named component under a valid key -> Expect a single component.
    - Retrieve a named component that is not enabled -> Expect an empty list.
    - Retrieve a nonexistent component under a valid key -> Expect an empty list.
    - Retrieve from a nonexistent key -> Expect an empty list.

    Arguments
    ---------
    query_field : str
        Field to retrieve components from.
    query_name : str
        Optional name of the component to retrieve.
    enabled_only : bool
        Whether to retrieve only enabled components.
    expected_components : List[str]
        Expected names of the components to retrieve.
    """
    # Set up a PluginRegistry instance with mock components
    registry = PluginRegistry()
    if query_field == "test_key":
        registry.components[query_field] = ComponentSet()
        for comp_name, plugin_name in [
            ("comp1", "pluginA"),
            ("comp2", "pluginA"),
            ("comp3", "pluginB"),
        ]:
            component = mock_component(mocker, comp_name, plugin_name)
            registry.components[query_field].append(component)
    if enabled_only:
        registry.enabled = ["pluginA"]  # enable only components from pluginA
    # Retrieve the components and compare with the expected ones
    components = registry.get(query_field, query_name, enabled_only)
    assert len(components) == len(expected_components)
    for comp in components:
        assert comp.name in expected_components


@pytest.mark.parametrize(
    "plugin_name, initial_enabled, registered, expected",
    [
        # Case 1: Enable a plugin that is not registered -> Expect AttributeError
        ("unknown_plugin", [], [], None),
        # Case 2: Enable a plugin that is registered but not enabled -> Expect plugin to be added to `enabled`
        ("known_plugin", [], ["known_plugin"], ["known_plugin"]),
        # Case 3: Enable a plugin that is already enabled -> Expect no change
        ("known_plugin", ["known_plugin"], ["known_plugin"], ["known_plugin"]),
    ],
)
def test_plugin_registry_enable(
    mocker: pytest_mock.MockFixture,
    plugin_name: str,
    initial_enabled: list,
    registered: list,
    expected: list,
):
    """
    Test for the `enable` method in different scenarios.

    Test Cases:
    - Enable a plugin that is not registered -> Expect AttributeError.
    - Enable a plugin that is registered but not enabled -> Expect plugin to be added to `enabled`.
    - Enable a plugin that is already enabled -> Expect no change.

    Arguments
    ---------
    plugin_name : str
        Name of the plugin to enable.
    initial_enabled : list
        Initial list of enabled plugins.
    registered : list
        Plugins registered in the registry before calling `enable`.
    expected : list or None
        Expected list of enabled plugins after enabling. If None, expect AttributeError.
    """
    registry = PluginRegistry()
    registry.enabled = initial_enabled
    # Register only plugins that should be present
    for name in registered:
        plugin = mock_plugin(mocker, name=name)
        registry.plugins[name] = plugin
    # Enable the plugin and check the result
    if expected is None:  # Expecting an AttributeError
        with pytest.raises(AttributeError):
            registry.enable(plugin_name)
    else:
        registry.enable(plugin_name)
        assert registry.enabled == expected


@pytest.mark.parametrize(
    "plugin_name, initial_enabled, registered, expected",
    [
        # Case 1: Disable a plugin that is not registered -> Expect no change
        ("unknown_plugin", ["known_plugin"], [], ["known_plugin"]),
        # Case 2: Disable a registered and enabled plugin -> Expect removal from `enabled`
        ("known_plugin", ["known_plugin"], ["known_plugin"], []),
        # Case 3: Disable a registered but already disabled plugin -> Expect no change
        ("known_plugin", [], ["known_plugin"], []),
    ],
)
def test_plugin_registry_disable(
    mocker: pytest_mock.MockFixture,
    plugin_name: str,
    initial_enabled: list,
    registered: list,
    expected: list,
):
    """
    Test for the `disable` method in different scenarios.

    Test Cases:
    - Disable a plugin that is not registered -> Expect no change.
    - Disable a registered and enabled plugin -> Expect removal from `enabled`.
    - Disable a registered but already disabled plugin -> Expect no change.

    Arguments
    ---------
    plugin_name : str
        Name of the plugin to disable.
    initial_enabled : list
        Initial list of enabled plugins.
    registered : list
        Plugins registered in the registry before calling `disable`.
    expected : list
        Expected list of enabled plugins after disabling.
    """
    registry = PluginRegistry()
    registry.enabled = initial_enabled
    # Register only plugins that should be present
    for name in registered:
        plugin = mock_plugin(mocker, name=name)
        registry.plugins[name] = plugin
    # Disable the plugin and check the result
    registry.disable(plugin_name)
    assert registry.enabled == expected


@pytest.mark.parametrize(
    "initial_components, plugin_components, expected",
    [
        # Case 1: Plugin provides new components under a new key
        ({}, {"key1": ["compA"]}, {"key1": ["compA"]}),
        # Case 2: Plugin adds components to an existing key
        ({"key1": ["compA"]}, {"key1": ["compB"]}, {"key1": ["compA", "compB"]}),
        # Case 3: Plugin provides multiple keys with components
        ({}, {"key1": ["compA"], "key2": ["compB"]}, {"key1": ["compA"], "key2": ["compB"]}),
        # Case 4: Plugin adds components to multiple existing keys
        (
            {"key1": ["compA"], "key2": ["compB"]},
            {"key1": ["compC"], "key2": ["compD"]},
            {"key1": ["compA", "compC"], "key2": ["compB", "compD"]},
        ),
    ],
)
def test_plugin_registry_unpack(
    mocker: pytest_mock.MockFixture,
    initial_components: dict,
    plugin_components: dict,
    expected: dict,
):
    """
    Test for the `unpack` method in different scenarios.

    Test Cases:
    - Plugin provides new components under a new key -> Registry should create a new field and store components.
    - Plugin adds components to an existing key -> Registry should extend the existing components.
    - Plugin provides multiple keys -> Registry should create and store components accordingly.
    - Plugin adds components to multiple existing keys -> Registry should extend each field.

    Arguments
    ---------
    initial_components : dict
        Initial state of the registry's component storage (keys mapped to component names).
    plugin_components : dict
        Components provided by the plugin (keys mapped to component names).
    expected : dict
        Expected state of the registry's component storage after unpacking (keys mapped to component names).
    """
    registry = PluginRegistry()
    # Mock ComponentSet objects
    registry.components = {
        key: ComponentSet([mock_component(mocker, name) for name in names])
        for key, names in initial_components.items()
    }
    # Mock plugin and set its components
    plugin = mocker.Mock(spec=Plugin)
    plugin.components = {
        key: ComponentSet([mock_component(mocker, name) for name in names])
        for key, names in plugin_components.items()
    }
    # Unpack plugin components and check registry state
    registry.unpack(plugin)
    assert registry.components.keys() == expected.keys()
    for key in expected:
        actual_names = [comp.name for comp in registry.components[key]]
        assert sorted(actual_names) == sorted(expected[key])


# --- Tests for the final `register` method --------------------------------------------------------


def test_plugin_registry_register(mocker: pytest_mock.MockFixture):
    """
    Test registering a plugin under normal conditions, i.e. no conflicts or validation issues.

    Test Cases:
    - A valid plugin is registered successfully.
    - The plugin is stored in `registry.plugins`.
    - The `unpack` method is called to store its components.
    - If `enable_by_default` is True, the plugin is enabled.

    Notes
    -----
    Mocking strategy:

    - Patch the `validate` method of the `PluginValidator` to return `True` (bypassing validation
      logic).
    - Spy the `unpack` and `enable` methods of the registry to ensure they are called.
    """
    registry = PluginRegistry(enable_by_default=True)
    # Patch the validator to always return True
    patch_validator(mocker, output=True)
    # Spy on `unpack` and `enable`
    mock_unpack = mocker.spy(registry, "unpack")
    mock_enable = mocker.spy(registry, "enable")
    # Ensure plugin has components
    plugin = mock_plugin(mocker)
    # Register the plugin and check the results
    registry.register(plugin)
    assert plugin.name in registry.plugins
    mock_unpack.assert_called_once_with(plugin)
    if registry.enable_by_default:
        mock_enable.assert_called_once_with(plugin.name)


def test_plugin_registry_register_invalid_plugin(mocker):
    """
    Test attempting to register an invalid plugin.

    Test Case:

    - If a plugin is invalid (fails validation), `register` should raise `ValueError`.
    - The plugin should not be stored in `registry.plugins`.
    - The `unpack` method should never be called.
    """
    registry = PluginRegistry()
    patch_validator(mocker, output=False)  # force invalid plugin
    plugin = mock_plugin(mocker)
    with pytest.raises(ValueError, match=f"Invalid plugin: {plugin.name}"):
        registry.register(plugin)
    assert plugin.name not in registry.plugins


def test_plugin_registry_register_conflict_override(mocker):
    """
    Test registering a plugin with conflict resolution set to 'OVERRIDE'.

    Test Case:

    - If a plugin with the same name is already registered, the new one should replace it.
    - A warning should be raised during the override.
    - The `unpack` and `enable` methods should be called for the new plugin.
    """
    registry = PluginRegistry(resolver=ConflictResolver("OVERRIDE"))
    patch_validator(mocker, output=True)  # force valid plugin
    # Create two plugin instances with the same name
    name = "test_plugin"
    plugin1 = mock_plugin(mocker, name=name)
    plugin2 = mock_plugin(mocker, name=name)
    # Register the first plugin
    registry.register(plugin1)
    assert registry.plugins[name] == plugin1
    # Spy on `unpack` to verify it is called
    mock_unpack = mocker.spy(registry, "unpack")
    # Register the second plugin, which should override the first
    with pytest.warns(UserWarning):
        registry.register(plugin2)
    assert registry.plugins[name] == plugin2  # replaced plugin
    mock_unpack.assert_called_with(plugin2)  # unpack called for the new plugin


def test_plugin_registry_register_conflict_ignore(mocker):
    """
    Test registering a plugin with conflict resolution set to 'IGNORE'.

    Test Case:

    - If a plugin with the same name is already registered, the new one should be discarded.
    - A warning should be raised during the ignore action.
    - The `unpack` method should not be called for the new plugin.
    """
    registry = PluginRegistry(resolver=ConflictResolver("IGNORE"))
    patch_validator(mocker, output=True)  # force valid plugin
    # Create two plugin instances with the same name
    name = "test_plugin"
    plugin1 = mock_plugin(mocker, name=name)
    plugin2 = mock_plugin(mocker, name=name)
    # Register the first plugin
    registry.register(plugin1)
    assert registry.plugins[name] == plugin1
    # Spy on `unpack` to verify it is NOT called for the ignored plugin
    mock_unpack = mocker.spy(registry, "unpack")
    # Register the second plugin, which should be ignored
    with pytest.warns(UserWarning):
        registry.register(plugin2)
    assert registry.plugins[name] == plugin1  # remain unchanged
    mock_unpack.assert_not_called()  # unpack NOT called for ignored plugin
