"""
khimera.cli.app
===============

Provides a custom CLI class which inherits from a `Typer` application, with additional methods for
structured command registration.

Classes
-------
CliApp
"""
from typing import Optional, Self, Dict, Callable

import typer


class CliApp(typer.Typer):  # pylint: disable=unused-variable
    """
    Extends Typer with additional functionality for structured command registration.

    Arguments
    ---------
    app : typer.Typer, optional
        Existing Typer instance to wrap. If None, a new Typer instance is created.
    **kwargs
        Additional keyword arguments to pass to the Typer constructor.

    Attributes
    ----------
    groups_index : Dict[str, int]
        Registry of command groups, storing references to the index of the group in the
        the application.
        Keys: Group names. Values: Index of the group in the `Typer.registered_groups` list.
    commands_index : Dict[str, int]
        Registry of commands at the main application level.
        Keys: Group names. Values: Index of the command in the `Typer.registered_commands` list.

    Usage
    -----
    To define a main application:

    1. Create a new Python script (e.g., `main.py`).
    2. Initialize an instance of `CliApp`
    3. Add command groups and commands (see Examples).
    4. Register the main application as the entry point.

    Structure of the main application (`main.py`):

    .. code-block:: python

        #!/usr/bin/env python3

        from app import CliApp

        cli = CliApp()

        def my_command(arg: str):
            print("Test command with argument:", arg)

        cli.add_command(name="test-command", function=my_command)

        if __name__ == "__main__":
            cli()

    To run commands from the terminal:

    1. Display available commands:

    .. code-block:: bash

        $ python main.py --help

    2. Invoke commands from the terminal:

    .. code-block:: bash

        $ python main.py test-command --arg "Test argument"
        Test command with argument: Test argument


    To use this application as a command-line tool:

    1. Create a `pyproject.toml` file in the project root:

    .. code-block:: toml

        [build-system]
        requires = ["setuptools", "wheel"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "my-app"
        version = "0.1.0"
        dependencies = ["typer"]

        [project.scripts]
        my-app = "main:cli"

    2. Install the package locally in editable mode:

    .. code-block:: bash

        $ pip install -e .

    3. Use the CLI directly as a command-line tool:

    .. code-block:: bash

        $ my-app test-command --arg "Test argument"
        Test command with argument: Test argument

    Examples
    --------
    Add a command to the main application:

    >>> def my_command():
    ...     print("Test command")
    >>> cli.add_command(name="test-command", function=my_command)

    Add a command group:

    >>> cli.add_group("test-group")

    Add a command to the group:

    >>> def group_command():
    ...     print("Test group command")
    >>> group.add_command(name="group-command", function=group_command)

    Retrieve the group and check the command it contains:

    >>> group = cli.get_group("test-group")
    >>> print(group.has_command("group-command"))
    True

    Notes
    -----
    A default callback is registered to prevent errors when the CLI is invoked without any argument.
    Although the attribute `no_args_is_help` is set to True, it does not prevent parsing errors:
    `RuntimeError: Could not get a command for this Typer instance`.

    See Also
    --------
    typer.Typer.registered_groups : List[TyperInfo]
        Registered command groups, stored as TyperInfo objects. To access the Typer instance, use
        the `typer_instance` attribute.
    typer.Typer.registered_commands : List[TyperInfo]
        Registered commands at the main application level, stored as TyperInfo objects. To access
        the command function, use the `command` attribute.
    """

    def __init__(self, app: Optional[typer.Typer] = None, **kwargs):
        """Initialize the custom CLI wrapper."""
        # Create new Typer instance
        super().__init__(no_args_is_help=True, **kwargs)
        # If an existing Typer instance is provided, copy all its other attributes
        if app:
            self.__dict__.update(app.__dict__)
            self.info.no_args_is_help = True  # enforce `no_args_is_help` to True
        # Register default callback
        self.callback()(self.default_callback)
        # Add new attributes for group and command indexing
        self.groups_index: Dict[str, int] = {}
        self.commands_index: Dict[str, int] = {}

    def default_callback(self):
        """Default CLI entry point when no command is provided or execution fails."""

    def has_group(self, name: str) -> bool:
        """Check if a command group exists."""
        return name in self.groups_index

    def has_command(self, name: str, in_group: Optional[str] = None) -> bool:
        """Check if a command exists, either in the main app or in a specified group."""
        if in_group:
            group = self.get_group(in_group)
            if group:
                return group.has_command(name)
        else:
            return name in self.commands_index
        return False

    def get_group(self, name: str) -> Optional[Self]:
        """
        Retrieve a command group by name.

        Arguments
        ---------
        name : str
            Name of the command group to retrieve.

        Returns
        -------
        CliApp
            Instance corresponding to the command group. None if not found.
        """
        index = self.groups_index.get(name)
        if index is not None:
            typer_instance = self.registered_groups[index].typer_instance
            return typer_instance if isinstance(typer_instance, self.__class__) else None
        return None

    def add_group(
        self, name: str, sub_app: Optional[typer.Typer] = None, help_msg: Optional[str] = None
    ) -> Self:
        """
        Registers a command group, either an existing Typer instance or a new empty one.

        Arguments
        ---------
        name : str
            Name of the command group.
        sub_app : typer.Typer, optional
            Typer instance to be used as the command group. If None, a new Typer instance is
            created.
        help_msg : str, optional
            Help message for the command group.

        Returns
        -------
        CliApp
            Instance of the command group, to allow fluent construction.

        Raises
        ------
        ValueError
            If a command group already exists under the given name.

        See Also
        --------
        typer.Typer.add_typer
            Add a sub-Typer instance as a command group. The new group is appended to the end of the
            `registered_groups` list, so that newly added command group becomes the last item in the
            list of registered groups.

        Implementation
        --------------
        The new application is converted to an instance of the current class (`self.__class__`) if
        it is not already, to inherit the custom methods of the class. The current class is
        dynamically determined, so that subclasses of `CliApp` can be used uniformly.
        """
        if self.has_group(name):
            raise ValueError(f"Command group '{name}' already exists.")
        new_app = sub_app if isinstance(sub_app, self.__class__) else self.__class__(app=sub_app)
        self.add_typer(new_app, name=name, help=help_msg)  # call Typer's add_typer method
        self.groups_index[name] = len(self.registered_groups) - 1  # group index in main app
        return new_app

    def add_command(self, name: str, function: Callable, in_group: Optional[str] = None) -> None:
        """
        Dynamically register a command inside a specific group.

        Arguments
        ---------
        function : callable
            Function to be executed when the command is triggered.
        name : str
            Name of the command.
        in_group : str, optional
            Name of the group the command belongs to. If not specified, the command is added to the
            main application.

        Raises
        ------
        ValueError
            If the command group does not exist.

        See Also
        --------
        typer.Typer.command
            Decorator for registering a command in a Typer application.
        """
        if in_group:  # retrieve group and delegate command registration
            app = self.get_group(in_group)  # None if group not found
            if not app:
                raise ValueError(f"Command group '{in_group}' not found.")
            app.add_command(name, function, in_group=None)
        else:  # fallback to main app (self)
            if self.has_command(name):
                raise ValueError(f"Command '{name}' already exists.")
            self.command(name=name)(function)  # call Typer's command decorator
            self.commands_index[name] = len(self.registered_commands) - 1  # index in main app
