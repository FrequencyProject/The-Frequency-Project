#!/usr/bin/env python3
"""Phase 2: Pre-Flight Configuration and Structural Validator."""
import sys
import pathlib

def verify_repository_integrity() -> bool:
    print("[INIT] Launching configuration and structural manifest audit...")
    p = pathlib.Path("pyproject.toml")
    if not p.exists():
        print("[CRITICAL] Missing master package manager manifest: pyproject.toml")
        return False
    
    manifest_text = p.read_text(encoding="utf-8").replace(" ", "")
    
    required_pins = ["torch==2.14.0", "cryptography==50.0.0"]
    for pin in required_pins:
        if pin not in manifest_text:
            print(f"[CRITICAL] Missing required version lock specification anchor: {pin}")
            return False
            
    print("[VALIDATED] Project dependencies and configuration structures verified.")
    return True

if __name__ == "__main__":
    if not verify_repository_integrity():
        sys.exit(1)
    print("[SUCCESS] Infrastructure configuration matrix: pyproject.toml loaded and validated successfully.")
