"""
test_khimera.test_components.test_commands
==========================================

Tests for the component and specification classes for commands.

See Also
--------
khimera.components.commands
"""
# --- Silenced Errors ---
# pylint: disable=unused-variable
#   Test functions are used, but pylint does not detect it.
# pylint: disable=unused-import
#   Pytest is imported for testing while not explicitly used in this module.

import pytest

from khimera.components.commands import Command, CommandSpec


# --- Tests for Command (Component) ----------------------------------------------------------------


def test_command_initialization():
    """Test initialization of Command."""
    name = "test_command"
    description = "Test command"
    group = "test_group"

    def sample_command():
        pass

    command = Command(name=name, func=sample_command, group=group, description=description)
    assert command.name == name
    assert command.func is sample_command
    assert command.group == group
    assert command.description == description


def test_command_initialization_without_group():
    """Test initialization of Command without group."""
    name = "test_command"

    def sample_command():
        pass

    command = Command(name=name, func=sample_command)
    assert command.name == name
    assert command.func is sample_command
    assert command.group is None


# --- Tests for CommandSpec (FieldSpec) ------------------------------------------------------------


def test_command_spec_initialization():
    """Test initialization of `CommandSpec`."""
    name = "test_spec"
    groups = {"group1", "group2"}
    admits_new_groups = True
    admits_top_level = False
    required = True
    unique = False
    description = "Test command specification"
    command_spec = CommandSpec(
        name=name,
        groups=groups,
        admits_new_groups=admits_new_groups,
        admits_top_level=admits_top_level,
        required=required,
        unique=unique,
        description=description,
    )
    assert command_spec.name == name
    assert command_spec.groups == groups
    assert command_spec.admits_new_groups == admits_new_groups
    assert command_spec.admits_top_level == admits_top_level
    assert command_spec.required == required
    assert command_spec.unique == unique
    assert command_spec.description == description


def test_command_spec_initialization_defaults():
    """Test initialization of `CommandSpec` with default values."""
    command_spec = CommandSpec(name="test_spec")
    assert command_spec.groups == set()
    assert command_spec.admits_new_groups is True
    assert command_spec.admits_top_level is True
    assert command_spec.required is False
    assert command_spec.unique is False


# --- Tests for CommandSpec validation -------------------------------------------------------------


def test_command_spec_validate_valid_group():
    """Test `CommandSpec` validation with a valid group."""
    command_spec = CommandSpec(name="test_spec", groups={"group1", "group2"})
    command = Command(name="test_command", func=lambda: None, group="group1")
    assert command_spec.validate(command) is True


def test_command_spec_validate_new_group():
    """Test `CommandSpec` validation with a new group."""
    command_spec = CommandSpec(
        name="test_spec", groups={"group1", "group2"}, admits_new_groups=True
    )
    command = Command(name="test_command", func=lambda: None, group="new_group")
    assert command_spec.validate(command) is True


def test_command_spec_validate_new_group_not_allowed():
    """Test `CommandSpec` validation with a new group not allowed."""
    command_spec = CommandSpec(
        name="test_spec", groups={"group1", "group2"}, admits_new_groups=False
    )
    command = Command(name="test_command", func=lambda: None, group="new_group")
    assert command_spec.validate(command) is False


def test_command_spec_validate_top_level():
    """Test `CommandSpec` validation with a top-level command."""
    command_spec = CommandSpec(name="test_spec", admits_top_level=True)
    command = Command(name="test_command", func=lambda: None)
    assert command_spec.validate(command) is True


def test_command_spec_validate_top_level_not_allowed():
    """Test `CommandSpec` validation with a top-level command not allowed."""
    command_spec = CommandSpec(name="test_spec", admits_top_level=False)
    command = Command(name="test_command", func=lambda: None)
    assert command_spec.validate(command) is False


def test_command_spec_validate_empty_groups():
    """Test `CommandSpec` validation with empty groups."""
    command_spec = CommandSpec(name="test_spec")
    command = Command(name="test_command", func=lambda: None, group="new_group")
    assert command_spec.validate(command) is True
