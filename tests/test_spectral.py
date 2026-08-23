#!/usr/bin/env python3
"""Unit tests verifying Spectral Processing Module conditioning and shape logic."""
import numpy as np
import pytest
from spectral_processing import AsymmetricTensorPipeline, HardenedSignalConditioner

def test_notch_filter_suppression() -> None:
    conditioner = HardenedSignalConditioner()
    fs = 1000.0
    t = np.linspace(0, 1.0, int(fs))
    # Combine a pure 60Hz hum with a 120Hz signal
    raw_signal = np.sin(2 * np.pi * 60.0 * t) + np.sin(2 * np.pi * 120.0 * t)
    filtered = conditioner.apply_notch_filter(raw_signal, sample_rate=fs, target_freq=60.0)
    
    # Verify significant reduction in signal power
    assert np.std(filtered) < np.std(raw_signal)

def test_pipeline_output_tensor_dimensions() -> None:
    pipeline = AsymmetricTensorPipeline()
    ch1 = np.random.normal(0, 1, 2560)
    ch2 = np.random.normal(0, 1, 1280)
    ch3 = np.random.normal(0, 1, 1280)
    ch4 = np.random.normal(0, 1, 2560)
    
    tensor = pipeline.compile_feature_tensor(ch1, ch2, ch3, ch4)
    assert tensor.shape == (4, 1280)
    assert tensor.dtype == np.float32
    # Verify row independent scaling outputs close to zero-mean
    np.testing.assert_allclose(tensor.mean(axis=1), 0.0, atol=1e-5)
