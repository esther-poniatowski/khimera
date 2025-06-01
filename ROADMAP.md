# ROADMAP

## TODO

- [ ] Move the `cli`functionality to a separate package.
- [ ] Review all modules for linting and formatting.
- [ ] Implement the adapter pattern to add plugin commands to the CLI.
- [ ] Add an attribute to `Plugin` to specify the host application they are intended for (to prevent
  accidental registration in the wrong application when multiple plugins are provided in the same
  package).
- [ ] Implement various discovery strategies and functions to automate trigger and configuration in
  host and user codes.
- [ ] Verify tests are well designed and cover all the code (how to analyze coverage?).
- [ ] Replace pytest_mock.MockFixture by only Fixture
- [ ] Add a `pyproject.toml` file to the project.
- [ ] Reformulate the `README.md` to reflect the new structure and features.
- [ ] Implement versioning: Add a `CHANGELOG.md` file, release notes, `VERSION` file, `__version__`
  attribute in the package, a `--version` command to the CLI, github workflow for releases.
- [ ] Write the final documentation with Sphinx and auto-generate the API reference.
- [ ] Distribute the package on PyPI.
- [ ] Implement plugin caching (not priority).
