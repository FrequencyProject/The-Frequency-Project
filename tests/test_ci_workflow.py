import re
from pathlib import Path

from packaging.requirements import Requirement


def test_ci_dependency_install_step_avoids_unquoted_version_range_specs() -> None:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
    workflow_text = workflow_path.read_text(encoding="utf-8")

    for package in ("numpy", "pyserial", "black", "ruff"):
        assert f"pip install {package}" not in workflow_text
        assert f"python -m pip install {package}" not in workflow_text

    assert "docker build" in workflow_text
    assert "the-frequency-project:ci-gate" in workflow_text


def test_pyproject_torch_requirement_is_a_valid_cpu_pin() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^\s*"(torch[^"]*)",?$', pyproject_text, re.MULTILINE)

    assert match is not None
    requirement = Requirement(match.group(1))
    assert requirement.specifier == "==2.4.1+cpu"
