import numpy as np
import pytest
from prototype_simulation import (
    apply_log_min_max_normalization,
    execute_ecological_ingestion_pipeline,
    generate_mock_sensor_wave,
    process_to_frequency_vector,
)


def test_deterministic_rng_seeding():
    """Verifies that the multi-channel pipeline yields perfectly reproducible results across isolated runs."""
    tensor_a = execute_ecological_ingestion_pipeline(seed=42)
    tensor_b = execute_ecological_ingestion_pipeline(seed=42)
    np.testing.assert_array_equal(tensor_a, tensor_b)


def test_normalization_boundary_constraints():
    """Asserts that the log min-max scaling function strictly restricts output bounds between 0.0 and 1.0."""
    mock_vector = np.array([10.0, 50.0, 100.0, 1000.0])
    normalized = apply_log_min_max_normalization(mock_vector)
    assert np.min(normalized) >= 0.0
    assert np.max(normalized) <= 1.0


def test_flat_signal_and_epsilon_stability():
    """Confirms that the epsilon-stabilized denominator prevents division-by-zero crashes on dead sensor inputs."""
    flat_vector = np.ones(1280) * 5.0
    normalized = apply_log_min_max_normalization(flat_vector)
    assert np.all(normalized == 0.0)


def test_pipeline_output_tensor_shape():
    """Asserts that the multi-modal ingestion pipeline reliably outputs the exact unified target matrix dimensions."""
    tensor = execute_ecological_ingestion_pipeline(seed=101)
    assert tensor.shape == (3, 1280)


def test_defensive_checks_invalid_inputs():
    """Validates that the ingestion layer explicitly intercepts and handles corrupt or dangerous input arguments."""
    valid_wave = np.sin(2 * np.pi * 7.83 * np.linspace(0, 1, 250))

    # Validate non-positive sampling rate rejection
    with pytest.raises(
        ValueError, match="Sampling rate must be a strictly positive integer"
    ):
        process_to_frequency_vector(valid_wave, sampling_rate=0)

    # Validate target dimension minimum rejection
    with pytest.raises(
        ValueError, match="Target dimension .* must be greater than 2"
    ):
        process_to_frequency_vector(valid_wave, sampling_rate=250, target_dim=2)

    # Validate non-finite array tracking
    corrupt_wave = np.array([1.0, np.nan, 3.0])
    with pytest.raises(
        ValueError, match="Input array raw_wave contains non-finite values"
    ):
        process_to_frequency_vector(corrupt_wave, sampling_rate=250)
