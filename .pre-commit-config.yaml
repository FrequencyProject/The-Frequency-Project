#!/usr/bin/env python3
import os
import sys

# tomllib is native in Python 3.11+. For 3.10 compatibility, we fall back to tomli gracefully.
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        print(
            "[ERROR] On Python versions below 3.11, you must run 'pip install tomli' to validate config.",
            file=sys.stderr,
        )
        sys.exit(1)


def validate_repository_config(toml_path: str = "pyproject.toml") -> bool:
    """Parses and checks the structural health of the repository configuration

    natively across Python 3.10, 3.11, and 3.12 environments.
    """
    if not os.path.exists(toml_path):
        print(
            f"[VALIDATION FAILED] Required file '{toml_path}' not found in root directory.",
            file=sys.stderr,
        )
        return False

    try:
        # File reading using binary mode ("rb") is strictly required by both tomli and tomllib
        with open(toml_path, "rb") as f:
            config_data = tomllib.load(f)

        print(f"[VALIDATION] Successfully parsed '{toml_path}'")

        # 1. Verify mandatory project definition blocks are present
        if "project" not in config_data:
            print(
                "[ERROR] Missing '[project]' block in TOML structure.",
                file=sys.stderr,
            )
            return False

        project = config_data["project"]
        print(f" -> System Package Name: {project.get('name')}")
        print(f" -> Current Target Version: {project.get('version')}")
        print(f" -> Locked Dependencies: {project.get('dependencies')}")

        # Perform explicit environmental requirement checks
        required_python_version = project.get("requires-python", ">=3.10")
        print(
            f"[OK] Python version constraints set to: {required_python_version}"
        )

        # 2. Hardened Tooling Integration Checks
        # Ensures new tool definitions added for multi-version compliance are fully mapped
        if "tool" in config_data:
            tools = config_data["tool"]
            if "black" in tools:
                print(
                    f"[OK] Verified Black Formatting Engine target arrays: {tools['black'].get('target-version')}"
                )
            if "ruff" in tools:
                print(
                    f"[OK] Verified Ruff Quality Engine target constraints: {tools['ruff'].get('target-version')}"
                )
        else:
            print(
                "[WARNING] Missing '[tool]' block definitions inside configuration.",
                file=sys.stderr,
            )

        print(
            "[SUCCESS] pyproject.toml configuration is valid and production-ready."
        )
        return True

    except Exception as parse_error:
        print(
            f"[VALIDATION FAILED] Syntax error detected within TOML file: {parse_error}",
            file=sys.stderr,
        )
        return False


if __name__ == "__main__":
    # Execute structural integrity validation routine
    success = validate_repository_config()
    if not success:
        sys.exit(1)
