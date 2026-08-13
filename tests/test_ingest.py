import numpy as np
import pytest
from prototype_simulation import process_to_frequency_vector, apply_log_min_max_normalization, generate_mock_sensor_wave, execute_ecological_ingestion_pipeline

def test_normalization_bounds():
    """Verify that the Logarithmic Rescaling forces data strictly between 0.0 and 1.0."""
    mock_vector = np.array([0.0, 10.5, 500.2, 10000.0, 999999.0])
    normalized = apply_log_min_max_normalization(mock_vector)

    assert np.min(normalized) >= 0.0, "Normalization dropped below 0.0"
    assert np.max(normalized) <= 1.0, "Normalization exceeded 1.0"
    assert np.isclose(normalized[0], 0.0), "Minimum value failed to map to 0.0"
    assert np.isclose(normalized[-1], 1.0), "Maximum value failed to map to 1.0"

def test_normalization_edge_case_flat_signal():
    """Verify that a completely static/flat sensor reading does not crash the system with division-by-zero."""
    flat_vector = np.array([10.0, 10.0, 10.0, 10.0])
    normalized = apply_log_min_max_normalization(flat_vector)
    assert np.all(normalized == 0.0), "Flat sensor reading failed to normalize safely to zeros matrix"

def test_normalization_small_variance():
    """Verify that an extremely tiny dynamic range variation remains numerically stable without NaN outputs."""
    tiny_variance_vector = np.array([1.000000000001, 1.000000000002, 1.000000000001])
    normalized = apply_log_min_max_normalization(tiny_variance_vector)
    assert not np.isnan(normalized).any(), "Small variance caused unstable NaN values inside normalization layer"
    assert not np.isinf(normalized).any(), "Small variance caused infinite scaling inside normalization layer"

def test_deterministic_generator_seeding():
    """Verify that using isolated numpy Generator instances forces identical deterministic simulation outputs."""
    rng_1a = np.random.default_rng(42)
    rng_1b = np.random.default_rng(42)
    rng_2  = np.random.default_rng(100)

    wave_1a = generate_mock_sensor_wave(frequency=7.83, sampling_rate=250, duration=5.0, rng=rng_1a)
    wave_1b = generate_mock_sensor_wave(frequency=7.83, sampling_rate=250, duration=5.0, rng=rng_1b)
    wave_2  = generate_mock_sensor_wave(frequency=7.83, sampling_rate=250, duration=5.0, rng=rng_2)

    assert np.array_equal(wave_1a, wave_1b), "Isolated generators with matching seeds produced unique outputs"
    assert not np.array_equal(wave_1a, wave_2), "Isolated generators with unique seeds produced identical outputs"

def test_vector_dimensions_and_frequency_peak():
    """Verify that the FFT processing layer outputs exactly the target 1280 dimension size and peaks near a pure tone."""
    sampling_rate = 1000
    target_dim = 1280
    nfft = 2 * (target_dim - 1)
    duration = 2.56
    
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    raw_wave = np.sin(2 * np.pi * 10 * t)  # Simulate pure 10 Hz tone

    vector, freqs = process_to_frequency_vector(raw_wave, sampling_rate, target_dim=target_dim)
    assert len(vector) == 1280, f"FFT output dimension was {len(vector)}, expected 1280"
    assert len(freqs) == 1280, f"Frequency axis length was {len(freqs)}, expected 1280"

    peak_idx = int(np.argmax(vector))
    
    # Calculate exact mathematical grid spacing resolution: Delta_f = fs / nfft
    frequency_resolution = sampling_rate / nfft
    
    # Assert peak accuracy strictly within the physical grid resolution boundary
    assert abs(freqs[peak_idx] - 10.0) <= frequency_resolution, f"Peak frequency {freqs[peak_idx]} exceeded exact mathematical grid resolution bound"

def test_execute_pipeline_shape():
    """Verify that the full multi-channel integration pipeline aggregates exactly into a 3x1280 stacked tensor."""
    unified_tensor = execute_ecological_ingestion_pipeline(seed=123)
    assert unified_tensor.shape == (3, 1280), f"Pipeline shape mismatch: generated {unified_tensor.shape}, expected (3, 1280)"
