#!/usr/bin/env python3
"""Phase 10: High-Assurance Hardware TPM Exception Taxonomy Unit Tests."""
import pytest
from secure_hardware_vault import SecureHardwareVault, SecurityTamperException, HardwareBusException

def test_vault_initialization_fallback_mode():
    """Validates that setting tcti to none bypasses hardware scans cleanly for software mode."""
    vault = SecureHardwareVault(tcti_profile="none")
    assert vault.initialize_tpm_session() is True
    assert vault.is_sealed is False

def test_vault_retry_mechanism_on_bus_timeout(monkeypatch):
    """Asserts that transient line jitter triggers a 3-pass retry cycle before failure."""
    import tpm2_pytss
    
    vault = SecureHardwareVault(tcti_profile="mock_bus_profile")
    attempt_counter = 0

    class MockTSSTimeoutException(Exception):
        def __init__(self):
            self.rc = 0x101  # Retryable status flag

    def mock_esapi_timeout(*args, **kwargs):
        nonlocal attempt_counter
        attempt_counter += 1
        raise MockTSSTimeoutException()

    monkeypatch.setattr("tpm2_pytss.ESAPI", mock_esapi_timeout)

    with pytest.raises(HardwareBusException):
        vault.initialize_tpm_session()

    assert attempt_counter == 3

def test_vault_immediate_alert_on_policy_tampering(monkeypatch):
    """Asserts that a PCR-7 mismatch (0x9A) triggers an immediate security fail-secure breach."""
    import tpm2_pytss
    
    vault = SecureHardwareVault(tcti_profile="mock_bus_profile")
    attempt_counter = 0

    class MockTSSTamperException(Exception):
        def __init__(self):
            self.rc = 0x9A  # Policy validation tamper code

    def mock_esapi_tamper(*args, **kwargs):
        nonlocal attempt_counter
        attempt_counter += 1
        raise MockTSSTamperException()

    monkeypatch.setattr("tpm2_pytss.ESAPI", mock_esapi_tamper)

    with pytest.raises(SecurityTamperException):
        vault.initialize_tpm_session()

    # Integrity Breach Rule: Halt immediately on pass 1
    assert attempt_counter == 1
