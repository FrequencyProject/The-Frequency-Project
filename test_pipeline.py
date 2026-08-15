import sys
import numpy as np
from typing import Tuple

class IngestionOutput:
    """
    A unified wrapper object that encapsulates the pipeline output data layers.
    This prevents unpacking errors downstream by returning a single object instance.
    """
    def __init__(self, tensor: np.ndarray, plv_index: float):
        self.tensor = tensor
        self.plv = plv_index

    def __repr__(self):
        return f"IngestionOutput(tensor_shape={self.tensor.shape}, plv={self.plv:.4f})"


def generate_mock_sensor_wave(
    frequency: float,
    sampling_rate: int,
    duration: float,
    rng: np.random.Generator = None,
) -> np.ndarray:
    """Generates a raw time-series sensor wave using modern, isolated, thread-safe RNG Generators."""
    if rng is None:
        rng = np.random.default_rng()

    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    pure_wave = np.sin(2 * np.pi * frequency * t)
    noise = rng.normal(0, 0.2, len(t))
    return pure_wave + noise


def process_to_frequency_vector(
    raw_wave: np.ndarray,
    sampling_rate: int,
    target_dim: int = 1280,
    window: str = "hann",
) -> Tuple[np.ndarray, np.ndarray]:
    """Compute a stable magnitude-spectrum of the input signal with a reproducible
    number of frequency bins equal to target_dim.
    """
    if sampling_rate <= 0:
        raise ValueError("Sampling rate must be a strictly positive integer.")
    if target_dim <= 2:
        raise ValueError("Target dimension (target_dim) must be greater than 2.")
    if not np.all(np.isfinite(raw_wave)):
        raise ValueError("Input array raw_wave contains non-finite values (NaN/Inf).")

    nfft = 2 * (target_dim - 1)

    if len(raw_wave) >= nfft:
        frame = raw_wave[:nfft]
    else:
        frame = np.pad(raw_wave, (0, nfft - len(raw_wave)), "constant")

    if window == "hann":
        win = np.hanning(nfft)
        frame = frame * win

    fft_vals = np.abs(np.fft.rfft(frame, n=nfft))

    if len(fft_vals) != target_dim:
        if len(fft_vals) > target_dim:
            fft_vals = fft_vals[:target_dim]
        else:
            fft_vals = np.pad(fft_vals, (0, target_dim - len(fft_vals)), "constant")

    freqs = np.fft.rfftfreq(nfft, d=1.0 / sampling_rate)[:target_dim]
    return fft_vals, freqs


def apply_log_min_max_normalization(
    vector: np.ndarray, eps: float = 1e-12
) -> np.ndarray:
    log_vector = np.log1p(vector)
    v_min, v_max = np.min(log_vector), np.max(log_vector)
    denom = max(v_max - v_min, eps)
    return (log_vector - v_min) / denom


def compute_cross_channel_plv(signal_a: np.ndarray, signal_b: np.ndarray) -> float:
    """Computes the mathematical Phase-Locking Value (PLV) between two arrays using NumPy vectors."""
    fft_a = np.fft.fft(signal_a)
    fft_b = np.fft.fft(signal_b)
    
    phase_a = np.angle(fft_a)
    phase_b = np.angle(fft_b)
    
    phase_diff = phase_a - phase_b
    complex_vectors = np.exp(1j * phase_diff)
    plv = np.abs(np.mean(complex_vectors))
    return float(plv)


def execute_ecological_ingestion_pipeline(seed: int = 42) -> IngestionOutput:
    """Simulates natural channels, builds the 3x1280 matrix, calculates PLV, and returns an IngestionOutput object."""
    rng_geo = np.random.default_rng(seed)
    rng_bio = np.random.default_rng(seed + 1)
    rng_mol = np.random.default_rng(seed + 2)

    # Channel 1: Geophysical (Schumann Resonance baseline)
    schumann_raw = generate_mock_sensor_wave(
        frequency=7.83, sampling_rate=250, duration=10.24, rng=rng_geo
    )
    schumann_vec, _ = process_to_frequency_vector(
        schumann_raw, sampling_rate=250, target_dim=1280
    )
    schumann_norm = apply_log_min_max_normalization(schumann_vec)

    # Channel 2: Biological (Plant bio-potentials)
    plant_raw = generate_mock_sensor_wave(
        frequency=7.83, sampling_rate=1000, duration=10.24, rng=rng_bio
    )
    plant_vec, _ = process_to_frequency_vector(
        plant_raw, sampling_rate=1000, target_dim=1280
    )
    plant_norm = apply_log_min_max_normalization(plant_vec)

    # Channel 3: Molecular (Water acoustics)
    water_raw = generate_mock_sensor_wave(
        frequency=440.0, sampling_rate=44100, duration=10.24, rng=rng_mol
    )
    water_vec, _ = process_to_frequency_vector(
        water_raw, sampling_rate=44100, target_dim=1280
    )
    water_norm = apply_log_min_max_normalization(water_vec)

    # Calculate the Sovereign Common Tongue index (PLV) between Earth and Plant Layer
    min_length = min(len(schumann_raw), len(plant_raw))
    live_plv = compute_cross_channel_plv(schumann_raw[:min_length], plant_raw[:min_length])

    unified_tensor = np.stack([schumann_norm, plant_norm, water_norm])
    return IngestionOutput(tensor=unified_tensor, plv_index=live_plv)


if __name__ == "__main__":
    pipeline_result = execute_ecological_ingestion_pipeline()

    print("\n--- Initializing The Frequency Project Ecological Ingestion Engine ---")
    print(f"Pipeline Execution Result: {pipeline_result}")
    print(f"Success. Unified Input Tensor Matrix Built. Shape: {pipeline_result.tensor.shape}")
    print(f"Matrix Slice (First 5 data nodes):\n{pipeline_result.tensor[:, :5]}")
    print(f"Validation Bounds -> Minimum Scale: {np.min(pipeline_result.tensor):.4f} | Maximum Scale: {np.max(pipeline_result.tensor):.4f}")
    print(f"\nCurrent Sovereign Common Tongue Index (Earth <-> Plant PLV): {pipeline_result.plv:.4f}")
def test_ecological_pipeline_execution():
    """
    Automated test case for pytest to validate tensor shapes, value scaling,
    and Phase-Locking Value boundaries.
    """
    # Run the main pipeline engine
    result = execute_ecological_ingestion_pipeline()
    
    # 1. Verify a single, unified data wrapper object is returned
    assert isinstance(result, IngestionOutput), "Pipeline must return an IngestionOutput object."
    
    # 2. Verify the multi-modal tensor matrix dimension is exactly 3x1280
    assert result.tensor.shape == (3, 1280), f"Expected shape (3, 1280), got {result.tensor.shape}"
    
    # 3. Verify min-max normalization keeps bounds strictly between 0.0 and 1.0
    assert np.min(result.tensor) >= 0.0, "Normalization failure: minimum value below 0.0"
    assert np.max(result.tensor) <= 1.0, "Normalization failure: maximum value above 1.0"
    
    # 4. Verify Phase-Locking Value operates strictly within mathematical probability limits
    assert 0.0 <= result.plv <= 1.0, f"PLV index out of mathematical bounds: {result.plv}"
