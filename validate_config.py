#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def run_configuration_audit() -> None:
    print("[INIT] Launching repository structural validation scan...")
    target_toml = "pyproject.toml"
    target_requirements = "requirements.txt"
    workflows_dir = Path(".github/workflows")

    if not os.path.exists(target_toml) or not os.path.exists(target_requirements):
        print("[ERROR] Missing critical repository architecture files.")
        sys.exit(1)

    if not workflows_dir.exists():
        print("[ERROR] Missing .github/workflows directory.")
        sys.exit(1)

    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    if not workflow_files:
        print("[ERROR] No workflow YAML files found.")
        sys.exit(1)

    required_gates = ["black --check", "ruff check", "python -m mypy", "pytest -q"]

    for wf_path in workflow_files:
        try:
            wf = wf_path.read_text(encoding="utf-8")
            if all(gate in wf for gate in required_gates):
                print(f"[SUCCESS] Validation passed via workflow: {wf_path}")
                sys.exit(0)
        except Exception as err:
            print(f"[WARN] Could not read {wf_path}: {err!r}")

    print("[ERROR] No workflow contains all required CI gates.")
    for gate in required_gates:
        print(f" - required gate missing in aggregate validation target: {gate}")
    sys.exit(1)


if __name__ == "__main__":
    run_configuration_audit()
