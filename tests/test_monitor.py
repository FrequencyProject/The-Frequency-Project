#!/usr/bin/env python3
"""Unit test suite for verification of Phase 3 Latent Monitor tracking loops."""
import numpy as np
import pytest
from latent_monitor import VivicLatentMonitor


def test_monitor_initialization_bounds():
    """Confirms monitor metrics map correctly on the primary entry frame."""
    monitor = VivicLatentMonitor(latent_dim=64)
    mock_vector = np.random.normal(0, 1, 64)

    metrics = monitor.evaluate_vector(mock_vector)
    assert metrics["step"] == 1
    assert metrics["euclidean_delta"] == 0.0
    assert metrics["cosine_similarity"] == 1.0
    assert metrics["is_anomaly"] is False


def test_monitor_dimension_guard():
    """Verifies that vector sizing drops throw an explicit shape exception constraint."""
    monitor = VivicLatentMonitor(latent_dim=128)
    invalid_short_vector = np.zeros(100)

    with pytest.raises(ValueError, match="Expected latent dimension of 128"):
        monitor.evaluate_vector(invalid_short_vector)


def test_monitor_anomaly_detection_trajectory():
    """Validates that rapid geometric shifts trigger a three-sigma tracking alert."""
    monitor = VivicLatentMonitor(latent_dim=128, threshold_sigma=2.0)

    # Pre-load stable structural vector history configurations
    for _ in range(15):
        stable_vec = np.ones(128) * 0.05
        monitor.evaluate_vector(stable_vec)

    # Inject maximum displacement change shift
    spike_vec = np.ones(128) * 50.0
    metrics = monitor.evaluate_vector(spike_vec)

    assert metrics["is_anomaly"] is True
    assert monitor.anomalies_detected == 1
