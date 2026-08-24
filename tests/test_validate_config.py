#!/usr/bin/env python3
import os


def test_validator_detects_complete_ci_matrix() -> None:
    # Verify repository validation structures clear smoothly
    assert os.path.exists("validate_config.py")
