#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
khimera.components
==================

Specific plugin components that typically contribute to a host application.

Each module in this package encapsulates the behavior of one type of plugin components. Each
inherits from the base classes `Component` and `FieldSpec` and tailors their attributes and methods
to the specific plugin components they represent.

Both the `Component` and `FieldSpec` classes are subclassed in parallel in each module, forming a
hierarchy of plugin components. The `Component` class represents the actual components provided by
plugin instances, while the `FieldSpec` class represents constraints for those components
according to the host application's requirements.

Modules
-------
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
khimera.core.components
    Base components of plugins models and instances.
"""
