#!/usr/bin/env python3
"""Phase 6: Nonlinear Chaos Dynamics & Phase-Space Reconstructor.

Simulates a 3D chaotic Lorenz Attractor system and uses Takens' Embedding Theorem
to reconstruct the multi-dimensional manifold from a single time-delayed channel.
"""
import numpy as np


def simulate_lorenz_chaos(num_steps: int = 5000, dt: float = 0.01) -> np.ndarray:
    """Solves the classical Lorenz system differential equations to generate a chaotic timeline."""
    # Standard chaotic parameters: sigma=10, rho=28, beta=8/3
    sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0

    # Initialize coordinates at an unstable non-zero state
    x = np.zeros(num_steps, dtype=np.float32)
    y = np.zeros(num_steps, dtype=np.float32)
    z = np.zeros(num_steps, dtype=np.float32)

    x[0], y[0], z[0] = 1.0, 1.0, 1.0

    # Run a first-order Euler integration loop pass across the velocity fields
    for t in range(1, num_steps):
        dx = sigma * (y[t-1] - x[t-1])
        dy = x[t-1] * (rho - z[t-1]) - y[t-1]
        dz = x[t-1] * y[t-1] - beta * z[t-1]

        x[t] = x[t-1] + (dx * dt)
        y[t] = y[t-1] + (dy * dt)
        z[t] = z[t-1] + (dz * dt)

    return x  # Return strictly a single isolated observational channel stream


def build_takens_embedding(signal: np.ndarray, delay: int, dimension: int) -> np.ndarray:
    """Reconstructs a multi-dimensional phase-space manifold using delay-coordinate slots."""
    num_samples = len(signal)
    # Bounded length calculated to prevent terminal array clipping limits
    reconstructed_length = num_samples - (dimension - 1) * delay

    if reconstructed_length <= 0:
        raise ValueError("Error: Delay and dimension limits exceed signal data bounds.")

    # Pre-allocate the coordinate trajectory matrix pool
    embedded_manifold = np.zeros((reconstructed_length, dimension), dtype=np.float32)

    for d in range(dimension):
        start_idx = d * delay
        end_idx = start_idx + reconstructed_length
        embedded_manifold[:, d] = signal[start_idx:end_idx]

    return embedded_manifold


def execute_attractor_reconstruction_audit():
    print("[INIT] Simulating 3D non-linear Lorenz chaotic velocity fields...")
    # Generate 5,000 steps of pure deterministic chaos
    raw_single_channel = simulate_lorenz_chaos(num_steps=5000, dt=0.01)

    print(" -> Instantiating Takens delay-coordinate loop (tau=10, dimension=3)...")
    # Define standard embedding constraints: delay (tau)=10 frames, dimension (d)=3 coordinates
    tau = 10
    dim = 3

    reconstructed_manifold = build_takens_embedding(raw_single_channel, delay=tau, dimension=dim)

    print("\n" + "="*70)
    print("NON-LINEAR CHAOTIC ATTRACTOR MAP")
    print("="*70)
    print(f" -> Raw Observed Signal Points : {len(raw_single_channel)}")
    print(f" -> Reconstructed Trajectory Vector Map Shape: {reconstructed_manifold.shape}")

    # Calculate topological invariant metrics (Mean coordinate variance)
    manifold_variance = np.var(reconstructed_manifold, axis=0)
    print(f" -> Reconstructed Phase-Space Variance vector : {manifold_variance}")

    # Verify the attractor has multi-dimensional volume and hasn't collapsed into a single point
    assert np.all(manifold_variance > 1.0), "Error: Phase space collapsed! Reconstruction failed."
    print("[SUCCESS] Takens' Embedding verified. Single-channel chaotic projection is complete.")
    print("="*70 + "\n")


if __name__ == "__main__":
    execute_attractor_reconstruction_audit()
