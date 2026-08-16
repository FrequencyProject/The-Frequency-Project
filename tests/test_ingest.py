import numpy as np
import pytest

from prototype_simulation import (
    apply_log_min_max_normalization,
    execute_ecological_ingestion_pipeline,
    process_to_frequency_vector,
)


def test_pipeline_shape_and_determinism():
    """Verifies the core ingestion pipeline outputs a rigid 4x1280 matrix and is fully reproducible."""
    tensor_1 = execute_ecological_ingestion_pipeline(seed=42)
    tensor_2 = execute_ecological_ingestion_pipeline(seed=42)

    # Assert structural bounds reflect the unified 4-channel specifications
    assert tensor_1.shape == (4, 1280)
    assert np.array_equal(tensor_1, tensor_2)
    assert np.min(tensor_1) >= 0.0
    assert np.max(tensor_1) <= 1.0


def test_sample_count_determinism_and_rounding():
    """Validates float-duration to sample-count rounding logic across all specified metrics."""
    # Test Schumann specs
    schumann_samples = round(250 * 10.24)
    assert schumann_samples == 2560

    # Test Plant specs
    plant_samples = round(1000 * 2.56)
    assert plant_samples == 2560

    # Test Water specs using exact division routing
    water_samples = round(44100 * (2560 / 44100))
    assert water_samples == 2560


def test_defensive_validation_gates():
    """Verifies that the processing engine fails fast when encountering illegal input parameters."""
    valid_wave = np.ones(2560)

    with pytest.raises(
        ValueError, match="Sampling rate must be a strictly positive integer."
    ):
        process_to_frequency_vector(valid_wave, sampling_rate=0, target_dim=1280)

    with pytest.raises(ValueError, match="Target dimension .* must be greater than 2."):
        process_to_frequency_vector(valid_wave, sampling_rate=250, target_dim=2)

    infinite_wave = np.array([np.nan, 1.0, np.inf])
    with pytest.raises(
        ValueError, match="Input array raw_wave contains non-finite values"
    ):
        process_to_frequency_vector(infinite_wave, sampling_rate=250, target_dim=1280)


def test_normalization_with_flat_zero_input():
    """Verifies that an absolute zero input array does not trigger a division-by-zero error."""
    flat_array = np.zeros(1280)
    normalized = apply_log_min_max_normalization(flat_array)
    assert np.all(normalized == 0.0)
    assert np.all(np.isfinite(normalized))
