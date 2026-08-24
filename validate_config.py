#!/usr/bin/env python3
import os
import sys


def run_configuration_audit():
    print("[INIT] Launching repository structural validation scan...")
    target_toml = "pyproject.toml"
    target_requirements = "requirements.txt"
    target_workflow = ".github/workflows/ci.yml"

    if not all(os.path.exists(x) for x in [target_toml, target_requirements, target_workflow]):
        print("[ERROR] Missing critical repository architecture files.")
        sys.exit(1)

    try:
        with open(target_workflow, "r", encoding="utf-8") as f:
            wf = f.read()

        required_gates = ["black --check", "ruff check", "mypy", "pytest -v"]
        for gate in required_gates:
            if gate not in wf:
                print(f"[ERROR] Stale contract layout detected. Missing active CI gate: {gate}")
                sys.exit(1)

        print("[SUCCESS] Core technical infrastructure matrix checks out flawlessly.")
        sys.exit(0)
    except Exception as err:
        print(f"[FATAL] Code validation execution failure: {repr(err)}")
        sys.exit(1)


if __name__ == "__main__":
    run_configuration_audit()
