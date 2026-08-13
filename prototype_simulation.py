import numpy as np

def generate_mock_sensor_wave(frequency: float, sampling_rate: int, duration: float, rng: np.random.Generator = None) -> np.ndarray:
    """Generates a raw time-series sensor wave using modern, isolated, thread-safe RNG Generators."""
    if rng is None:
        rng = np.random.default_rng()
    
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    pure_wave = np.sin(2 * np.pi * frequency * t)
    noise = rng.normal(0, 0.2, len(t))
    return pure_wave + noise

def process_to_frequency_vector(raw_wave: np.ndarray, sampling_rate: int, target_dim: int = 1280, window: str = "hann") -> tuple[np.ndarray, np.ndarray]:
    """
    Compute a stable magnitude-spectrum with a reproducible number of frequency bins.
    Aligns the time-domain frame length precisely with nfft before windowing to prevent leakage.
    """
    nfft = 2 * (target_dim - 1)

    # Signal-processing correction: Explicitly align time-domain frame length to nfft
    if len(raw_wave) >= nfft:
        frame = raw_wave[:nfft]
    else:
        frame = np.pad(raw_wave, (0, nfft - len(raw_wave)), 'constant')

    # Apply window to the perfectly aligned frame length
    if window == "hann":
        win = np.hanning(nfft)
        raw_win = frame * win
    else:
        raw_win = frame

    fft_vals = np.abs(np.fft.rfft(raw_win, n=nfft))

    if len(fft_vals) != target_dim:
        fft_vals = np.resize(fft_vals, target_dim)

    freqs = np.fft.rfftfreq(nfft, d=1.0 / sampling_rate)[:target_dim]
    return fft_vals, freqs

def apply_log_min_max_normalization(vector: np.ndarray) -> np.ndarray:
    """Applies log scaling and safely normalizes data with strong epsilon numerical stability bounds."""
    log_vector = np.log1p(vector)
    v_min, v_max = np.min(log_vector), np.max(log_vector)
    
    # Epsilon numerical safety hardening to prevent tiny dynamic range instability
    eps = 1e-12
    if np.isclose(v_max, v_min, atol=eps):
        return np.zeros_like(log_vector)
        
    return (log_vector - v_min) / (v_max - v_min + eps)

def execute_ecological_ingestion_pipeline(seed: int = 42) -> np.ndarray:
    """Simulates three natural frequency channels, processes them with windowing, and stacks into a 3x1280 tensor."""
    rng_geo = np.random.default_rng(seed)
    rng_bio = np.random.default_rng(seed + 1)
    rng_mol = np.random.default_rng(seed + 2)

    # Channel 1: Geophysical (Schumann Resonance baseline)
    schumann_raw = generate_mock_sensor_wave(frequency=7.83, sampling_rate=250, duration=10.24, rng=rng_geo)
    schumann_vec, _ = process_to_frequency_vector(schumann_raw, sampling_rate=250, target_dim=1280)
    schumann_norm = apply_log_min_max_normalization(schumann_vec)

    # Channel 2: Biological (Plant bio-potentials)
    plant_raw = generate_mock_sensor_wave(frequency=15.0, sampling_rate=1000, duration=2.56, rng=rng_bio)
    plant_vec, _ = process_to_frequency_vector(plant_raw, sampling_rate=1000, target_dim=1280)
    plant_norm = apply_log_min_max_normalization(plant_vec)

    # Channel 3: Molecular (Water acoustics)
    water_raw = generate_mock_sensor_wave(frequency=440.0, sampling_rate=44100, duration=0.058, rng=rng_mol)
    water_vec, _ = process_to_frequency_vector(water_raw, sampling_rate=44100, target_dim=1280)
    water_norm = apply_log_min_max_normalization(water_vec)

    unified_tensor = np.stack([schumann_norm, plant_norm, water_norm])
    return unified_tensor

if __name__ == "__main__":
    print("Initializing The Frequency Project Ecological Ingestion Simulation...")
    tensor = execute_ecological_ingestion_pipeline()
    print(f"Success. Unified Matrix Tensor Shape Generated: {tensor.shape}")
    print(f"Tensor Matrix Values (Truncated view):\n{tensor[:, :5]}")
