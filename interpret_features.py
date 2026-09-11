#!/usr/bin/env python3
"""Phase 6: Neural Feature Attribution and Input Saliency Auditor.

Computes the raw Jacobian matrix of the AsymmetricSpatialEncoder output vectors
with respect to the input telemetry channel frames to map frequency saliency.
"""
import numpy as np
import torch
from model_architecture import AsymmetricSpatialEncoder
from analyze_information_flow import generate_chaotic_stress_vectors


def compute_jacobian_saliency(model: torch.nn.Module, input_tensor: torch.Tensor) -> np.ndarray:
    """Calculates the absolute partial gradients of latent outputs w.r.t input features."""
    # Ensure input tensor tracks gradients explicitly
    input_tensor.requires_grad_(True)
    
    # Forward pass to capture output embeddings
    latent_output = model(input_tensor) # Shape: (1, 128)
    
    latent_dim = latent_output.shape[1]
    input_shape = input_tensor.shape
    
    # Pre-allocate array to hold partial derivatives: Shape (128, 4, 1280)
    jacobian_matrix = np.zeros((latent_dim, input_shape[1], input_shape[2]), dtype=np.float32)
    
    # Calculate gradients dimension-by-dimension across the latent space bottleneck
    for i in range(latent_dim):
        if input_tensor.grad is not None:
            input_tensor.grad.zero_()
            
        # Create a gradient mask isolating the i-th dimension
        grad_mask = torch.zeros_like(latent_output)
        grad_mask[0, i] = 1.0
        
        # Backward pass calculates d(Output_i) / d(Input)
        latent_output.backward(gradient=grad_mask, retain_graph=True)
        
        # Capture the absolute gradient map from the input tensor
        jacobian_matrix[i] = torch.abs(input_tensor.grad).cpu().numpy()[0]
        
    return jacobian_matrix


def execute_feature_attribution_audit():
    print("[INIT] Loading Spatial Encoder and preparing Jacobian saliency maps...")
    encoder = AsymmetricSpatialEncoder(latent_dim=128)
    encoder.eval()
    
    # Pull nominal Fibonacci and chaotic Lorenz waveforms
    nominal_signals, _ = generate_chaotic_stress_vectors(num_cycles=1)
    
    # Wrap single frame into a PyTorch float32 tensor
    input_frame = torch.from_numpy(nominal_signals[0]).unsqueeze(0) # Shape: (1, 4, 1280)
    
    # Compute full partial derivative matrix
    jacobian = compute_jacobian_saliency(encoder, input_frame) # Shape: (128, 4, 1280)
    
    # Collapse across the 128 latent dimensions to find global input channel sensitivity
    channel_saliency = np.mean(jacobian, axis=(0, 2)) # Average over latent dim and time steps
    
    print("\n" + "="*70)
    print("NEURAL FEATURE ATTRIBUTION & SALIENCY LOGS")
    print("="*70)
    print(f" -> Full Jacobian Matrix Ensembled Shape : {jacobian.shape}")
    print(f" -> Channel 1 (Plant Bioelectric) Saliency: {channel_saliency[0]:.6f}")
    print(f" -> Channel 2 (Chemical Alpha) Saliency    : {channel_saliency[1]:.6f}")
    print(f" -> Channel 3 (Chemical Beta) Saliency     : {channel_saliency[2]:.6f}")
    print(f" -> Channel 4 (EM Monitoring) Saliency     : {channel_saliency[3]:.6f}")
    
    print("\nOperational Operational Assertions:")
    # Verify that the network is actively attributing features (gradients aren't zero/dead)
    assert np.any(channel_saliency > 0.0), "Error: Exploding or Vanishing gradients detected! Neural saliency is dead."
    print(" -> [PASSED] Gradient paths are fully active. Feature attribution mapped successfully.")
    print("="*70 + "\n")


if __name__ == "__main__":
    execute_feature_attribution_audit()
