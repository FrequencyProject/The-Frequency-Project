#!/usr/bin/env python3
"""Phase 10: Test Matrix for Optimization and Neural Training Engines."""
import numpy as np
import pytest
from train_engine import VivicTrainingEngine

def test_training_engine_initialization():
    """Validates that weights and loss metrics bind to active hardware topologies safely."""
    engine = VivicTrainingEngine(port="TEST_MOCK_PORT")
    assert engine.warmed_up is False
    assert engine.device is not None

def test_training_step_warmup_gate():
    """Verifies that an un-saturated queue gracefully skips optimization without crashing."""
    engine = VivicTrainingEngine(port="TEST_MOCK_PORT")
    # Buffer is completely empty, should return the -1.0 warm-up status code and None vector
    loss_val, latent_vector = engine.train_step()
    assert loss_val == -1.0
    assert latent_vector is None

def test_training_step_backprop_pass():
    """Validates that a saturated tensor window executes a clean backward pass gradient step."""
    engine = VivicTrainingEngine(port="TEST_MOCK_PORT")
    rng = np.random.default_rng(seed=101)

    # Force saturate the memory deques past the 1280 limit to trigger the operational path
    for _ in range(1285):
        v1, v2, v3, v4 = rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1)
        packet = f"V1:{v1},V2:{v2},V3:{v3},V4:{v4}\n"
        engine.adapter.process_incoming_packet(packet)

    # Run the training step and cleanly unpack both tuple parameters
    loss_val, latent_vector = engine.train_step()
    assert loss_val >= 0.0
    assert latent_vector is not None
