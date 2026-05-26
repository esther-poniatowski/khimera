<a id="cli"></a>

# CLI

Command-line interface for the `khimera` package.

<a id="module-khimera.cli.app"></a>

<a id="app"></a>

## App

<a id="khimera-cli-app"></a>

### khimera.cli.app

Provides a custom CLI class which inherits from a Typer application, with additional methods for
structured command registration.

<a id="khimera.cli.app.CliApp"></a>

### *class* khimera.cli.app.CliApp(app=None, \*\*kwargs)

Bases: `Typer`

Extends Typer with additional functionality for structured command registration.

* **Parameters:**
  * **app** (*typer.Typer* *,* *optional*) – Existing Typer instance to wrap. If None, a new Typer instance is created.
  * **\*\*kwargs** – Additional keyword arguments to pass to the Typer constructor.
  * **Usage**
  * **-----**
  * **application** (*To define a main*)
  * **(****e.g.** (*1. Create a new Python script*)
  * **main.py****)****.**
  * **CliApp** (*2. Initialize an instance of*)
  * **Examples****)****.** (*3. Add command groups and commands* *(**see*)
  * **point.** (*4. Register the main application as the entry*)
  * **(****main.py****)** (*Structure* *of* *the main application*)
  * **code-block:** ( *..*) – 

    python: #!/usr/bin/env python3

    from app import CliApp

    cli = CliApp()

    def my_command(arg: str):
    : print(“Test command with argument:”, arg)

    cli.add_command(name=”test-command”, function=my_command)

    if \_\_name_\_ == “_\_main_\_”:
    : cli()
  * **terminal** (*2. Invoke commands from the*)
  * **commands** (*1. Display available*)
  * **code-block:** – bash: $ python main.py –help
  * **terminal**
  * **code-block:** – bash: $ python main.py test-command –arg “Test argument”
    Test command with argument: Test argument

To use this application as a command-line tool:

1. Create a pyproject.toml file in the project root:

```toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-app"
version = "0.1.0"
dependencies = ["typer"]

[project.scripts]
my-app = "main:cli"
```

1. Install the package locally in editable mode:

```bash
$ pip install -e .
```

1. Use the CLI directly as a command-line tool:

```bash
$ my-app test-command --arg "Test argument"
Test command with argument: Test argument
```

### Examples

Add a command to the main application:

```pycon
>>> def my_command():
...     print("Test command")
>>> cli.add_command(name="test-command", function=my_command)
```

Add a command group:

```pycon
>>> cli.add_group("test-group")
```

Add a command to the group:

```pycon
>>> def group_command():
...     print("Test group command")
>>> group.add_command(name="group-command", function=group_command)
```

Retrieve the group and check the command it contains:

```pycon
>>> group = cli.get_group("test-group")
>>> print(group.has_command("group-command"))
True
```

### Notes

A default callback is registered to prevent errors when the CLI is invoked without any argument.
Although the attribute no_args_is_help is set to True, it does not prevent parsing errors:
RuntimeError: Could not get a command for this Typer instance.

> **See also**
>
> `typer.Typer.registered_groups`
> : List[TyperInfo] Registered command groups, stored as TyperInfo objects. To access the Typer instance, use the typer_instance attribute.
>
> `typer.Typer.registered_commands`
> : List[TyperInfo] Registered commands at the main application level, stored as TyperInfo objects. To access the command function, use the command attribute.

<a id="khimera.cli.app.CliApp.__init__"></a>

#### \_\_init_\_(app=None, \*\*kwargs)

Initialize the custom CLI wrapper.

<a id="khimera.cli.app.CliApp.default_callback"></a>

#### default_callback()

Default CLI entry point when no command is provided or execution fails.

<a id="khimera.cli.app.CliApp.has_group"></a>

#### has_group(name)

Check if a command group exists.

<a id="khimera.cli.app.CliApp.has_command"></a>

#### has_command(name, in_group=None)

Check if a command exists, either in the main app or in a specified group.

<a id="khimera.cli.app.CliApp.get_group"></a>

#### get_group(name)

Retrieve a command group by name.

* **Parameters:**
  **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the command group to retrieve.
* **Returns:**
  Instance corresponding to the command group. None if not found.
* **Return type:**
  [CliApp](#khimera.cli.app.CliApp)

<a id="khimera.cli.app.CliApp.add_group"></a>

#### add_group(name, sub_app=None, help_msg=None)

Registers a command group, either an existing Typer instance or a new empty one.

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the command group.
  * **sub_app** (*typer.Typer* *,* *optional*) – Typer instance to be used as the command group. If None, a new Typer instance is
    created.
  * **help_msg** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Help message for the command group.
* **Returns:**
  Instance of the command group, to allow fluent construction.
* **Return type:**
  [CliApp](#khimera.cli.app.CliApp)
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If a command group already exists under the given name.

> **See also**
>
> `typer.Typer.add_typer`
> : Add a sub-Typer instance as a command group. The new group is appended to the end of the registered_groups list, so that newly added command group becomes the last item in the list of registered groups.
>
> `Implementation`, `--------------`, `The`, `it`, `to`, `dynamically`, `so`

<a id="khimera.cli.app.CliApp.add_command"></a>

#### add_command(name, function, in_group=None)

Dynamically register a command inside a specific group.

* **Parameters:**
  * **function** (*callable*) – Function to be executed when the command is triggered.
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str)) – Name of the command.
  * **in_group** ([*str*](https://docs.python.org/3/library/stdtypes.html#str) *,* *optional*) – Name of the group the command belongs to. If not specified, the command is added to the
    main application.
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the command group does not exist.

> **See also**
>
> `typer.Typer.command`
> : Decorator for registering a command in a Typer application.
