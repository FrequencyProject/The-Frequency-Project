#!/usr/bin/env python3
"""Automated Validation Tests for Continuous Integration Pipeline Configuration."""
from pathlib import Path


def test_ci_dependency_install_step_avoids_unquoted_version_range_specs() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")

    for package in ("numpy", "pyserial", "black", "ruff"):
        assert f"pip install {package}" not in workflow_text
        assert f"python -m pip install {package}" not in workflow_text

    # Verify either unified or independent pip execution layout paths are structurally valid
    assert "pip install -r requirements.txt" in workflow_text
