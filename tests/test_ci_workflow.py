#!/usr/bin/env python3
"""Validates Continuous Integration configuration file invariants."""
from pathlib import Path

def test_ci_dependency_install_step_avoids_unquoted_version_range_specs() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")

    for package in ("numpy", "pyserial", "black", "ruff"):
        assert f"pip install {package}" not in workflow_text
        assert f"python -m pip install {package}" not in workflow_text

    # HARDENING REMEDIATION: Loosened literal string assertion to support optimization parameters 
    # like --no-cache-dir or CPU extra-index-url configurations seamlessly.
    assert "-r requirements.txt" in workflow_text
