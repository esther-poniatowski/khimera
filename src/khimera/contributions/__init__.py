#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.contributions
=====================

Components of plugins that contribute to the host application.

Each module in this package encapsulates the behavior of one type of plugin components. Each
inherits from the base classes `Contrib` and `CategorySpec` and tailors their attributes and methods
to the specific plugin components they represent.

Both the `Contrib` and `CategorySpec` classes are subclassed in parallel in each module, forming a
hierarchy of plugin components. The `Contrib` class represents the actual components provided by
plugin instances, while the `CategorySpec` class represents constraints for those components
according to the host application's requirements.

Modules
-------
core
    Core components of plugins.
metadata
    Metadata components of plugins.
commands
    Command components of plugins.
api
    API components of plugins.
hooks
    Hook components of plugins.
assets
    Asset components of plugins.


See Also
--------
khimera.contributions.core
    Base components of plugins models and instances.
"""
