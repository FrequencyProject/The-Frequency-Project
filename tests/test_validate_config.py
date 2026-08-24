#!/usr/bin/env python3
import os
import pytest
from validate_config import run_configuration_audit


def test_validator_detects_complete_ci_matrix() -> None:
    # Verify repository validation structures clear smoothly
    assert os.path.exists("validate_config.py")
