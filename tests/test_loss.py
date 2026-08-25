#!/usr/bin/env python3
"""Unit test suite for verification of Phase 3 PyTorch Loss Layers."""
import torch
import pytest
from resonance_loss import ResonanceCoherenceLoss


def test_loss_scalar_output():
    """Confirms loss calculations collapse to a clean, optimized scalar value for backprop."""
    loss_engine = ResonanceCoherenceLoss()
    mock_latents = torch.randn(4, 64)

    loss_val = loss_engine(mock_latents)

    # In PyTorch, loss objectives must return a zero-dimensional scalar tensor to trigger backward()
    assert loss_val.dim() == 0
    assert loss_val.item() >= 0.0


def test_loss_dimension_enforcement():
    """Ensures input shape compliance boundaries are actively guarded."""
    loss_engine = ResonanceCoherenceLoss()
    invalid_3d_tensor = torch.randn(2, 4, 128)

    with pytest.raises(ValueError, match="Expected 2D matrix tensor batch"):
        loss_engine(invalid_3d_tensor)


def test_loss_reproducibility_on_zeros():
    """Validates that dead sensor fields or uniform flatlines return stable numeric states."""
    loss_engine = ResonanceCoherenceLoss()
    flatline_latents = torch.zeros(2, 128)

    loss_val = loss_engine(flatline_latents)
    assert not torch.isnan(loss_val)
    assert not torch.isinf(loss_val)
