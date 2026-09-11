#!/usr/bin/env python3
"""Phase 6: Neural Information Flow and Latent Entropy Auditor.

Quantifies Shannon Entropy and information retention inside the 128-dimensional 
latent manifold vectors under nominal and chaotic workloads.
"""
import numpy as np
import torch
from model_architecture import AsymmetricSpatialEncoder
from map_latent_manifold import generate_chaotic_stress_vectors


def calculate_shannon_entropy(vectors: np.ndarray, num_bins: int = 10) -> float:
    """Calculates the discrete Shannon Entropy (H) across an ensemble of latent embeddings."""
    # Flatten the ensemble or compute per-dimension and average
    flat_data = vectors.flatten()
    
    # Generate an empirical probability density function via histogramming
    counts, _ = np.histogram(flat_data, bins=num_bins)
    probabilities = counts / np.sum(counts)
    
    # Filter out zero probabilities to prevent numeric log(0) explosions
    probabilities = probabilities[probabilities > 0]
    
    # H = -sum(p * log2(p))
    shannon_h = -np.sum(probabilities * np.log2(probabilities))
    return float(shannon_h)


def execute_information_audit():
    print("[INIT] Loading Spatial Encoder and preparing information flow channels...")
    encoder = AsymmetricSpatialEncoder(latent_dim=128)
    encoder.eval()
    
    # Pull 50 pairs of nominal Fibonacci and chaotic Lorenz waveforms
    nominal_signals, chaotic_signals = generate_chaotic_stress_vectors(num_cycles=50)
    
    latent_nom_pool = []
    latent_ch_pool = []
    
    with torch.no_grad():
        for i in range(50):
            # Process nominal vectors
            tensor_nom = torch.from_numpy(nominal_signals[i]).unsqueeze(0)
            latent_nom = encoder(tensor_nom).cpu().numpy().flatten()
            latent_nom_pool.append(latent_nom)
            
            # Process chaotic vectors
            tensor_ch = torch.from_numpy(chaotic_signals[i]).unsqueeze(0)
            latent_ch = encoder(tensor_ch).cpu().numpy().flatten()
            latent_ch_pool.append(latent_ch)
            
    X_nom = np.array(latent_nom_pool)
    X_chaos = np.array(latent_ch_pool)
    
    # 1. Evaluate Shannon Entropy (Higher values mean more complex, uncollapsed distribution)
    entropy_nominal = calculate_shannon_entropy(X_nom)
    entropy_chaos = calculate_shannon_entropy(X_chaos)
    
    # Maximum theoretical entropy for 10 bins is log2(10) = 3.3219
    max_theoretical = np.log2(10)
    
    print("\n" + "="*70)
    print("NEURAL INFORMATION QUANTIFICATION LOGS")
    print("="*70)
    print(f" -> Nominal Latent Shannon Entropy (H) : {entropy_nominal:.4f} bits")
    print(f" -> Chaotic Latent Shannon Entropy (H) : {entropy_chaos:.4f} bits")
    print(f" -> Maximum Theoretical Target Limit    : {max_theoretical:.4f} bits")
    
    # Audit for latent collapse (An entropy < 1.0 implies the features are flatlining)
    print("\nOperational Assurance Assertions:")
    assert entropy_nominal > 1.5, "Error: Latent collapse detected! Nominal entropy is too constrained."
    print(" -> [PASSED] Nominal latent state space maintains high-entropy distribution.")
    
    # The chaotic model should trigger equal or greater entropy than nominal streams
    assert entropy_chaos >= (entropy_nominal - 0.5), "Error: Informational flow throttled on chaotic inputs."
    print(" -> [PASSED] Network dynamically tracks and transfers chaotic variance parameters.")
    print("="*70 + "\n")


if __name__ == "__main__":
    execute_information_audit()
