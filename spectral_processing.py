#!/usr/bin/env python3
"""Phase 2: Digital Signal Processing Pipeline.

Applies 60Hz IIR notch filtration, Hanning windowing matrices, 
and Real Fast Fourier Transforms (RFFT) to condition streaming analog signals.
"""
import numpy as np
from scipy.signal import iirnotch, lfilter


def apply_60hz_notch_filter(signal: np.ndarray, sample_rate: float) -> np.ndarray:
    """Designs and applies a sharp Direct Form II IIR 60Hz notch filter to remove grid hum."""
    if (sample_rate / 2.0) <= 60.0:
        return signal  # Bypasses filter if it violates Nyquist boundary limits
    b, a = iirnotch(w0=60.0, Q=30.0, fs=sample_rate)
    return lfilter(b, a, signal)


def create_hanning_window(length: int) -> np.ndarray:
    """Generates a standard Hanning window array for spectral smoothing."""
    return np.hanning(length)


class AsymmetricTensorPipeline:
    """Conditions multi-rate environmental signals into uniform spectral feature matrices."""

    def __init__(self, target_len: int = 1280):
        self.target_len = target_len

    def compile_feature_tensor(self, ch1: np.ndarray, ch2: np.ndarray, ch3: np.ndarray, ch4: np.ndarray) -> np.ndarray:
        """Processes 4 input streams, applying filters and dimensions alignment matches."""
        # Process and filter Channel 1 (Arboreal Bio-potentials)
        filtered_ch1 = apply_60hz_notch_filter(ch1, sample_rate=1000.0)
        window_1 = create_hanning_window(len(filtered_ch1))
        # Enforce an explicit n-point FFT to guarantee output vector length consistency
        fft_1 = np.abs(np.fft.rfft(filtered_ch1 * window_1, n=self.target_len * 2))[:self.target_len]

        # Process Channel 2 & 3 (Direct Time-Series Mycelial Ingestion)
        features_ch2 = ch2[:self.target_len]
        features_ch3 = ch3[:self.target_len]

        # Process and filter Channel 4 (Geophysical Background Field Monitoring)
        filtered_ch4 = apply_60hz_notch_filter(ch4, sample_rate=250.0)
        window_4 = create_hanning_window(len(filtered_ch4))
        fft_4 = np.abs(np.fft.rfft(filtered_ch4 * window_4, n=self.target_len * 2))[:self.target_len]

        # Assemble the clean data rows into a single multi-channel snapshot array
        feature_matrix = np.stack([fft_1, features_ch2, features_ch3, fft_4], axis=0)
        
        # Enforce z-score normalization along the temporal axis
        means = feature_matrix.mean(axis=1, keepdims=True)
        stds = feature_matrix.std(axis=1, keepdims=True) + 1e-8
        normalized_matrix = (feature_matrix - means) / stds

        return normalized_matrix.astype(np.float32)
