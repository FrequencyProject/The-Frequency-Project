#!/usr/bin/env python3
"""Phase 6: Latent Manifold Jitter and Wasserstein Drift Auditor.

Computes the 1D Earth Mover's Distance (Wasserstein-1) across rolling 128-dimensional
latent ensembles to quantify feature drift velocity under structural variations.
"""
import numpy as np
import torch
from scipy.stats import wasserstein_distance
from model_architecture import AsymmetricSpatialEncoder
from analyze_information_flow import generate_chaotic_stress_vectors


def execute_wasserstein_drift_audit():
    print("[INIT] Loading Spatial Encoder and preparing historical latent pools...")
    encoder = AsymmetricSpatialEncoder(latent_dim=128)
    encoder.eval()

    # Extract nominal and chaotic stress signal waves
    nominal_signals, chaotic_signals = generate_chaotic_stress_vectors(num_cycles=50)

    # Divide our nominal tracking points into two sequential chunks to establish a baseline drift
    nominal_pool_alpha = []
    nominal_pool_beta = []
    chaotic_pool = []

    with torch.no_grad():
        for i in range(25):
            tensor_nom_a = torch.from_numpy(nominal_signals[i]).unsqueeze(0)
            nominal_pool_alpha.append(encoder(tensor_nom_a).cpu().numpy().flatten())

            tensor_nom_b = torch.from_numpy(nominal_signals[i+25]).unsqueeze(0)
            nominal_pool_beta.append(encoder(tensor_nom_b).cpu().numpy().flatten())

        for i in range(50):
            tensor_ch = torch.from_numpy(chaotic_signals[i]).unsqueeze(0)
            chaotic_pool.append(encoder(tensor_ch).cpu().numpy().flatten())

    # Flatten pools down into 1D structural ensembles for distribution mapping
    arr_alpha = np.array(nominal_pool_alpha).flatten()
    arr_beta = np.array(nominal_pool_beta).flatten()
    arr_chaos = np.array(chaotic_pool).flatten()

    # 1. Compute baseline background drift (Nominal Alpha vs Nominal Beta)
    w1_baseline = wasserstein_distance(arr_alpha, arr_beta)

    # 2. Compute anomaly-induced manifold drift (Nominal Alpha vs Chaotic Pool)
    w1_chaos_drift = wasserstein_distance(arr_alpha, arr_chaos)

    print("\n" + "="*70)
    print("LATENT MANIFOLD WASSERSTEIN DRIFT LOGS")
    print("="*70)
    print(f" -> Baseline Background Jitter (W1 Distance) : {w1_baseline:.6f}")
    print(f" -> Chaotic Shift Velocity     (W1 Distance) : {w1_chaos_drift:.6f}")

    # Calculate relative acceleration factor
    drift_acceleration = w1_chaos_drift / (w1_baseline + 1e-8)
    print(f" -> Relative Manifold Drift Acceleration Rate: {drift_acceleration:.2f}x")

    print("\nOperational Assurance Assertions:")
    # Ensure that systemic chaos triggers significantly higher distribution displacement than normal variance
    assert w1_chaos_drift > w1_baseline, "Error: Wasserstein metric failed to capture structural feature drift!"
    print(" -> [PASSED] Earth Mover's Distance correctly identifies manifold distribution drift.")
    print("="*70 + "\n")


if __name__ == "__main__":
    execute_wasserstein_drift_audit()
