import sys
import numpy as np
from typing import Tuple


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

    This function trims the input to nfft samples or zero-pads it to nfft before
    applying the window (truncation if longer, zero-padding if shorter).

    Amplitude Scaling Note:
        The returned raw magnitudes preserve the un-normalized absolute spectrum values.
        Downstream cross-channel normalization is delegated to the logarithmic min-max step.

    Returns:
      (fft_magnitudes, freqs) where freqs maps bins -> Hz (len = target_dim).
    """
    # Desired rfft bins D = target_dim -> nfft = 2*(D - 1)
    nfft = 2 * (target_dim - 1)

    # Prepare a time-domain frame of exactly nfft samples (trim or pad)
    if len(raw_wave) >= nfft:
        frame = raw_wave[:nfft]
    else:
        frame = np.pad(raw_wave, (0, nfft - len(raw_wave)), "constant")

    # Apply window of length nfft to reduce spectral leakage
    if window == "hann":
        win = np.hanning(nfft)
        frame = frame * win

    # rfft with explicit n
    fft_vals = np.abs(np.fft.rfft(frame, n=nfft))

    # Ensure length matches target_dim (rfft length should be target_dim)
    if len(fft_vals) != target_dim:
        if len(fft_vals) > target_dim:
            fft_vals = fft_vals[:target_dim]
        else:
            # Explicit assignment to catch and retain the zero-padded vector matrix
            fft_vals = np.pad(
                fft_vals, (0, target_dim - len(fft_vals)), "constant"
            )

    freqs = np.fft.rfftfreq(nfft, d=1.0 / sampling_rate)[:target_dim]
    return fft_vals, freqs


def apply_log_min_max_normalization(
    vector: np.ndarray, eps: float = 1e-12
) -> np.ndarray:
    log_vector = np.log1p(vector)
    v_min, v_max = np.min(log_vector), np.max(log_vector)
    denom = max(v_max - v_min, eps)
    return (log_vector - v_min) / denom


def execute_ecological_ingestion_pipeline(seed: int = 42) -> np.ndarray:
    """Simulates the three natural frequency channels using isolated RNG instances and outputs a 3x1280 tensor."""
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
        frequency=15.0, sampling_rate=1000, duration=2.56, rng=rng_bio
    )
    plant_vec, _ = process_to_frequency_vector(
        plant_raw, sampling_rate=1000, target_dim=1280
    )
    plant_norm = apply_log_min_max_normalization(plant_vec)

    # Channel 3: Molecular (Water acoustics)
    water_raw = generate_mock_sensor_wave(
        frequency=440.0, sampling_rate=44100, duration=0.058, rng=rng_mol
    )
    water_vec, _ = process_to_frequency_vector(
        water_raw, sampling_rate=44100, target_dim=1280
    )
    water_norm = apply_log_min_max_normalization(water_vec)

    unified_tensor = np.stack([schumann_norm, plant_norm, water_norm])
    return unified_tensor


if __name__ == "__main__":
    tensor = execute_ecological_ingestion_pipeline()

    # Gated behind a debug flag to keep testing, CI runs, and library imports silent
    if "--debug" in sys.argv:
        print(
            "Initializing The Frequency Project Ecological Ingestion Simulation..."
        )
        print(
            f"Success. Unified Matrix Tensor Shape Generated: {tensor.shape}"
        )
        print(f"Tensor Matrix Values (Truncated view):\n{tensor[:, :5]}")
        print(
            f"\nVerification Bounds -> Min value found: {np.min(tensor)}, Max value found: {np.max(tensor)}"
        )
