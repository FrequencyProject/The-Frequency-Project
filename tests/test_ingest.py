import numpy as np
import pytest
from prototype_simulation import (
    process_to_frequency_vector,
    apply_log_min_max_normalization,
    execute_ecological_ingestion_pipeline,
)

def test_pipeline_shape_and_determinism():
    """Verifies the core ingestion pipeline outputs a rigid 3x1280 matrix and is fully reproducible."""
    tensor_1 = execute_ecological_ingestion_pipeline(seed=42)
    tensor_2 = execute_ecological_ingestion_pipeline(seed=42)
    
    # Assert structural bounds
    assert tensor_1.shape == (3, 1280)
    # Assert thread-safe RNG determinism
    assert np.array_equal(tensor_1, tensor_2)
    # Assert value boundaries match min-max expectations
    assert np.min(tensor_1) >= 0.0
    assert np.max(tensor_1) <= 1.0

def test_defensive_validation_gates():
    """Verifies that the processing engine fails fast when encountering illegal input parameters."""
    valid_wave = np.ones(2560)
    
    # Assert invalid sampling rates are rejected
    with pytest.raises(ValueError, match="Sampling rate must be a strictly positive integer."):
        process_to_frequency_vector(valid_wave, sampling_rate=0, target_dim=1280)
        
    # Assert insufficient target dimensions are rejected
    with pytest.raises(ValueError, match="Target dimension .* must be greater than 2."):
        process_to_frequency_vector(valid_wave, sampling_rate=250, target_dim=2)
        
    # Assert non-finite arrays are caught before processing
    infinite_wave = np.array([np.nan, 1.0, np.inf])
    with pytest.raises(ValueError, match="Input array raw_wave contains non-finite values"):
        process_to_frequency_vector(infinite_wave, sampling_rate=250, target_dim=1280)

def test_normalization_with_flat_zero_input():
    """Verifies that an absolute zero input array does not trigger a division-by-zero error."""
    flat_array = np.zeros(1280)
    normalized = apply_log_min_max_normalization(flat_array)
    # The pipeline should clamp flat vectors gracefully to zero due to epsilon boundaries
    assert np.all(normalized == 0.0)
    assert np.all(np.isfinite(normalized))

def test_normalization_with_tiny_variance_input():
    """Verifies computational stability when input data exhibits microscopic variance close to zero limits."""
    # Create an array with artificial variance compressed past standard epsilon margins
    tiny_variance_array = np.ones(1280) * 1.0 + np.random.default_rng(42).normal(0, 1e-20, 1280)
    normalized = apply_log_min_max_normalization(tiny_variance_array)
    assert np.all(np.isfinite(normalized))
    assert normalized.shape == (1280,)
