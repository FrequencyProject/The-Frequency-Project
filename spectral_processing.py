#!/usr/bin/env python3
"""Phase 1: Spectral Processing & Signal Conditioning Module.

Implements Direct Form II IIR Notch Filters, Hanning windowing, and asymmetric 
Real FFT magnitude conversions to compile a unified feature tensor.
"""
import numpy as np
import scipy.signal as signal

class HardenedSignalConditioner:
    """Manages active electrical hum filtration and spectral extraction transformations."""
    
    def __init__(self, q_factor: float = 30.0):
        self.q_factor = q_factor

    def apply_notch_filter(self, data: np.ndarray, sample_rate: float, target_freq: float = 60.0) -> np.ndarray:
        """Applies a sharp Direct Form II IIR notch filter to remove electrical grid pollution."""
        if sample_rate <= target_freq * 2:
            return data
        b, a = signal.iirnotch(target_freq, self.q_factor, fs=sample_rate)
        return signal.filtfilt(b, a, data)

    def extract_fft_magnitude(self, data: np.ndarray, expected_bins: int = 1280) -> np.ndarray:
        """Applies a Hanning window and computes the Real FFT magnitude spectrum."""
        windowed_data = data * np.hanning(len(data))
        rfft_vals = np.fft.rfft(windowed_data)
        magnitude = np.abs(rfft_vals)
        
        # Enforce deterministic padding or truncation without cyclic repetition
        if len(magnitude) > expected_bins:
            return magnitude[:expected_bins].astype(np.float32)
        elif len(magnitude) < expected_bins:
            return np.pad(magnitude, (0, expected_bins - len(magnitude)), 'constant').astype(np.float32)
        return magnitude.astype(np.float32)

class AsymmetricTensorPipeline:
    """Ingests multi-rate time-series signals and maps them to a uniform (4, 1280) matrix."""
    
    def __init__(self):
        self.conditioner = HardenedSignalConditioner()

    def compile_feature_tensor(self, ch1_raw: np.ndarray, ch2_raw: np.ndarray, 
                               ch3_raw: np.ndarray, ch4_raw: np.ndarray) -> np.ndarray:
        """Processes raw inputs through asymmetric paths to compile the unified AI tensor."""
        # Ch 1: Biotic (1000 Hz, 2560 samples -> 1280 spectral bins)
        ch1_filtered = self.conditioner.apply_notch_filter(ch1_raw, sample_rate=1000.0)
        ch1_features = self.conditioner.extract_fft_magnitude(ch1_filtered, expected_bins=1280)
        
        # Ch 2 & Ch 3: Mycelial Time-Series (20 Hz, 1280 samples)
        # Apply strict zero-padding or truncation instead of cyclic np.resize
        def process_time_series(raw_data: np.ndarray, sr: float) -> np.ndarray:
            filtered = self.conditioner.apply_notch_filter(raw_data, sample_rate=sr)
            if len(filtered) > 1280:
                return filtered[:1280].astype(np.float32)
            elif len(filtered) < 1280:
                return np.pad(filtered, (0, 1280 - len(filtered)), 'constant').astype(np.float32)
            return filtered.astype(np.float32)

        ch2_features = process_time_series(ch2_raw, sample_rate=20.0)
        ch3_features = process_time_series(ch3_raw, sample_rate=20.0)

        # Ch 4: Geophysical (250 Hz, 2560 samples -> 1280 spectral bins)
        ch4_filtered = self.conditioner.apply_notch_filter(ch4_raw, sample_rate=250.0)
        ch4_features = self.conditioner.extract_fft_magnitude(ch4_filtered, expected_bins=1280)

        # Stack into target dimension shape (4, 1280)
        tensor = np.vstack([ch1_features, ch2_features, ch3_features, ch4_features]).astype(np.float32)
        
        # Row-Independent Z-Score Normalization
        epsilon = 1e-8
        means = tensor.mean(axis=1, keepdims=True)
        stds = tensor.std(axis=1, keepdims=True)
        return (tensor - means) / (stds + epsilon)
