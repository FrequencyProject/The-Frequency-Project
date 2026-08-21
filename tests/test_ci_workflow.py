from pathlib import Path


def test_ci_dependency_install_step_avoids_unquoted_version_range_specs() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")

    assert "numpy>=1.24.0,<2.0.0" not in workflow_text
    assert "pip install -r requirements.txt" in workflow_text
