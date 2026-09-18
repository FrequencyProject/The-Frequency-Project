#!/usr/bin/env python3
"""High-Assurance Unit Test Suite for the Repository Configuration Validator.

Validates integrity checks against clean manifests, correct hardware pin maps,
and structural error-handling boundary faults.
"""
import pytest
from unittest.mock import patch, mock_open
from validate_config import InfrastructureValidator

def test_validator_production_manifest_integrity():
    """Asserts that the canonical repository manifest passes all structural checks successfully."""
    validator = InfrastructureValidator()
    success = validator.verify_repository_integrity()
    assert success is True

def test_validator_detects_mismatched_cs_pin():
    """Asserts that an un-synchronized or legacy Chip Select pin triggers a strict failure state."""
    validator = InfrastructureValidator()

    # Mocking a corrupted firmware module where the CS pin is left at legacy GPIO 5
    mocked_corrupt_firmware = "const int ADC_CS_PIN = 5;\nconst int ADC_DRDY_PIN = 4;\n"

    # We load a valid structural manifest block so the check gets past block 1, 2, and 3 safely
    valid_manifest = b"""
    [project]
    dependencies = ["numpy", "scipy", "torch", "tpm2-pytss", "cryptography==50.0.0"]
    [tool.setuptools]
    py-modules = ["run_session", "sensor_adapter", "serial_daemon", "validate_config", "spectral_processing", "model_architecture", "resonance_loss", "train_engine", "latent_monitor", "prototype_simulation", "stress_harness", "config", "validate_phi_hypothesis"]
    [tool.pytest.ini_options]
    env = ["OMP_NUM_THREADS=1", "MKL_NUM_THREADS=1", "OPENBLAS_NUM_THREADS=1", "VECLIB_MAXIMUM_THREADS=1", "NUMEXPR_NUM_THREADS=1"]
    """

    def mock_open_multiple(path, *args, **kwargs):
        if "pyproject.toml" in str(path):
            return mock_open(read_data=valid_manifest).return_value
        return mock_open(read_data=mocked_corrupt_firmware).return_value

    with patch("os.path.exists", return_value=True), \
            patch("builtins.open", side_effect=mock_open_multiple):
        success = validator.verify_repository_integrity()

    assert success is False

def test_validator_detects_mismatched_drdy_pin():
    """Asserts that an un-synchronized Data Ready interrupt pin triggers a strict failure state."""
    validator = InfrastructureValidator()

    # Mocking a corrupted firmware module where the DRDY pin is misaligned to GPIO 2
    mocked_corrupt_firmware = "const int ADC_CS_PIN = 10;\nconst int ADC_DRDY_PIN = 2;\n"
    valid_manifest = b"""
    [project]
    dependencies = ["numpy", "scipy", "torch", "tpm2-pytss", "cryptography==50.0.0"]
    [tool.setuptools]
    py-modules = ["run_session", "sensor_adapter", "serial_daemon", "validate_config", "spectral_processing", "model_architecture", "resonance_loss", "train_engine", "latent_monitor", "prototype_simulation", "stress_harness", "config", "validate_phi_hypothesis"]
    [tool.pytest.ini_options]
    env = ["OMP_NUM_THREADS=1", "MKL_NUM_THREADS=1", "OPENBLAS_NUM_THREADS=1", "VECLIB_MAXIMUM_THREADS=1", "NUMEXPR_NUM_THREADS=1"]
    """

    def mock_open_multiple(path, *args, **kwargs):
        if "pyproject.toml" in str(path):
            return mock_open(read_data=valid_manifest).return_value
        return mock_open(read_data=mocked_corrupt_firmware).return_value

    with patch("os.path.exists", return_value=True), \
            patch("builtins.open", side_effect=mock_open_multiple):
        success = validator.verify_repository_integrity()

    assert success is False
