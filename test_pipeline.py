import numpy as np
import pytest
from prototype_simulation import process_to_frequency_vector, apply_log_min_max_normalization, generate_mock_sensor_wave

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

def test_vector_dimensions():
    """Verify that the FFT processing layer outputs exactly the target 1280 dimension size."""
    sampling_rate = 1000
    duration = 2.56
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    raw_wave = np.sin(2 * np.pi * 10 * t)
    
    vector = process_to_frequency_vector(raw_wave, sampling_rate, target_dim=1280)
    assert len(vector) == 1280, f"FFT output dimension was {len(vector)}, expected 1280"
