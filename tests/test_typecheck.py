"""Test that verifies all project files pass type checking."""

import subprocess
from pathlib import Path


def test_typecheck():
    """Run pyright type checker on the project."""
    project_root = Path(__file__).parent.parent
    result = subprocess.run(
        ["pyright"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"Pyright failed:\n{result.stdout}\n{result.stderr}")
