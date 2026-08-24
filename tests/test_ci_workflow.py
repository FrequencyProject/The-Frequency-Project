#!/usr/bin/env python3
"""Automated validation tests for the current CI workflow configuration."""
from pathlib import Path


def test_ci_workflow_installs_repository_requirements() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")

    assert "python -m pip install --upgrade pip" in workflow_text
    assert "pip install -r requirements.txt" in workflow_text


def test_ci_workflow_runs_validator_in_python_matrix() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")

    assert 'python-version: ["3.10", "3.11", "3.12"]' in workflow_text
    assert "python validate_config.py" in workflow_text
