import numpy as np

def generate_mock_sensor_wave(frequency: float, sampling_rate: int, duration: float, rng: np.random.Generator = None) -> np.ndarray:
    """Generates a raw time-series sensor wave using modern, isolated, thread-safe RNG Generators."""
    if rng is None:
        rng = np.random.default_rng()  # Fallback to an unseeded generator if none provided
    
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    # Generate core natural frequency wave
    pure_wave = np.sin(2 * np.pi * frequency * t)
    # Add random background environmental noise using the isolated generator instance
    noise = rng.normal(0, 0.2, len(t))
    return pure_wave + noise

def process_to_frequency_vector(raw_wave: np.ndarray, sampling_rate: int, target_dim: int = 1280) -> np.ndarray:
    """Applies a Fast Fourier Transform and resizes the array to match the target tensor dimension."""
    fft_values = np.abs(np.fft.rfft(raw_wave))
    
    if len(fft_values) == target_dim:
        return fft_values
    elif len(fft_values) > target_dim:
        return fft_values[:target_dim]
    else:
        return np.pad(fft_values, (0, target_dim - len(fft_values)), 'constant')

def apply_log_min_max_normalization(vector: np.ndarray) -> np.ndarray:
    """Applies log scaling and safely normalizes data between 0.0 and 1.0."""
    log_vector = np.log1p(vector)
    v_min, v_max = np.min(log_vector), np.max(log_vector)
    
    if np.isclose(v_max, v_min):
        return np.zeros_like(log_vector)
        
    return (log_vector - v_min) / (v_max - v_min)

def execute_ecological_ingestion_pipeline(seed: int = 42) -> np.ndarray:
    """Simulates the three natural frequency channels using isolated RNG instances and outputs a 3x1280 tensor."""
    # Instantiating isolated, thread-safe RNG instances for each unique data stream
    rng_geo = np.random.default_rng(seed)
    rng_bio = np.random.default_rng(seed + 1)
    rng_mol = np.random.default_rng(seed + 2)

    # Channel 1: Geophysical (Schumann Resonance baseline)
    schumann_raw = generate_mock_sensor_wave(frequency=7.83, sampling_rate=250, duration=10.24, rng=rng_geo)
    schumann_vec = process_to_frequency_vector(schumann_raw, sampling_rate=250, target_dim=1280)
    schumann_norm = apply_log_min_max_normalization(schumann_vec)

    # Channel 2: Biological (Plant bio-potentials)
    plant_raw = generate_mock_sensor_wave(frequency=15.0, sampling_rate=1000, duration=2.56, rng=rng_bio)
    plant_vec = process_to_frequency_vector(plant_raw, sampling_rate=1000, target_dim=1280)
    plant_norm = apply_log_min_max_normalization(plant_vec)

    # Channel 3: Molecular (Water acoustics)
    water_raw = generate_mock_sensor_wave(frequency=440.0, sampling_rate=44100, duration=0.058, rng=rng_mol)
    water_vec = process_to_frequency_vector(water_raw, sampling_rate=44100, target_dim=1280)
    water_norm = apply_log_min_max_normalization(water_vec)

    unified_tensor = np.stack([schumann_norm, plant_norm, water_norm])
    return unified_tensor

if __name__ == "__main__":
    print("Initializing The Frequency Project Ecological Ingestion Simulation...")
    tensor = execute_ecological_ingestion_pipeline()
    print(f"Success. Unified Matrix Tensor Shape Generated: {tensor.shape}")
    print(f"Tensor Matrix Values (Truncated view):\n{tensor[:, :5]}")
