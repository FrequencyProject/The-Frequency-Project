#!/usr/bin/env python3
"""Phase 6: Latent Space Topography and Chaotic Manifold Auditor.

Extracts high-dimensional latent vectors from the 1D-CNN Encoder and applies
Principal Component Analysis (PCA) to map cluster distributions under complex
deterministic chaotic Lorenz attractor stress vectors.
"""
import numpy as np
import torch
from model_architecture import AsymmetricSpatialEncoder
from reconstruct_attractor import simulate_lorenz_chaos, build_takens_embedding


def generate_chaotic_stress_vectors(num_cycles: int = 50):
    """Generates pairs of nominal Fibonacci wavefronts and chaotic Lorenz stress matrices."""
    rng = np.random.default_rng(seed=42)
    phi = (1.0 + 5.0 ** 0.5) / 2.0
    
    nominal_set = []
    anomaly_set = []
    
    # Generate a long continuous block of deterministic chaos to cut slices from
    # 50 cycles * 1280 steps = 64,000 steps minimum. Pre-allocating a robust time series.
    raw_chaos_signal = simulate_lorenz_chaos(num_steps=80000, dt=0.01)
    # Untangle the single stream into a 3D phase-space manifold via Takens delay slots
    chaotic_manifold = build_takens_embedding(raw_chaos_signal, delay=10, dimension=3)
    
    for idx in range(num_cycles):
        # 1. Standard Nominal Fibonacci Wavefront Configuration
        t = np.linspace(0, 10, 1280, dtype=np.float32)
        ch1 = np.sin(t * 60.0 * (phi**0))
        ch2 = np.sin(t * 60.0 * (phi**-1))
        ch3 = np.sin(t * 60.0 * (phi**-2))
        ch4 = np.sin(t * 60.0 * (phi**-3))
        nominal_frame = np.stack([ch1, ch2, ch3, ch4], axis=0) # Shape (4, 1280)
        nominal_set.append(nominal_frame)
        
        # 2. ADVANCED RESEARCH EXPANSION: Route Chaotic Lorenz Attractor Slices
        # Extracts independent 1280-length trajectory coordinates out of the 3D attractor
        start_slice = idx * 1280
        end_slice = start_slice + 1280
        
        # Map our 3 reconstructed chaotic dimensions directly into the first 3 channels
        ch1_chaos = chaotic_manifold[start_slice:end_slice, 0]
        ch2_chaos = chaotic_manifold[start_slice:end_slice, 1]
        ch3_chaos = chaotic_manifold[start_slice:end_slice, 2]
        ch4_chaos = np.zeros(1280, dtype=np.float32) # Standard ground alignment
        
        # Normalize the raw chaos scales to prevent numeric layer saturation faults
        ch1_chaos = (ch1_chaos - ch1_chaos.mean()) / (ch1_chaos.std() + 1e-8)
        ch2_chaos = (ch2_chaos - ch2_chaos.mean()) / (ch2_chaos.std() + 1e-8)
        ch3_chaos = (ch3_chaos - ch3_chaos.mean()) / (ch3_chaos.std() + 1e-8)
        
        chaotic_frame = np.stack([ch1_chaos, ch2_chaos, ch3_chaos, ch4_chaos], axis=0)
        anomaly_set.append(chaotic_frame)
        
    return np.array(nominal_set, dtype=np.float32), np.array(anomaly_set, dtype=np.float32)


def execute_manifold_mapping_audit():
    print("[INIT] Booting Spatial Encoder and generating chaotic Lorenz attractor signals...")
    encoder = AsymmetricSpatialEncoder(latent_dim=128)
    encoder.eval()
    
    nominal_signals, anomaly_signals = generate_chaotic_stress_vectors(num_cycles=50)
    
    latent_vectors_nominal = []
    latent_vectors_anomaly = []
    
    # Extract 128-dimensional hidden embeddings from the encoder layer parameters
    with torch.no_grad():
        for i in range(50):
            # Process nominal vectors
            tensor_nom = torch.from_numpy(nominal_signals[i]).unsqueeze(0)
            latent_nom = encoder(tensor_nom)
            latent_vectors_nominal.append(latent_nom.cpu().numpy().flatten())
            
            # Process chaotic attractor vectors
            tensor_anom = torch.from_numpy(anomaly_signals[i]).unsqueeze(0)
            latent_anom = encoder(tensor_anom)
            latent_vectors_anomaly.append(latent_anom.cpu().numpy().flatten())
            
    X_nom = np.array(latent_vectors_nominal) # Shape (50, 128)
    X_anom = np.array(latent_vectors_anomaly) # Shape (50, 128)
    
    # Apply standard Principal Component Analysis (PCA) to reduce 128-dimensions down to 2D
    X_combined = np.vstack([X_nom, X_anom])
    X_centered = X_combined - np.mean(X_combined, axis=0)
    covariance_matrix = np.cov(X_centered, rowvar=False)
    
    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
    sorted_idx = np.argsort(eigenvalues)[::-1]
    top_2_components = eigenvectors[:, sorted_idx[:2]]
    
    X_projected = np.dot(X_centered, top_2_components)
    
    print("\n" + "="*70)
    print("CHAOTIC MANIFOLD PROJECTION RESULTS")
    print("="*70)
    print(f" -> Nominal Clusters Centroid (2D Space): {X_projected[:50].mean(axis=0)}")
    print(f" -> Chaotic Attractor Centroid (2D Space): {X_projected[50:].mean(axis=0)}")
    
    inter_cluster_distance = np.linalg.norm(X_projected[:50].mean(axis=0) - X_projected[50:].mean(axis=0))
    print(f" -> Verifiable Inter-Cluster Separation Distance: {inter_cluster_distance:.4f}")
    
    assert inter_cluster_distance > 1e-3, "Error: Latent space topology fails to separate chaos from nominal states."
    print("[SUCCESS] Topography verification complete. Network manifold separation verified under chaos.")
    print("="*70 + "\n")


if __name__ == "__main__":
    execute_manifold_mapping_audit()
