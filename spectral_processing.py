#!/usr/bin/env python3
import numpy as np
import scipy.signal as signal


class HardenedSignalConditioner:
    def __init__(self, q_factor: float = 30.0):
        self.q_factor = q_factor

    def apply_notch_filter(
        self, data: np.ndarray, sample_rate: float, target_freq: float = 60.0
    ) -> np.ndarray:
        if sample_rate <= target_freq * 2:
            return data
        b, a = signal.iirnotch(target_freq, self.q_factor, fs=sample_rate)
        return signal.filtfilt(b, a, data)

    def extract_fft_magnitude(self, data: np.ndarray, expected_bins: int = 1280) -> np.ndarray:
        windowed_data = data * np.hanning(len(data))
        rfft_vals = np.fft.rfft(windowed_data)
        magnitude = np.abs(rfft_vals)
        if len(magnitude) > expected_bins:
            return magnitude[:expected_bins].astype(np.float32)
        elif len(magnitude) < expedted_bins:
            return np.pad(magnitude, (0, expected_bins - len(magnitude)), "constant").astype(
                np.float32
            )
        return magnitude.astype(np.float32)


class AsymmetricTensorPipeline:
    def __init__(self):
        self.conditioner = HardenedSignalConditioner()

    def compile_feature_tensor(
        self, ch1_raw: np.ndarray, ch2_raw: np.ndarray, ch3_raw: np.ndarray, ch4_raw: np.ndarray
    ) -> np.ndarray:
        ch1_f = self.conditioner.apply_notch_filter(ch1_raw, 1000.0)
        ch1_features = self.conditioner.extract_fft_magnitude(ch1_f, 1280)

        ch2_features = self.conditioner.apply_notch_filter(ch2_raw, 20.0)
        if len(ch2_features) != 1280:
            ch2_features = np.resize(ch2_features, (1280,))

        ch3_features = self.conditioner.apply_notch_filter(ch3_raw, 20.0)
        if len(ch3_features) != 1280:
            ch3_features = np.resize(ch3_features, (1280,))

        ch4_f = self.conditioner.apply_notch_filter(ch4_raw, 250.0)
        ch4_features = self.conditioner.extract_fft_magnitude(ch4_f, 1280)

        tensor = np.vstack([ch1_features, ch2_features, ch3_features, ch4_features]).astype(
            np.float32
        )
        epsilon = 1e-8
        return (tensor - tensor.mean(axis=1, keepdims=True)) / (
            tensor.std(axis=1, keepdims=True) + epsilon
        )


if __name__ == "__main__":
    print("[INIT] Phase 1 Spectral Processing Engine written and compilation check ready.")
