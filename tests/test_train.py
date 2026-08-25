#!/usr/bin/env python3
"""Unit test suite for verification of Phase 3 Training Engine loops."""
import numpy as np
import pytest
from train_engine import VivicTrainingEngine


def test_training_engine_initialization():
    """Confirms all internal model, optimizer, and data components link up flawlessly."""
    engine = VivicTrainingEngine(port="TEST_MOCK_PORT")
    assert engine.adapter.window_size == 1280
    assert hasattr(engine.model, "spectral_conv")
    assert len(engine.optimizer.param_groups) == 1


def test_training_step_warmup_gate():
    """Verifies that an un-saturated queue gracefully skips optimization without crashing."""
    engine = VivicTrainingEngine(port="TEST_MOCK_PORT")
    # Buffer is completely empty, should return the -1.0 warm-up status code
    loss_val = engine.train_step()
    assert loss_val == -1.0


def test_training_step_backprop_pass():
    """Validates that a saturated tensor window executes a clean backward pass gradient step."""
    engine = VivicTrainingEngine(port="TEST_MOCK_PORT")
    rng = np.random.default_rng(seed=101)

    # Force saturate the memory deques past the 1280 limit to trigger the operational path
    for _ in range(1285):
        v1, v2, v3, v4 = rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1), rng.normal(0, 1)
        packet = f"V1:{v1},V2:{v2},V3:{v3},V4:{v4}\n"
        engine.adapter.process_incoming_packet(packet)

    # Run the training step
    loss_val = engine.train_step()
    assert loss_val >= 0.0
