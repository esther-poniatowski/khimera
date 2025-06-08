"""
Entry point for the `khimera` package, invoked as a module.

Usage
-----
To launch the command-line interface, execute::

    python -m khimera


See Also
--------
khimera.cli: Module implementing the application's command-line interface.
"""
from .cli import app

app()
