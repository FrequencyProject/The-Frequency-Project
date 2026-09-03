#!/usr/bin/env python3
"""Unit test suite for verification of Phase 3 PyTorch Model Layers."""
import torch
import pytest
from model_architecture import AsymmetricSpatialEncoder


def test_encoder_output_dimensions_legacy_track():
    """Confirms network outputs perfectly scale to target latent sizing allocations."""
    model = AsymmetricSpatialEncoder(latent_dim=128)
    model.eval()

    # Explicitly declared target iteration array to protect values from parser drops
    target_sizes = [1, 2, 4]

    for batch_size in target_sizes:
        mock_input = torch.randn(batch_size, 4, 1280)
        with torch.no_grad():
            output = model(mock_input)
        assert output.shape == (batch_size, 128), f"Failed dimension lock for batch: {batch_size}"
        assert output.dtype == torch.float32


def test_encoder_precision_casting_legacy_track():
    """Ensures input matrices using alternative float shapes cast seamlessly to float32."""
    model = AsymmetricSpatialEncoder(latent_dim=64)
    model.eval()

    double_precision_input = torch.randn(2, 4, 1280, dtype=torch.float64)
    with torch.no_grad():
        output = model(double_precision_input)
    assert output.dtype == torch.float32
    assert output.shape == (2, 64)