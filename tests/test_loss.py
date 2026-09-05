#!/usr/bin/env python3
"""Unit and Integration Tests for the Resonance Coherence Loss Function.

Fully resolves continuous deployment Gap 6 by verifying scalar dimensions,
numerical stability boundaries, and backward gradient propagation flow.
"""
import torch
import pytest
from resonance_loss import ResonanceCoherenceLoss


def test_loss_scalar_dimension_compliance():
    """Asserts that the loss function properly condenses batches into a 0D scalar."""
    loss_engine = ResonanceCoherenceLoss()
    mock_latent_batch = torch.randn(4, 128)
    
    computed_loss = loss_engine(mock_latent_batch)
    
    assert computed_loss.dim() == 0, "Loss output must be a 0D scalar tensor."
    assert computed_loss.item() >= 0.0, "Loss output must be non-negative."


def test_loss_shape_contract_enforcement():
    """Asserts that inputs breaking the 2D tensor shape contract are rejected."""
    loss_engine = ResonanceCoherenceLoss()
    invalid_1d_tensor = torch.randn(128)
    invalid_3d_tensor = torch.randn(4, 2, 64)

    with pytest.raises(ValueError, match="Expected 2D matrix tensor batch"):
        loss_engine(invalid_1d_tensor)

    with pytest.raises(ValueError, match="Expected 2D matrix tensor batch"):
        loss_engine(invalid_3d_tensor)


def test_loss_gradient_flow_and_optimization():
    """ADVANCED VERIFICATION: Asserts that backward gradients flow seamlessly.

    Ensures that PyTorch gradients propagate back through the bidirectional
    Kullback-Leibler matrix and the Golden Ratio constraint penalty loop
    without returning dead or un-instantiated tracking blocks.
    """
    loss_engine = ResonanceCoherenceLoss()
    
    # 1. Instantiate a mock latent tracking batch with gradient tracking activated
    mock_vectors = torch.randn(4, 128, requires_grad=True)
    
    # 2. Execute the forward pass through the objective loss calculations
    loss_value = loss_engine(mock_vectors)
    
    # 3. Trigger the backward backpropagation pass
    loss_value.backward()
    
    # 4. Verify that the input tensor accumulated real gradient parameters
    assert mock_vectors.grad is not None, "Gradients failed to flow backward through the loss engine."
    assert not torch.isnan(mock_vectors.grad).any(), "Gradient graph returned corrupt NaN parameters."
    assert not torch.isinf(mock_vectors.grad).any(), "Gradient graph returned exploded Inf parameters."


def test_loss_extreme_numerical_stability():
    """ADVANCED VERIFICATION: Asserts numerical safety under severe edge-case stress inputs.

    Tests behavioral safety when processing massive outliers, uniform flatlines,
    and structural extreme values to guarantee that stabilized log-softmax layers
    prevent infinity underflow traps.
    """
    loss_engine = ResonanceCoherenceLoss()

    # Case A: Massive Outlier Values (Simulating a sudden extreme signal spike)
    spike_vectors = torch.ones(4, 128) * 1e6
    loss_spike = loss_engine(spike_vectors)
    assert not torch.isnan(loss_spike), "Loss engine crashed into NaN during an extreme signal spike."
    assert not torch.isinf(loss_spike), "Loss engine crashed into Inf during an extreme signal spike."

    # Case B: Absolute Zeros Flatline (Simulating a temporary sensor open-circuit dropout)
    flatline_vectors = torch.zeros(4, 128)
    loss_flatline = loss_engine(flatline_vectors)
    assert not torch.isnan(loss_flatline), "Loss engine crashed into NaN during an absolute sensor flatline."
    assert not torch.isinf(loss_flatline), "Loss engine crashed into Inf during an absolute sensor flatline."

    # Case C: Single-Item Batch Constraints (Verifying standard deviation safety)
    single_batch_vector = torch.randn(1, 128)
    loss_single = loss_engine(single_batch_vector)
    assert not torch.isnan(loss_single), "Loss engine crashed into NaN when processing a single-item batch snapshot."
    assert not torch.isinf(loss_single), "Loss engine crashed into Inf when processing a single-item batch snapshot."
