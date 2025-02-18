#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.contributions.commands
==============================

Classes for defining new commands in plugin models and instances.

Classes
-------
Command
    Represents a command in the host application's CLI.
CommandSpec
    Declare the constraints that the commands of the plugins must satisfy.

See Also
--------
khimera.plugins.core.Contrib
    Abstract base class representing a contribution to a plugin instance.
khimera.plugins.core.CategorySpec
    Abstract base class for defining constraints and validations for contributions in a plugin model.
"""
from typing import Callable, Optional, Set

from khimera.contributions.core import Contrib, CategorySpec


class Command(Contrib):
    """
    Represents a command in the host application's CLI, optionally nested in a predefined
    sub-command group.

    Attributes
    ----------
    callable : Callable
        Function or method to be executed when the command is invoked.
    group : str, optional
        Name of the sub-command group where the command will be nested.
        If not provided, the command will be a top-level command, if allowed by the host
        application.
        If the group names does not match any predefined group in the host application, a new group
        will be created, if allowed by the host application.
    """
    def __init__(self, name: str, callable: Callable, group: Optional[str] = None, description: Optional[str] = None):
        super().__init__(name=name, description=description)
        self.callable = callable
        self.group = group


class CommandSpec(CategorySpec[Command]):
    """
    Declare the constraints that the commands of the plugins must satisfy to be accepted by the host
    application's CLI.

    Attributes
    ----------
    groups : Set[str], optional
        Allowed sub-command groups where new commands can be nested.
    admits_new_groups : bool, default=True
        Whether the plugin can add new sub-command groups.
    admits_top_level : bool, default=True
        Whether the plugin can add top-level commands.

    Notes
    -----
    Because new commands are not involved in the host application's execution flow, the constraints
    are related to the general CLI structure rather than to predefined and strict properties of the
    commands themselves.
    Usually the `unique` attribute is set to `False` since multiple commands can be nested in the
    same group, and the host application identifies all of them in a general list associated with
    the spec name.
    """
    CONTRIB_TYPE = Command

    def __init__(self, name: str,
                 groups: Optional[Set[str]] = None,
                 admits_new_groups: bool = True,
                 admits_top_level: bool = True,
                 required: bool = False,
                 unique: bool = False,
                 description: Optional[str] = None,
    ):
        super().__init__(name=name, required=required, unique=unique, description=description)
        # Configure CLI
        self.groups = groups or set()
        self.admits_new_groups = admits_new_groups
        self.admits_top_level = admits_top_level

    def validate(self, contrib: Command) -> bool:
        """Check if the command group is allowed by the host application."""
        if contrib.group is None and not self.admits_top_level:
            return False
        if contrib.group not in self.groups and not self.admits_new_groups:
            return False
        return True
