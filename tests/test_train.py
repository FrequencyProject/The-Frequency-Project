#!/usr/bin/env python3
"""Automated unit tests for the deep learning training engine optimization loops."""
import numpy as np
from train_engine import VivicTrainingEngine


def test_training_engine_initialization():
    """Confirms optimizer, core modules, and hyper-parameters mount cleanly."""
    engine = VivicTrainingEngine(port="MOCK")
    assert engine.optimizer is not None
    assert engine.model is not None


def test_training_step_warmup_gate():
    """Ensures empty deque structures safely trigger the -1.0 warmup flag."""
    engine = VivicTrainingEngine(port="REAL_HW_PORT")
    # Bypass simulation mode flag to explicitly trigger buffer check logic
    engine.is_mock = False

    loss_val = engine.train_step()
    assert loss_val == -1.0


def test_training_step_backprop_pass():
    """Verifies that active features yield stable, localized scalar PDI losses."""
    engine = VivicTrainingEngine(port="MOCK")
    loss_val = engine.train_step()

    # Loss should return a stable, non-exploding optimized value
    assert loss_val > 0.0
    assert loss_val < 50.0
