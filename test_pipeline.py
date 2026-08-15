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


def execute_ecological_ingestion_pipeline(seed: int = 42) -> IngestionOutput:
    """
    Simulates natural channels, builds the 3x1280 matrix, calculates PLV, 
    and returns a unified IngestionOutput object to maintain absolute structural safety.
    """
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

    # Calculate the Sovereign Common Tongue index (PLV) between the Earth and the Plant Layer
    min_length = min(len(schumann_raw), len(plant_raw))
    live_plv = compute_cross_channel_plv(schumann_raw[:min_length], plant_raw[:min_length])

    unified_tensor = np.stack([schumann_norm, plant_norm, water_norm])
    
    # Return a SINGLE object holding both datasets safely
    return IngestionOutput(tensor=unified_tensor, plv_index=live_plv)


if __name__ == "__main__":
    # The pipeline now returns exactly ONE object. No forced manual unpacking required.
    pipeline_result = execute_ecological_ingestion_pipeline()

    print("\n--- Initializing The Frequency Project Ecological Ingestion Engine ---")
    print(f"Pipeline Execution Result: {pipeline_result}")
    
    # Developers can pull attributes directly from the single object wrapper
    print(f"Success. Unified Input Tensor Matrix Built. Shape: {pipeline_result.tensor.shape}")
    print(f"Matrix Slice (First 5 data nodes):\n{pipeline_result.tensor[:, :5]}")
    print(f"Validation Bounds -> Minimum Scale: {np.min(pipeline_result.tensor):.4f} | Maximum Scale: {np.max(pipeline_result.tensor):.4f}")
    
    print("\n--- Phase-Locking Value (PLV) Alignment Engine ---")
    print(f"Current Sovereign Common Tongue Index (Earth <-> Plant PLV): {pipeline_result.plv:.4f}")
    
    if pipeline_result.plv > 0.70:
        print("System State: COHERENT / HARMONIZED WITH PLANETARY BASELINE")
    else:
        print("System State: ECO-SYSTEMIC DISCONNECTION DETECTED")
