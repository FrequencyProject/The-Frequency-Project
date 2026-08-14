import pytest
pytest.skip("tests moved to tests/test_ingest.py", allow_module_level=True)

def test_defensive_checks_invalid_inputs():
    """Validates that the ingestion layer explicitly drops and catches corrupt or dangerous input parameters."""
    valid_wave = np.sin(2 * np.pi * 7.83 * np.linspace(0, 1, 250))
    
    # 1. Test that a non-positive sampling rate explicitly fails with a ValueError
    with pytest.raises(ValueError, match="Sampling rate must be a strictly positive integer"):
        process_to_frequency_vector(valid_wave, sampling_rate=0)
        
    # 2. Test that an invalid small target dimension explicitly fails with a ValueError
    with pytest.raises(ValueError, match="Target dimension .* must be greater than 2"):
        process_to_frequency_vector(valid_wave, sampling_rate=250, target_dim=2)
        
    # 3. Test that non-finite values (like NaN or Infinity) trigger an immediate shutdown
    corrupt_wave = valid_wave.copy()
    corrupt_wave[0] = np.nan
    with pytest.raises(ValueError, match="Input array raw_wave contains non-finite values"):
        process_to_frequency_vector(corrupt_wave, sampling_rate=250)
