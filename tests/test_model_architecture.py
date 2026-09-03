#!/usr/bin/env python3
"""High-Assurance Unit Test Suite for the 1D-CNN Encoder Model Architecture.

Validates input shape firewalls against single-stream unbatched vectors, 
batched multi-dimensional tensors, and invalid dimension profiles.
"""
import pytest
import torch
from model_architecture import AsymmetricSpatialEncoder

def test_model_encoder_single_stream_unbatched_shape():
    """Asserts that raw unbatched (4, 1280) vectors are auto-expanded and processed cleanly."""
    model = AsymmetricSpatialEncoder(latent_dim=128)
    unbatched_tensor = torch.randn(4, 1280)
    
    model.eval()
    with torch.no_grad():
        output = model(unbatched_tensor)
        
    assert output.shape == (1, 128)

def test_model_encoder_parallel_batch_shape():
    """Asserts that multidimensional batched tensors (N, 4, 1280) process without channel shifts."""
    model = AsymmetricSpatialEncoder(latent_dim=128)
    batched_tensor = torch.randn(16, 4, 1280)  # Batch size of 16
    
    model.eval()
    with torch.no_grad():
        output = model(batched_tensor)
        
    assert output.shape == (16, 128)

def test_model_encoder_invalid_channel_rejection():
    """Asserts that input vectors breaking the 4-channel tracking anchor are instantly quarantined."""
    model = AsymmetricSpatialEncoder(latent_dim=128)
    invalid_channels = torch.randn(5, 1280)  # Broken channel trace
    
    with pytest.raises(ValueError, match="Model Input Firewall"):
        _ = model(invalid_channels)

def test_model_encoder_invalid_sequence_rejection():
    """Asserts that window frames breaking the 1280 timeline parameters are instantly blocked."""
    model = AsymmetricSpatialEncoder(latent_dim=128)
    invalid_sequence = torch.randn(4, 1200)  # Insufficient window metrics
    
    with pytest.raises(ValueError, match="Model Input Firewall"):
        _ = model(invalid_sequence)
