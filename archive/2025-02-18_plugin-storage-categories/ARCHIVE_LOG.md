# Archive Log

## Archive Details

- Date of archival: 2025-02-18
- Last commit hash on `main`: aefd79d96453b254771f6aefecd85bc2d81ccf27

## Reason for Archival

Experimental feature not pursued.

In the `Plugin` object, the separation of contributions between (flexible) specific storage
attributes was replaced by a central storage in the `contributions` attribute.

Reasons:

- The separation introduced unnecessary complexity to access the appropriate storage attribute each
  time a contribution is added or retrieved.
- A category-based separation could be achieved simply by the `filter` method itself, without hard-coded
  storage attributes.
- A centralised storage aligns with the structure of the `PluginModel`, where all specifications are stored
  in the `specifications` attribute.

## Contents

- `create.py` (origin: `src/khimera/plugins/create.py`)
  - Removed the `specific_storage` and `default_storage` attributes.
  - Removed the `get_storage` method.
  - Simplified the initialization of the `Plugin` object, the `add` method, the `get` method, and
    the `filter` method.
