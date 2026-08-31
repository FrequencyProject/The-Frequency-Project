import torch
import pytest
from model_architecture import AsymmetricSpatialEncoder

def test_model_encoder_batch_and_single_sample_shapes():
    """Validates that GroupNorm and Linear layers process variable batches without crashing."""
    model = AsymmetricSpatialEncoder(latent_dim=128)
    model.eval()
    
    # 1. Test standard training batch processing
    batch_tensor = torch.randn(4, 4, 1280)
    out_batch = model(batch_tensor)
    assert out_batch.shape == (4, 128), "Batch feature extraction dimension mismatch encountered."
    
    # 2. Test single-sample live stream tracking (Hot Path)
    stream_tensor = torch.randn(1, 4, 1280)
    out_stream = model(stream_tensor)
    assert out_stream.shape == (1, 128), "Stream sample extraction dimension mismatch encountered."

def test_model_encoder_automatic_dimension_expansion():
    """Verifies that the model automatically pads unbatched 2D matrices into 3D spaces."""
    model = AsymmetricSpatialEncoder(latent_dim=128)
    model.eval()
    
    # Pass a raw unbatched (4, 1280) matrix tensor
    unbatched_tensor = torch.randn(4, 1280)
    out = model(unbatched_tensor)
    
    # Output must expand to shape (1, latent_dim) smoothly
    assert out.shape == (1, 128)
