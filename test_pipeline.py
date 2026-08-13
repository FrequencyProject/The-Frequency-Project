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
    
    # System should safely output a matrix of zeros rather than crashing
    assert np.all(normalized == 0.0), "Flat sensor reading failed to normalize safely to zeros matrix"

def test_deterministic_seeding():
    """Verify that passing an explicit seed parameter forces identical simulation outputs."""
    wave_1 = generate_mock_sensor_wave(frequency=7.83, sampling_rate=250, duration=5.0, seed=100)
    wave_2 = generate_mock_sensor_wave(frequency=7.83, sampling_rate=250, duration=5.0, seed=100)
    wave_3 = generate_mock_sensor_wave(frequency=7.83, sampling_rate=250, duration=5.0, seed=200)

    assert np.array_equal(wave_1, wave_2), "Deterministic seeding failed; identical seeds yielded unique outputs"
    assert not np.array_equal(wave_1, wave_3), "Seeding failed; unique seeds yielded identical outputs"

def test_vector_dimensions():
    """Verify that the FFT processing layer outputs exactly the target 1280 dimension size."""
    sampling_rate = 1000
    duration = 2.56
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    raw_wave = np.sin(2 * np.pi * 10 * t)
    
    vector = process_to_frequency_vector(raw_wave, sampling_rate, target_dim=1280)
    assert len(vector) == 1280, f"FFT output dimension was {len(vector)}, expected 1280"

