#!/usr/bin/env python3
import os
import sys

# 1. Standard library management across Python 3.10, 3.11, and 3.12
if sys.version_info >= (3, 11):
    import tomllib
    TOMLDecodeError = tomllib.TOMLDecodeError
else:
    try:
        import tomli as tomllib  # type: ignore
        TOMLDecodeError = tomllib.TOMLDecodeError # type: ignore
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


def validate_pyproject_toml(toml_path: str = "pyproject.toml") -> dict | None:
    """Parses pyproject.toml, applying type checking and dual dependency pin validation

    across TOML structures and raw requirements manifests.
    """
    if not os.path.exists(toml_path):
        print(f"[ERROR] Required file '{toml_path}' missing from repository root.", file=sys.stderr)
        return None

    try:
        with open(toml_path, "rb") as f:
            config_data = tomllib.load(f)

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
            print("[WARN] Standard '[project]' block absent. Falling back to '[tool.poetry]' profile metadata.")
        else:
            print("[ERROR] Architectural Error: Missing mandatory project definition blocks.", file=sys.stderr)
            return None

        print(f" -> System Package Name: {project_name}")
        print(f" -> Current Target Version: {project_version}")
        print(f" -> Active Production Dependencies: {project_deps}")

        # Copilot Optimization 1: Cross-check dependency pins across BOTH optional-deps and requirements.txt
        dev_deps = config_data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
        requirements_pins = extract_pins_from_requirements()
        
        # Consolidate all configured package rules into a single lookup set
        all_declared_deps = {dep.replace(" ", "") for dep in dev_deps} | requirements_pins
        
        required_pins = ["black==24.10.0", "ruff==0.14.1"]
        for pin in required_pins:
            if pin not in all_declared_deps:
                print(f"[ERROR] Tooling drift: Missing mandatory pin configuration '{pin}' in repo environment.", file=sys.stderr)
                return None
            print(f"[OK] Verified pinned quality gate dependency path: {pin}")

        # Explicit structural checks for formatting shapes/types
        if "tool" in config_data:
            tools = config_data["tool"]
            
            if "black" in tools and "target-version" in tools["black"]:
                b_ver = tools["black"]["target-version"]
                if isinstance(b_ver, (list, tuple)):
                    print(f"[OK] Black formatting engine target array checked: {list(b_ver)}")
                else:
                    print(f"[WARN] Non-standard type shape inside tool.black.target-version structure: {type(b_ver)}")
            
            if "ruff" in tools and "target-version" in tools["ruff"]:
                r_ver = tools["ruff"]["target-version"]
                if isinstance(r_ver, str):
                    print(f"[OK] Ruff compiler check target string verified: '{r_ver}'")
                else:
                    print(f"[WARN] Non-standard type shape inside tool.ruff.target-version structure: {type(r_ver)}")

        print("[SUCCESS] pyproject.toml structural compliance tests completed cleanly.")
        return config_data

    except OSError as io_err:
        print(f"[ERROR] Local File System I/O Failure while accessing TOML mapping: {repr(io_err)}", file=sys.stderr)
        return None
    except TOMLDecodeError as syntax_err:
        print(f"[ERROR] Corrupted configuration matrix. TOML Syntax Exception: {repr(syntax_err)}", file=sys.stderr)
        return None
    except Exception as runtime_panic:
        print(f"[ERROR] Unexpected structural panic caught inside processing loop: {repr(runtime_panic)}", file=sys.stderr)
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

            if " " in stripped and not any(op in stripped for op in ["==", ">=", "<=", ">", "<", ";"]):
                print(
                    f"[ERROR] Formatting failure on line {idx} of requirements.txt: '{stripped}'\n"
                    f"        Every requirement entry must map directly to an explicit package token or be commented via '#'.",
                    file=sys.stderr
                )
                return False

        print("[OK] Verified requirements.txt structure (No non-standard text headers present).")
        return True
    except Exception as e:
        print(f"[ERROR] Trace failed to audit requirements allocation mapping: {repr(e)}", file=sys.stderr)
        return False


def hunt_phantom_telemetry_tokens(root_dir: str = ".") -> bool:
    """Copilot Optimization 2: Actively sweeps explicitly permitted text extension files

    to isolate phantom telemetry references while avoiding binary scan performance overhead.
    """
    phantom_token = "test-requirements"
    exclusions = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".venv", "env", "venv"}
    valid_extensions = {".py", ".md", ".toml", ".yml", ".yaml", ".txt", ".patch", ".ino"}
    ghost_found = False

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclusions]
        for file in files:
            if file == "validate_config.py":
                continue
                
            _, ext = os.path.splitext(file)
            if ext.lower() not in valid_extensions:
                continue  # Skip unreadable binary formats, compiled libraries, and zip archives
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if phantom_token in content.lower():
                    print(f"[WARN] Phantom variable layout reference tracked inside file matrix: {file_path}")
                    ghost_found = True
            except Exception:
                continue

    if ghost_found:
        print("[ERROR] Telemetry matrix contains dead tokens. Review file metrics before build deployment.", file=sys.stderr)
        return False
    print(f"[OK] Global repository audit complete. Zero traces of '{phantom_token}' uncovered.")
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("VIVIC AI: HARDENED ECOSYSTEM PACKAGING & VALIDATION INTEGRATION ENGINE")
    print("=" * 70)

    # Trigger cascaded validation routines
    toml_valid = validate_pyproject_toml()
    reqs_valid = sanitize_requirements_file()
    phantom_clean = hunt_phantom_telemetry_tokens()

    print("=" * 70)
    if not toml_valid or not reqs_valid or not phantom_clean:
        print("[ERROR] Structural repository configuration checks failed.", file=sys.stderr)
        sys.exit(1)
        
    print("[SUCCESS] All package configurations fully match multi-version baseline criteria. Pipeline ready.")
    sys.exit(0)
