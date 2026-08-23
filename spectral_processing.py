#!/usr/bin/env python3
"""Phase 1: Spectral Processing & Signal Conditioning Module.

Implements Direct Form II IIR Notch Filters and Asymmetric Real FFT 
conversions to prepare raw analog feeds for Vivic AI network layers.
"""
import numpy as np
import scipy.signal as signal


class HardenedSignalConditioner:
    """Manages active electrical hum filtration and spectral extraction transformations."""

    def __init__(self, q_factor: float = 30.0):
        self.q_factor = q_factor

    def apply_notch_filter(
        self, data: np.ndarray, sample_rate: float, target_freq: float = 60.0
    ) -> np.ndarray:
        """Applies a sharp Direct Form II IIR notch filter to remove electrical grid pollution."""
        if sample_rate <= target_freq * 2:
            # Nyquist criteria safeguard: skip filtering if sampling rate is too low
            return data

        # Calculate filter coefficients
        b, a = signal.iirnotch(target_freq, self.q_factor, fs=sample_rate)

        # Execute zero-phase forward-backward digital filter to maintain temporal alignment
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data

    def extract_fft_magnitude(self, data: np.ndarray, expected_bins: int = 1280) -> np.ndarray:
        """Applies a Hanning window and computes the Real FFT magnitude spectrum."""
        # 1. Apply windowing to mitigate spectral leakage edge effects
        windowed_data = data * np.hanning(len(data))

        # 2. Compute the Real Fast Fourier Transform
        rfft_vals = np.fft.rfft(windowed_data)
        magnitude = np.abs(rfft_vals)

        # 3. Handle physical shape constraints precisely
        if len(magnitude) > expected_bins:
            return magnitude[:expected_bins].astype(np.float32)
        elif len(magnitude) < expected_bins:
            return np.pad(magnitude, (0, expected_bins - len(magnitude)), "constant").astype(
                np.float32
            )

        return magnitude.astype(np.float32)


class AsymmetricTensorPipeline:
    """Ingests multi-rate time-series signals and maps them to a uniform (4, 1280) matrix."""

    def __init__(self):
        self.conditioner = HardenedSignalConditioner()

    def compile_feature_tensor(
        self, ch1_raw: np.ndarray, ch2_raw: np.ndarray, ch3_raw: np.ndarray, ch4_raw: np.ndarray
    ) -> np.ndarray:
        """Processes raw inputs through asymmetric paths to compile the unified AI tensor."""

        # --- Channel 1: Biotic Anchor (1000 Hz, 2.56s = 2560 samples) ---
        ch1_filtered = self.conditioner.apply_notch_filter(ch1_raw, sample_rate=1000.0)
        ch1_features = self.conditioner.extract_fft_magnitude(ch1_filtered, expected_bins=1280)

        # --- Channel 2: Mycelial Subnetwork Alpha (20 Hz, 64s = 1280 samples) ---
        # Direct Time-Series Ingestion (FFT bypassed to monitor slow microvolt dc gradients)
        ch2_features = self.conditioner.apply_notch_filter(ch2_raw, sample_rate=20.0)
        if len(ch2_features) != 1280:
            ch2_features = np.resize(ch2_features, (1280,))

        # --- Channel 3: Mycelial Subnetwork Beta (20 Hz, 64s = 1280 samples) ---
        ch3_features = self.conditioner.apply_notch_filter(ch3_raw, sample_rate=20.0)
        if len(ch3_features) != 1280:
            ch3_features = np.resize(ch3_features, (1280,))

        # --- Channel 4: Geophysical Anchor (250 Hz, 10.24s = 2560 samples) ---
        ch4_filtered = self.conditioner.apply_notch_filter(ch4_raw, sample_rate=250.0)
        ch4_features = self.conditioner.extract_fft_magnitude(ch4_filtered, expected_bins=1280)

        # Stack into target dimension shape (4, 1280)
        tensor = np.vstack([ch1_features, ch2_features, ch3_features, ch4_features]).astype(
            np.float32
        )

        # Enforce Row-Independent Z-Score Normalization with Epsilon Guard
        epsilon = 1e-8
        means = tensor.mean(axis=1, keepdims=True)
        stds = tensor.std(axis=1, keepdims=True)
        normalized_tensor = (tensor - means) / (stds + epsilon)

        return normalized_tensor


if __name__ == "__main__":
    print("[INIT] Verifying Spectral Processing Module Engine Logic...")
    pipeline = AsymmetricTensorPipeline()

    # Generate realistic testing signals (mock inputs containing severe 60Hz hum artifacts)
    t_2560 = np.linspace(0, 2.56, 2560)
    t_1280 = np.linspace(0, 64.0, 1280)

    mock_ch1 = np.sin(2 * np.pi * 45 * t_2560) + np.sin(
        2 * np.pi * 60 * t_2560
    )  # 45Hz signal + 60Hz hum
    mock_ch2 = np.sin(2 * np.pi * 0.5 * t_1280)  # Slow 0.5Hz wave
    mock_ch3 = np.sin(2 * np.pi * 0.2 * t_1280)  # Slow 0.2Hz wave
    mock_ch4 = np.sin(2 * np.pi * 7.83 * t_2560) + np.sin(
        2 * np.pi * 60 * t_2560
    )  # 7.83Hz Schumann resonance + 60Hz hum

    out_tensor = pipeline.compile_feature_tensor(mock_ch1, mock_ch2, mock_ch3, mock_ch4)

    print("[SUCCESS] Feature Tensor Matrix Compiled.")
    print(f" -> Output Shape: {out_tensor.shape} (Expected: (4, 1280))")
    print(f" -> Output Precision Data Type: {out_tensor.dtype}")
    print(f" -> Row Means: {out_tensor.mean(axis=1)}")
    print(f" -> Row Standard Deviations: {out_tensor.std(axis=1)}")
