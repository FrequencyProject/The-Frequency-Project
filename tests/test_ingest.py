#!/usr/bin/env python3
"""Automated unit testing matrix for the cryptographically hardened ingestion engine."""
import pytest
import numpy as np
from sensor_adapter import MultiChannelSensorAdapter


@pytest.fixture
def clean_adapter() -> MultiChannelSensorAdapter:
    """Provides a fresh, isolated 4-channel sensor adapter instance before every test."""
    return MultiChannelSensorAdapter(port="MOCK_PORT", window_size=1280)


def test_tensor_dimension_compliance(clean_adapter: MultiChannelSensorAdapter) -> None:
    """Verifies that empty structures return zeros and saturated buffers compile a (4, 1280) tensor."""
    initial_tensor = clean_adapter.get_ai_features()
    assert initial_tensor.shape == (4, 1280)
    assert np.all(initial_tensor == 0.0)

    # Pre-saturate buffers with signed mock array frames
    mock_vector = np.array([1.0, -1.0, 0.5, -0.5], dtype=np.float32)
    p_bytes, s_bytes = clean_adapter.signer.sign_vector(mock_vector)

    for _ in range(2562):
        clean_adapter.process_signed_packet((p_bytes, s_bytes))

    saturated_tensor = clean_adapter.get_ai_features()
    assert saturated_tensor.shape == (4, 1280)
    assert not np.all(saturated_tensor == 0.0)


def test_row_independent_zscore_normalization(clean_adapter: MultiChannelSensorAdapter) -> None:
    """Ensures row-wise Z-score scaling enforces a mean of approx 0 and standard deviation of 1."""
    rng = np.random.default_rng(seed=42)

    # Inject dynamic multi-rate inputs with variance to satisfy Z-score denominators natively
    for _ in range(2565):
        mock_vector = rng.normal(0.0, 2.0, 4).astype(np.float32)
        p_bytes, s_bytes = clean_adapter.signer.sign_vector(mock_vector)
        clean_adapter.process_signed_packet((p_bytes, s_bytes))

    tensor = clean_adapter.get_ai_features()

    # Assert row-independent tracking criteria holds over changing distributions
    np.testing.assert_allclose(tensor.mean(axis=1), 0.0, atol=1e-5)
    np.testing.assert_allclose(tensor.std(axis=1), 1.0, atol=1e-4)


def test_malformed_string_packet_rejection(clean_adapter: MultiChannelSensorAdapter) -> None:
    """Confirms that invalid signatures are dropped immediately by the cryptographic gate."""
    bad_payload = b"MALICIOUS_INJECTION_DATA"
    bad_signature = b"INVALID_CRYPTO_SIGNATURE_KEY_BYTES"

    success = clean_adapter.process_signed_packet((bad_payload, bad_signature))
    assert success is False
    assert clean_adapter.metrics["frames_dropped_invalid_sig"] == 1


def test_epsilon_flatline_protection(clean_adapter: MultiChannelSensorAdapter) -> None:
    """Verifies that flat constant inputs do not trigger zero-division runtime exceptions."""
    flat_vector = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
    p_bytes, s_bytes = clean_adapter.signer.sign_vector(flat_vector)

    for _ in range(2562):
        clean_adapter.process_signed_packet((p_bytes, s_bytes))

    tensor = clean_adapter.get_ai_features()
    assert not np.isnan(tensor).any()
    assert not np.isinf(tensor).any()
