#!/usr/bin/env python3
"""Phase 6: Neural Information Flow, Latent Entropy, and KL Divergence Auditor.

Quantifies Shannon Entropy, Uniform Reference Distributions, and raw Kullback-Leibler
(KL) Information Divergence profiles inside the 128-dimensional latent manifold vectors.
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

    # Generate continuous block of deterministic chaos
    raw_chaos_signal = simulate_lorenz_chaos(num_steps=80000, dt=0.01)
    chaotic_manifold = build_takens_embedding(raw_chaos_signal, delay=10, dimension=3)

    for idx in range(num_cycles):
        # 1. Standard Nominal Fibonacci Wavefront Configuration (Hardened tracking time window)
        time_offset = idx * 10.0
        t = np.linspace(time_offset, time_offset + 10.0, 1280, dtype=np.float32)
        # Apply micro-phase variance using the initialized random number generator
        phase_jitter = rng.uniform(-0.02, 0.02)
        t += phase_jitter
        ch1 = np.sin(t * 60.0 * (phi**0))
        ch2 = np.sin(t * 60.0 * (phi**-1))
        ch3 = np.sin(t * 60.0 * (phi**-2))
        ch4 = np.sin(t * 60.0 * (phi**-3))
        nominal_frame = np.stack([ch1, ch2, ch3, ch4], axis=0)
        nominal_set.append(nominal_frame)

        # 2. Route Chaotic Lorenz Attractor Slices
        start_slice = idx * 1280
        end_slice = start_slice + 1280

        ch1_chaos = chaotic_manifold[start_slice:end_slice, 0]
        ch2_chaos = chaotic_manifold[start_slice:end_slice, 1]
        ch3_chaos = chaotic_manifold[start_slice:end_slice, 2]
        ch4_chaos = np.zeros(1280, dtype=np.float32)

        ch1_chaos = (ch1_chaos - ch1_chaos.mean()) / (ch1_chaos.std() + 1e-8)
        ch2_chaos = (ch2_chaos - ch2_chaos.mean()) / (ch2_chaos.std() + 1e-8)
        ch3_chaos = (ch3_chaos - ch3_chaos.mean()) / (ch3_chaos.std() + 1e-8)

        chaotic_frame = np.stack([ch1_chaos, ch2_chaos, ch3_chaos, ch4_chaos], axis=0)
        anomaly_set.append(chaotic_frame)

    return np.array(nominal_set, dtype=np.float32), np.array(anomaly_set, dtype=np.float32)


def calculate_shannon_entropy(vectors: np.ndarray, num_bins: int = 10) -> float:
    """Calculates the discrete Shannon Entropy (H) across an ensemble of latent embeddings."""
    flat_data = vectors.flatten()
    counts, _ = np.histogram(flat_data, bins=num_bins)
    probabilities = counts / np.sum(counts)
    probabilities = probabilities[probabilities > 0]
    shannon_h = -np.sum(probabilities * np.log2(probabilities))
    return float(shannon_h)


def calculate_kl_divergence_vs_uniform(vectors: np.ndarray, num_bins: int = 10) -> float:
    """Calculates the raw Kullback-Leibler (KL) Divergence against a perfect Uniform reference."""
    flat_data = vectors.flatten()

    # Generate empirical distribution P
    counts, _ = np.histogram(flat_data, bins=num_bins)
    p_empirical = counts / np.sum(counts)

    # Generate target reference distribution Q (Uniform distribution across identical bin count)
    q_reference = np.ones(num_bins, dtype=np.float32) / num_bins

    kl_divergence = 0.0
    epsilon = 1e-12  # Protect against logarithmic zero bounds

    for i in range(num_bins):
        if p_empirical[i] > 0:
            # D_KL = sum(P(i) * log2(P(i) / Q(i)))
            kl_divergence += p_empirical[i] * np.log2(p_empirical[i] / (q_reference[i] + epsilon))

    return float(kl_divergence)


def execute_information_audit():
    print("[INIT] Loading Spatial Encoder and preparing relative entropy flow channels...")
    encoder = AsymmetricSpatialEncoder(latent_dim=128)
    encoder.eval()

    nominal_signals, chaotic_signals = generate_chaotic_stress_vectors(num_cycles=50)

    latent_nom_pool = []
    latent_ch_pool = []

    with torch.no_grad():
        for i in range(50):
            tensor_nom = torch.from_numpy(nominal_signals[i]).unsqueeze(0)
            latent_nom = encoder(tensor_nom).cpu().numpy().flatten()
            latent_nom_pool.append(latent_nom)

            tensor_ch = torch.from_numpy(chaotic_signals[i]).unsqueeze(0)
            latent_ch = encoder(tensor_ch).cpu().numpy().flatten()
            latent_ch_pool.append(latent_ch)

    X_nom = np.array(latent_nom_pool)
    X_chaos = np.array(latent_ch_pool)

    entropy_nominal = calculate_shannon_entropy(X_nom)
    entropy_chaos = calculate_shannon_entropy(X_chaos)

    # Execute KL Divergence audits vs Uniform State target
    kl_nominal = calculate_kl_divergence_vs_uniform(X_nom)
    kl_chaos = calculate_kl_divergence_vs_uniform(X_chaos)

    max_theoretical = np.log2(10)

    print("\n" + "="*70)
    print("NEURAL INFORMATION INFUSION LOGS (ENTROPY & KL)")
    print("="*70)
    print(f" -> Nominal Latent Shannon Entropy (H)      : {entropy_nominal:.4f} bits")
    print(f" -> Chaotic Latent Shannon Entropy (H)      : {entropy_chaos:.4f} bits")
    print(f" -> Maximum Theoretical Target Limit         : {max_theoretical:.4f} bits")
    print(f" -> Nominal KL Divergence vs. Uniform State : {kl_nominal:.4f} bits")
    print(f" -> Chaotic KL Divergence vs. Uniform State : {kl_chaos:.4f} bits")

    print("\nOperational Assurance Assertions:")
    assert kl_nominal < 1.0, "Error: Severe information divergence detected. Manifold distribution is highly uneven."
    print(" -> [PASSED] Nominal manifold tracks safely close to uniform information spread.")

    assert kl_chaos > kl_nominal, "Notice: Chaotic input failed to alter structural divergence vectors."
    print(" -> [PASSED] Relative entropy scale correctly maps non-linear state compression.")
    print("="*70 + "\n")


if __name__ == "__main__":
    execute_information_audit()
