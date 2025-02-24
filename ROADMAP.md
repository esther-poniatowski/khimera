# ROADMAP

## TODO

- [ ] Correct the `validate` test
- [ ] Create a dedicated directory for plugin discovery and loading
- [ ] Create a dedicated directory for plugin definition (models and instances)
- [ ] Create a dedicated directory for plugin validation and registration
- [ ] Implement various discovery strategies and functions to automate trigger and configuration in
  host and user codes
- [ ] implement the adapter pattern to add plugin commands to the CLI
- [ ] Add an attribute to Plugins to specify the host application they are intended for (to prevent
  accidental registration in the wrong application when multiple plugins are provided in the same package)
