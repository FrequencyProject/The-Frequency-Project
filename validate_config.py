#!/usr/bin/env python3
"""Repository Configuration Audit and Integrity Validator Engine.

Scans package manifests, tooling configurations, and core neural network 
pipeline script dependencies to guarantee total system integrity.
"""
import os
import sys


def run_configuration_audit():
    print("======================================================================")
    print("VIVIC AI: HARDENED ECOSYSTEM PACKAGING & VALIDATION INTEGRATION ENGINE")
    print("======================================================================")

    target_toml = "pyproject.toml"
    target_requirements = "requirements.txt"

    # 1. Explicitly audit the presence of the absolute structural architecture files
    if not all(os.path.exists(x) for x in [target_toml, target_requirements]):
        print("[ERROR] Missing critical repository architecture configuration files.")
        sys.exit(1)

    # 2. Strict Core Pipeline Integrity Matrix Check
    # Ensures that refactors or accidental drops do not orphan critical modules
    core_pipeline_files = [
        "serial_daemon.py",
        "sensor_adapter.py",
        "spectral_processing.py",
        "model_architecture.py",
        "resonance_loss.py",
        "train_engine.py",
    ]

    print("[INIT] Scanning core multi-modal pipeline files...")
    for script_file in core_pipeline_files:
        if not os.path.exists(script_file):
            print(f"[FATAL ERROR] Incomplete Pipeline! Missing core file: '{script_file}'")
            sys.exit(1)
        print(f"[OK] Verified active pipeline file path integrity: '{script_file}'")

    try:
        with open(target_toml, "r", encoding="utf-8") as f:
            toml_content = f.read()

        # Verify the presence of critical production library dependencies
        required_deps = ['"numpy>=1.24.0"', '"scipy>=1.12.0"', '"pyserial>=3.5"']
        for dep in required_deps:
            if dep not in toml_content:
                print(f"[ERROR] Missing or unpinned core dependency: {dep}")
                sys.exit(1)

        # Audit explicit pinned developer tooling definitions
        if "black==24.10.0" not in toml_content or "ruff==0.14.1" not in toml_content:
            print("[ERROR] Pinned developer quality gates modified in pyproject.toml.")
            sys.exit(1)

        print("[SUCCESS] Package configurations and neural scripts match all criteria.")
        sys.exit(0)
    except Exception as err:
        print(f"[FATAL] Code validation execution failure: {repr(err)}")
        sys.exit(1)


if __name__ == "__main__":
    run_configuration_audit()
