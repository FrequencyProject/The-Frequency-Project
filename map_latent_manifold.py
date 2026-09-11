#!/usr/bin/env python3
"""Phase 6: Latent Space Topography and Manifold Auditor.

Extracts high-dimensional latent vectors from the 1D-CNN Encoder and applies
Principal Component Analysis (PCA) to map cluster distributions under structural stress.
"""
import numpy as np
import torch
from model_architecture import AsymmetricSpatialEncoder


def generate_stress_vectors(num_cycles: int = 100):
    """Generates pairs of nominal and structurally anomalies signal matrices."""
    rng = np.random.default_rng(seed=42)
    phi = (1.0 + 5.0 ** 0.5) / 2.0
    
    nominal_set = []
    anomaly_set = []
    
    for _ in range(num_cycles):
        # 1. Standard Nominal Fibonacci Wavefront Configuration
        t = np.linspace(0, 10, 1280, dtype=np.float32)
        ch1 = np.sin(t * 60.0 * (phi**0))
        ch2 = np.sin(t * 60.0 * (phi**-1))
        ch3 = np.sin(t * 60.0 * (phi**-2))
        ch4 = np.sin(t * 60.0 * (phi**-3))
        nominal_frame = np.stack([ch1, ch2, ch3, ch4], axis=0) # Shape (4, 1280)
        nominal_set.append(nominal_frame)
        
        # 2. Adversarial Anomalous Structural Shift (Phase & Magnitude Disruption)
        # Injects heavy phase shifts simulating component degradation or noise spikes
        ch1_err = np.sin(t * 60.0 * (phi**0) + 1.5) * 2.5 
        ch2_err = np.sin(t * 60.0 * (phi**-1) - 0.8) * 0.1
        ch3_err = rng.normal(0, 2, 1280).astype(np.float32) # High entropy white noise
        ch4_err = ch4
        anomaly_frame = np.stack([ch1_err, ch2_err, ch3_err, ch4_err], axis=0)
        anomaly_set.append(anomaly_frame)
        
    return np.array(nominal_set, dtype=np.float32), np.array(anomaly_set, dtype=np.float32)


def execute_manifold_mapping_audit():
    print("[INIT] Booting Spatial Encoder and generating structural stress signals...")
    encoder = AsymmetricSpatialEncoder(latent_dim=128)
    encoder.eval()
    
    nominal_signals, anomaly_signals = generate_stress_vectors(num_cycles=50)
    
    latent_vectors_nominal = []
    latent_vectors_anomaly = []
    
    # Extract 128-dimensional hidden embeddings from the encoder layer parameters
    with torch.no_grad():
        for i in range(50):
            # Process nominal vectors
            tensor_nom = torch.from_numpy(nominal_signals[i]).unsqueeze(0) # Add batch axis
            latent_nom = encoder(tensor_nom)
            latent_vectors_nominal.append(latent_nom.cpu().numpy().flatten())
            
            # Process anomaly vectors
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
    # Sort eigenvectors by highest eigenvalue sorting markers
    sorted_idx = np.argsort(eigenvalues)[::-1]
    top_2_components = eigenvectors[:, sorted_idx[:2]]
    
    # Project vectors into the lower-dimensional manifold space
    X_projected = np.dot(X_centered, top_2_components)
    
    print("\n" + "="*70)
    print("MATHEMATICAL MANIFOLD PROJECTION RESULTS")
    print("="*70)
    print(f" -> Nominal Clusters Centroid (2D Space): {X_projected[:50].mean(axis=0)}")
    print(f" -> Anomaly Clusters Centroid (2D Space): {X_projected[50:].mean(axis=0)}")
    
    inter_cluster_distance = np.linalg.norm(X_projected[:50].mean(axis=0) - X_projected[50:].mean(axis=0))
    print(f" -> Verifiable Inter-Cluster Separation Distance: {inter_cluster_distance:.4f}")
    
    assert inter_cluster_distance > 1e-3, "Error: Latent space topology fails to separate anomalies from nominal states."
    print("[SUCCESS] Topography verification complete. Network manifold separation verified.")
    print("="*70 + "\n")


if __name__ == "__main__":
    execute_manifold_mapping_audit()
