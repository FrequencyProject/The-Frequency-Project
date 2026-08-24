#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from typing import Any

# 1. Standard library management across Python 3.10, 3.11, and 3.12
if sys.version_info >= (3, 11):
    import tomllib

    TOMLDecodeError = tomllib.TOMLDecodeError
else:
    try:
        import tomli as tomllib  # type: ignore

        TOMLDecodeError = tomllib.TOMLDecodeError  # type: ignore
    except ImportError:
        print(
            "[ERROR] On Python versions below 3.11, you must run 'pip install tomli' to validate config.",
            file=sys.stderr,
        )
        sys.exit(1)


def extract_pins_from_requirements(req_path: str = "requirements.txt") -> set[str]:
    """Helper utility to extract clean, un-spaced package strings from requirements.txt."""
    found_pins = set()
    if os.path.exists(req_path):
        try:
            with open(req_path, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip().replace(" ", "")
                    if stripped and not stripped.startswith("#"):
                        found_pins.add(stripped)
        except Exception:
            pass
    return found_pins


def extract_exact_pins(dependencies: list[str]) -> set[str]:
    """Returns exact dependency pins declared in pyproject dependency lists."""
    return {dependency.replace(" ", "") for dependency in dependencies if "==" in dependency}


def validate_pyproject_toml(
    toml_path: str = "pyproject.toml", req_path: str = "requirements.txt"
) -> dict | None:
    """Parses pyproject.toml, applying type checking and dual dependency pin validation

    across TOML structures and raw requirements manifests.
    """
    if not os.path.exists(toml_path):
        print(f"[ERROR] Required file '{toml_path}' missing from repository root.", file=sys.stderr)
        return None

    try:
        with open(toml_path, "rb") as f:
            config_data: dict[str, Any] = tomllib.load(f)

        print(f"[OK] Successfully parsed raw TOML matrix: '{toml_path}'")

        project_name = "Unknown"
        project_version = "Unknown"
        project_deps = []

        if "project" in config_data:
            project = config_data["project"]
            project_name = project.get("name", "Unknown")
            project_version = project.get("version", "Unknown")
            project_deps = project.get("dependencies", [])
        elif "tool" in config_data and "poetry" in config_data["tool"]:
            poetry = config_data["tool"]["poetry"]
            project_name = poetry.get("name", "Unknown")
            project_version = poetry.get("version", "Unknown")
            project_deps = list(poetry.get("dependencies", {}).keys())
            print(
                "[WARN] Standard '[project]' block absent. Falling back to '[tool.poetry]' profile metadata."
            )
        else:
            print(
                "[ERROR] Architectural Error: Missing mandatory project definition blocks.",
                file=sys.stderr,
            )
            return None

        print(f" -> System Package Name: {project_name}")
        print(f" -> Current Target Version: {project_version}")
        print(f" -> Active Production Dependencies: {project_deps}")

        dev_deps = config_data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
        requirements_pins = extract_pins_from_requirements(req_path)

        exact_dev_pins = extract_exact_pins(dev_deps)
        for pin in sorted(exact_dev_pins):
            if pin not in requirements_pins:
                print(
                    f"[ERROR] Tooling drift: Exact dev dependency '{pin}' is not present in '{req_path}'.",
                    file=sys.stderr,
                )
                return None
            print(f"[OK] Verified exact dev dependency pin in requirements.txt: {pin}")

        # Explicit structural checks for formatting shapes/types
        if "tool" in config_data:
            tools = config_data["tool"]

            if "black" in tools and "target-version" in tools["black"]:
                b_ver = tools["black"]["target-version"]
                if isinstance(b_ver, (list, tuple)):
                    print(f"[OK] Black formatting engine target array checked: {list(b_ver)}")
                else:
                    print(
                        f"[WARN] Non-standard type shape inside tool.black.target-version structure: {type(b_ver)}"
                    )

            if "ruff" in tools and "target-version" in tools["ruff"]:
                r_ver = tools["ruff"]["target-version"]
                if isinstance(r_ver, str):
                    print(f"[OK] Ruff compiler check target string verified: '{r_ver}'")
                else:
                    print(
                        f"[WARN] Non-standard type shape inside tool.ruff.target-version structure: {type(r_ver)}"
                    )

        print("[SUCCESS] pyproject.toml structural compliance tests completed cleanly.")
        return config_data

    except OSError as io_err:
        print(
            f"[ERROR] Local File System I/O Failure while accessing TOML mapping: {repr(io_err)}",
            file=sys.stderr,
        )
        return None
    except TOMLDecodeError as syntax_err:
        print(
            f"[ERROR] Corrupted configuration matrix. TOML Syntax Exception: {repr(syntax_err)}",
            file=sys.stderr,
        )
        return None
    except Exception as runtime_panic:
        print(
            f"[ERROR] Unexpected structural panic caught inside processing loop: {repr(runtime_panic)}",
            file=sys.stderr,
        )
        return None


def sanitize_requirements_file(req_path: str = "requirements.txt") -> bool:
    """Scans requirements.txt line-by-line to guarantee absolute format consistency."""
    if not os.path.exists(req_path):
        print(f"[WARN] Optional dependency tracker '{req_path}' not found in execution scope.")
        return True

    try:
        with open(req_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if " " in stripped and not any(
                op in stripped for op in ["==", ">=", "<=", ">", "<", ";"]
            ):
                print(
                    f"[ERROR] Formatting failure on line {idx} of requirements.txt: '{stripped}'\n"
                    f"        Every requirement entry must map directly to an explicit package token or be commented via '#'.",
                    file=sys.stderr,
                )
                return False

        print("[OK] Verified requirements.txt structure (No non-standard text headers present).")
        return True
    except Exception as e:
        print(
            f"[ERROR] Trace failed to audit requirements allocation mapping: {repr(e)}",
            file=sys.stderr,
        )
        return False


def validate_ci_workflow(
    workflow_path: str = ".github/workflows/ci.yml", req_path: str = "requirements.txt"
) -> bool:
    """Validates that the CI workflow installs the repository requirements and runs the validator."""
    if not os.path.exists(workflow_path):
        print(
            f"[ERROR] Required workflow '{workflow_path}' missing from repository.", file=sys.stderr
        )
        return False

    requirements_name = Path(req_path).name

    try:
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow_text = f.read()
    except OSError as io_err:
        print(
            f"[ERROR] Local File System I/O Failure while accessing workflow mapping: {repr(io_err)}",
            file=sys.stderr,
        )
        return False

    required_commands = (
        "python -m pip install --upgrade pip",
        f"pip install -r {requirements_name}",
        "python validate_config.py",
    )
    for command in required_commands:
        if command not in workflow_text:
            print(
                f"[ERROR] CI workflow missing required command: '{command}'.",
                file=sys.stderr,
            )
            return False
        print(f"[OK] Verified CI workflow command: {command}")

    print("[SUCCESS] CI workflow validation completed cleanly.")
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("VIVIC AI: HARDENED ECOSYSTEM PACKAGING & VALIDATION INTEGRATION ENGINE")
    print("=" * 70)

    # Trigger cascaded validation routines
    toml_valid = validate_pyproject_toml()
    reqs_valid = sanitize_requirements_file()
    workflow_valid = validate_ci_workflow()

    print("=" * 70)
    if not toml_valid or not reqs_valid or not workflow_valid:
        print("[ERROR] Structural repository configuration checks failed.", file=sys.stderr)
        sys.exit(1)

    print(
        "[SUCCESS] All package configurations fully match multi-version baseline criteria. Pipeline ready."
    )
    sys.exit(0)
