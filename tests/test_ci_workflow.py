#!/usr/bin/env python3
from pathlib import Path


def test_ci_dependency_install_step_avoids_unquoted_version_range_specs() -> None:
    workflow_path = Path(__file__).resolve().parents / ".github" / "workflows" / "vivic.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")
    assert "black --check" in workflow_text
    assert "ruff check ." in workflow_text
    assert "pytest -q" in workflow_text
