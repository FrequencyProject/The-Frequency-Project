#!/usr/bin/env python3
import sys
from pathlib import Path
from textwrap import dedent

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validate_config import validate_ci_workflow, validate_pyproject_toml


def test_validate_pyproject_toml_accepts_exact_dev_pins_in_requirements(
    tmp_path: Path,
) -> None:
    pyproject_path = tmp_path / "pyproject.toml"
    requirements_path = tmp_path / "requirements.txt"

    pyproject_path.write_text(
        dedent(
            """
            [project]
            name = "demo"
            version = "1.0.0"
            dependencies = ["numpy>=1.24.0"]

            [project.optional-dependencies]
            dev = ["black==24.10.0", "pytest>=7.3.0", "ruff==0.14.1"]
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    requirements_path.write_text(
        "numpy==1.26.4\nblack==24.10.0\nruff==0.14.1\npytest>=7.3.0\n",
        encoding="utf-8",
    )

    config = validate_pyproject_toml(str(pyproject_path), str(requirements_path))

    assert config is not None
    assert config["project"]["name"] == "demo"


def test_validate_pyproject_toml_rejects_missing_exact_dev_pins_in_requirements(
    tmp_path: Path, capsys
) -> None:
    pyproject_path = tmp_path / "pyproject.toml"
    requirements_path = tmp_path / "requirements.txt"

    pyproject_path.write_text(
        dedent(
            """
            [project]
            name = "demo"
            version = "1.0.0"
            dependencies = ["numpy>=1.24.0"]

            [project.optional-dependencies]
            dev = ["black==24.10.0", "ruff==0.14.1"]
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    requirements_path.write_text("numpy==1.26.4\nblack==24.10.0\n", encoding="utf-8")

    config = validate_pyproject_toml(str(pyproject_path), str(requirements_path))

    assert config is None
    assert "ruff==0.14.1" in capsys.readouterr().err


def test_validate_ci_workflow_checks_requirements_install_and_validator_step(
    tmp_path: Path,
) -> None:
    workflow_path = tmp_path / "ci.yml"
    workflow_path.write_text(
        dedent(
            """
            jobs:
              validate:
                steps:
                  - run: |
                      python -m pip install --upgrade pip
                      pip install -r requirements.txt
                  - run: |
                      python validate_config.py
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    assert validate_ci_workflow(str(workflow_path), "requirements.txt") is True
