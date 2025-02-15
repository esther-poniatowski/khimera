#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_climera.test_core.test_cli_app
====================================

Tests for the `CliApp` class, which extends `Typer` with additional functionality for structured
command registration.

See Also
--------
khimera.cli.cli_app.CliApp
"""
import pytest
import typer
from typer.testing import CliRunner

from khimera.cli.cli_app import CliApp

# --- Fixtures -------------------------------------------------------------------------------------

@pytest.fixture
def sample_command():
    """Factory for a sample command function."""
    def _factory():
        typer.echo("Success")
    return _factory

def test_sample_command(sample_command):
    """Ensure the sample command prints output correctly."""
    sample_command()

# --- Tests for CLI Initialization and Attributes --------------------------------------------------

def test_cli_app_creation_without_existing_instance():
    """Ensure the CLI application can be created without an existing Typer instance."""
    cli = CliApp()
    assert cli is not None, "CLI application was not created"
    assert isinstance(cli, typer.Typer), "CliApp should be an instance of Typer"

def test_cli_app_creation_with_existing_instance():
    """Ensure the CLI application can be created with an existing Typer instance and inherit attributes."""
    app = typer.Typer(help="Existing app")
    app.custom_attribute = "custom_value"
    cli = CliApp(app)
    assert cli.help == "Existing app", "CliApp should inherit 'help' attribute from existing Typer instance"
    assert hasattr(cli, "custom_attribute"), "CliApp should inherit custom attributes from existing Typer instance"
    assert cli.custom_attribute == "custom_value", "CliApp should copy the custom attribute correctly"

def test_custom_indices_initialized():
    """Ensure `groups_index` and `commands_index` are correctly initialized."""
    cli = CliApp()
    assert isinstance(cli.groups_index, dict), "`groups_index` should be initialized as a dictionary"
    assert isinstance(cli.commands_index, dict), "`commands_index` should be initialized as a dictionary"
    assert len(cli.groups_index) == 0, "`groups_index` should start empty"
    assert len(cli.commands_index) == 0, "`commands_index` should start empty"

@pytest.mark.parametrize("app", [None, typer.Typer(no_args_is_help=False)])
def test_no_args_is_help_enforced(app):
    """Ensure the attribute `no_args_is_help` is always set to True, even if the existing Typer instance has it False."""
    cli = CliApp(app) if app else CliApp()
    assert cli.info.no_args_is_help is True, "CliApp should enforce `no_args_is_help=True`"

# --- Tests for Command Group Management -----------------------------------------------------------

def test_add_group_new():
    """Ensure command groups can be created and retrieved with no sub-group instance."""
    cli = CliApp()
    group = cli.add_group("test-group")
    assert cli.has_group("test-group"), "Command group 'test-group' was not registered"
    assert cli.get_group("test-group") is group, "Retrieved group does not match the registered instance"

def test_add_group_existing():
    """Ensure command groups can be created and retrieved from an existing sub-group instance."""
    cli = CliApp()
    sub_app = CliApp()
    cli.add_group("test-group", sub_app)
    assert cli.has_group("test-group"), "Command group 'test-group' was not registered"
    assert cli.get_group("test-group") is sub_app, "Retrieved group does not match the registered instance"

def test_duplicate_group():
    """Ensure that adding a duplicate group is prevented."""
    cli = CliApp()
    cli.add_group("test-group")
    with pytest.raises(ValueError, match="Command group 'test-group' already exists."):
        cli.add_group("test-group")

def test_get_non_existent_group():
    """Ensure retrieving a non-existent group returns None."""
    cli = CliApp()
    assert cli.get_group("unknown") is None, "Non-existent group should return None"

def test_nested_groups():
    """Ensure nested command groups are correctly registered and accessible."""
    cli = CliApp()
    group = cli.add_group("test-group")
    sub_group = group.add_group("test-sub-group")
    assert group.has_group("test-sub-group"), "Nested group 'test-sub-group' was not registered under 'test-group'"
    assert group.get_group("test-sub-group") is sub_group, "Nested group retrieval failed"

# --- Tests for Command Registration ---------------------------------------------------------------

def test_register_command_main(sample_command):
    """Ensure commands can be registered dynamically in the main CLI."""
    cli = CliApp()
    cli.add_command(sample_command, "test-cmd")
    assert cli.has_command("test-cmd"), "Command 'test-cmd' was not registered"

def test_register_command_in_group(sample_command):
    """Ensure commands can be registered inside a command group."""
    cli = CliApp()
    group = cli.add_group("test-group")
    group.add_command(sample_command, "test-cmd")
    assert group.has_command("test-cmd"), "Command 'test-cmd' was not registered inside 'test-group'"

def test_register_command_non_existent_group(sample_command):
    """Ensure that a command cannot be registered in a non-existent group."""
    cli = CliApp()
    with pytest.raises(ValueError, match="Command group 'unknown' not found."):
        cli.add_command(sample_command, "test-cmd", in_group="unknown")

def test_duplicate_command_registration(sample_command):
    """Ensure that registering a duplicate command is prevented."""
    cli = CliApp()
    cli.add_command(sample_command, "test-cmd")
    with pytest.raises(ValueError, match="Command 'test-cmd' already exists."):
        cli.add_command(sample_command, "test-cmd")

# --- Tests for CLI Execution ----------------------------------------------------------------------

runner = CliRunner() # Typer testing runner

def test_cli_invocation():
    """Test that the CLI can be invoked with no argument."""
    cli = CliApp()
    result = runner.invoke(cli)
    assert result.exit_code == 0

def test_cli_help():
    """
    Test that the CLI displays help information (should be automatically provided by `Typer`).
    """
    cli = CliApp()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0

def test_unknown_command():
    """Ensure unknown commands return an error message."""
    cli = CliApp()
    result = runner.invoke(cli, ["unknown-command"])
    assert result.exit_code != 0

def test_command_execution(sample_command):
    """Ensure a command registered in the main CLI executes properly."""
    cli = CliApp()
    cli.add_command(sample_command, "test-cmd")
    result = runner.invoke(cli, ["test-cmd"])
    assert result.exit_code == 0, "Command execution failed"
    assert "Success" in result.output, "Expected output not found"

def test_group_command_execution(sample_command):
    """Ensure a command registered inside a group executes properly."""
    cli = CliApp()
    group = cli.add_group("test-group")
    group.add_command(sample_command, "test-cmd")
    result = runner.invoke(cli, ["test-group", "test-cmd"])
    assert result.exit_code == 0, "Command execution failed"
    assert "Success" in result.output, "Expected output not found"

def test_cli_groups_documented():
    """Ensure high-level command groups are documented in the help output."""
    cli = CliApp()
    group = cli.add_group("test-group", help="Test group")
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0, "Help command failed"
    assert "test-group" in result.output, "Command group 'test-group' missing from help output"
