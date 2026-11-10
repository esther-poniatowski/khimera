"""Tests for the reserved option `-v`/`--version` of the command line.

The command line runs in a subprocess, since importing the submodule ``khimera.cli.app`` replaces
the attribute ``app`` of the package ``khimera.cli`` within one interpreter.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from khimera import __version__

SOURCE_ROOT = Path(__file__).resolve().parents[3] / "src"


@pytest.mark.parametrize("flag", ["-v", "--version"])
def test_version_option_prints_the_version_without_a_command(flag: str) -> None:
    environment = {**os.environ, "PYTHONPATH": str(SOURCE_ROOT)}
    result = subprocess.run(
        [sys.executable, "-m", "khimera", flag],
        capture_output=True, text=True, env=environment, check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == __version__
