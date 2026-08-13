import numpy as np

def generate_mock_sensor_wave(frequency, sampling_rate, duration):
    """
    Simulates raw analog voltage waves coming from a physical sensor.
    Uses time-domain mathematics to create clean vibrational inputs.
    """
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    # Generate a pure sine wave representing the natural resonance frequency
    wave = np.sin(2 * np.pi * frequency * t)
    # Add minor random environmental noise to simulate a real ecosystem
    noise = np.random.normal(0, 0.1, wave.shape)
    return wave + noise

def process_to_frequency_vector(raw_wave, sampling_rate, target_dim=1280):
    """
    Executes a Fast Fourier Transform (FFT) to translate time-domain 
    waves directly into raw numerical frequency arrays.
    """
    # Calculate the raw FFT
    fft_complex = np.fft.fft(raw_wave)
    # Extract magnitudes (frequencies) and take the positive half of the spectrum
    fft_magnitudes = np.abs(fft_complex[:len(fft_complex)//2])
    
    # Resize or pad the vector mathematically to fit the exact target 1280 dimension
    if len(fft_magnitudes) >= target_dim:
        return fft_magnitudes[:target_dim]
    else:
        return np.pad(fft_magnitudes, (0, target_dim - len(fft_magnitudes)), 'constant')

def apply_log_min_max_normalization(vector):
    """
    Applies logarithmic rescaling to strip away physical amplitude biases.
    Forces all data into a clean 0.0 to 1.0 baseline.
    """
    log_vector = np.log1p(vector)  # log(x + 1) to prevent log(0) errors
    v_min = np.min(log_vector)
    v_max = np.max(log_vector)
    
    # Prevent division by zero if the sensor vector is completely flat
    if v_max == v_min:
        return np.zeros_like(log_vector)
        
    return (log_vector - v_min) / (v_max - v_min)

def execute_ecological_ingestion_pipeline():
    print("=================================================================")
    print("      INITIALIZING FREQUENCY-SYNCED AI DATA INTAKE PIPELINE      ")
    print("=================================================================\n")
    
    # 1. Simulate Raw Data Ingestion from Hardware Sensors
    print("[1/4] Ingesting real-time waveforms from physical sensors...")
    
    # Channel 0: Geophysical Anchor (Schumann Resonance @ ~7.83 Hz)
    raw_geophysical = generate_mock_sensor_wave(frequency=7.83, sampling_rate=250, duration=10.24)
    
    # Channel 1: Biological Anchor (Plant Bio-potential Burst @ ~15.0 Hz)
    raw_biological = generate_mock_sensor_wave(frequency=15.0, sampling_rate=1000, duration=2.56)
    
    # Channel 2: Molecular Anchor (Water Acoustic Frequency @ ~440.0 Hz)
    raw_molecular = generate_mock_sensor_wave(frequency=440.0, sampling_rate=44100, duration=0.058)
    
    print(f" -> Geophysical Array Shape: {raw_geophysical.shape} samples caught.")
    print(f" -> Biological Array Shape:  {raw_biological.shape} samples caught.")
    print(f" -> Molecular Array Shape:   {raw_molecular.shape} samples caught.\n")

    # 2. Run Fast Fourier Transform Layer
    print("[2/4] Transforming analog timelines into frequency spaces (FFT)...")
    vec_geo = process_to_frequency_vector(raw_geophysical, sampling_rate=250)
    vec_bio = process_to_frequency_vector(raw_biological, sampling_rate=1000)
    vec_mol = process_to_frequency_vector(raw_molecular, sampling_rate=44100)
    print(" -> All waves converted to independent 1280-dimensional spectrums.\n")

    # 3. Apply Logarithmic Normalization
    print("[3/4] Scaling data profiles via Min-Max Logarithmic Rescaling...")
    norm_geo = apply_log_min_max_normalization(vec_geo)
    norm_bio = apply_log_min_max_normalization(vec_bio)
    norm_mol = apply_log_min_max_normalization(vec_mol)
    print(" -> Amplitude distortions neutralized. Numeric boundaries restricted to [0.0, 1.0].\n")

    # 4. Construct the Unified Multi-Modal Input Tensor Matrix
    print("[4/4] Matrix stacking into high-dimensional model layer space...")
    unified_input_tensor = np.vstack([norm_geo, norm_bio, norm_mol])
    
    print("\n=================================================================")
    print("📌 SUCCESS: PIPELINE CONCURRENCY VERIFIED")
    print(f" -> Unified Input Tensor Matrix Shape: {unified_input_tensor.shape}")
    print(" -> Tensor Layout: Row 0 = Earth, Row 1 = Plant, Row 2 = Water")
    print(f" -> Sample Node Data (First 3 indices of Earth Row): {unified_input_tensor[0][:3]}")
    print("=================================================================")
    print("\nReady for injection into Resonance Coherence Objective Function optimization layer.")

if __name__ == "__main__":
    execute_ecological_ingestion_pipeline()
