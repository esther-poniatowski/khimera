#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_khimera.test_components.test_assets
========================================

Tests for the component and specification classes for assets.

See Also
--------
khimera.components.assets
"""
# --- Silenced Errors ---
# pylint: disable=unused-variable
#   Test functions are used, but pylint does not detect it.

from pathlib import Path
import sys  # for manipulating sys.path
import shutil  # for copying directories

import pytest

from khimera.components.assets import Asset, AssetSpec


# --- Tests for Asset (Component) ------------------------------------------------------------------


def test_asset_initialization():
    """Test initialization of `Asset`."""
    mock_package = "test_package"
    mock_file = "test_file.txt"
    name = "test_asset"
    description = "Test asset"
    asset = Asset(name=name, file_path=mock_file, package=mock_package, description=description)
    assert asset.name == name
    assert asset.file_path == mock_file
    assert asset.package == mock_package
    assert asset.description == description


def test_asset_initialization_default_package():
    """Test initialization of `Asset` with default package."""
    mock_file = "test_file.txt"
    asset = Asset(name="test_asset", file_path=mock_file, package=None)
    assert asset.package == asset.__module__


@pytest.mark.parametrize(
    "file_path, package",
    [
        ("assets/image.png", "my_package"),
        ("config.json", "my_package.resources"),
    ],
)
def test_asset_initialization_various_paths(file_path, package):
    """Test initialization of `Asset` with various file paths and package."""
    asset = Asset(name="test_asset", file_path=file_path, package=package)
    assert asset.file_path == file_path
    assert asset.package == package


# --- Tests for Asset.get_path() method ------------------------------------------------------------


def test_asset_get_path_installed_package(tmp_path: Path):
    """
    Test the `Asset.get_path()` method for an installed package.

    Notes
    -----
    This test simulates the installation of a package by:

    1. Creating a mock package structure in a temporary directory provided by the `tmp_path`
       fixture. This basic package structure includes an `__init__.py` file and a test file.
    2. Copying the package to a temporary site-packages directory.
    3. Adding the site-packages directory to `sys.path` so that the package can be imported.

    At the end of the test:

    - The temporary directory is automatically cleaned up by the `tmp_path` fixture.
    - The temporary site-packages directory is manually removed from `sys.path`.
    """
    # Package and file details
    package_name = "test_package"
    file_name = "test_file.txt"
    file_content = "Test content"
    # Create a mock package structure
    package_dir = tmp_path / package_name
    package_dir.mkdir()
    (package_dir / "__init__.py").touch()
    (package_dir / file_name).write_text(file_content)
    # Simulate installation by copying the package to a temporary site-packages directory
    site_packages_dir = tmp_path / "site-packages"
    site_packages_dir.mkdir()
    installed_package_dir = site_packages_dir / package_name
    shutil.copytree(package_dir, installed_package_dir)
    # Add the site-packages directory to sys.path
    sys.path.insert(0, str(site_packages_dir))
    try:  # Create an asset and get the path with a context manager
        asset = Asset(name="test_asset", file_path=file_name, package=package_name)
        with asset.get_path() as path:
            assert isinstance(path, Path)
            assert path.name == file_name
            assert path.read_text() == file_content
            assert path.exists(), "Resource file does not exist."
            assert path.is_file(), "Resource is not a file."
    finally:  # Clean up
        sys.path.pop(0)


# --- Tests for AssetSpec (FieldSpec) -----------------------------------------------------------


def test_asset_spec_initialization():
    """Test initialization of `AssetSpec`."""
    name = "test_spec"
    file_ext = (".txt", ".pdf")
    required = True
    unique = False
    description = "Test asset field"
    asset_spec = AssetSpec(
        name=name,
        file_ext=file_ext,
        required=required,
        unique=unique,
        description=description,
    )
    assert asset_spec.name == name
    assert asset_spec.file_ext == file_ext
    assert asset_spec.required == required
    assert asset_spec.unique == unique
    assert asset_spec.description == description


def test_asset_spec_initialization_defaults():
    """Test initialization of `AssetSpec` with default values."""
    asset_spec = AssetSpec(name="test_spec")
    assert asset_spec.file_ext is None
    assert asset_spec.required is False
    assert asset_spec.unique is True


# --- Tests for AssetSpec validation ---------------------------------------------------------------


def test_asset_spec_validate_valid_extension():
    """Test `AssetSpec` validation with valid extension."""
    asset_spec = AssetSpec(name="test_spec", file_ext=(".txt", ".pdf"))
    asset = Asset(name="test_asset", file_path="test.txt", package="test_package")
    assert asset_spec.validate(asset) is True


def test_asset_spec_validate_invalid_extension():
    """Test `AssetSpec` validation with invalid extension."""
    asset_spec = AssetSpec(name="test_spec", file_ext=(".txt", ".pdf"))
    asset = Asset(name="test_asset", file_path="test.png", package="test_package")
    assert asset_spec.validate(asset) is False


def test_asset_spec_validate_no_extension_restriction():
    """Test `AssetSpec` validation with no extension restriction."""
    asset_spec = AssetSpec(name="test_spec")
    asset = Asset(name="test_asset", file_path="test.any", package="test_package")
    assert asset_spec.validate(asset) is True
