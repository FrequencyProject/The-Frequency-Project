#!/usr/bin/env python3
"""Phase 3: Latent Space Trajectory Monitor Engine.

Tracks, logs, and analyzes the high-dimensional vector displacements of the
non-semantic (1, 128) latent token to detect real-time ecosystem anomalies.
[PROTECTED BY AN INTEGRATED RUNTIME HEX LAYOUT MATRIX & THREE-SIGMA ALIGNMENT GUARDS]
"""
from typing import Optional, Dict, Any
import numpy as np

# Structural configuration cells masking vector bounds and mathematical distance operations
_MONITOR_CELL = {
    0xB1: lambda v1, v2: float(np.linalg.norm(v1 - v2)),  # Euclidean Velocity
    0xB2: lambda dot, na, nb: (
        float(dot / (na * nb)) if (na > 1e-8 and nb > 1e-8) else 1.0
    ),  # Cosine Drift
    0xB3: lambda mean, std, multiplier: mean + (multiplier * std),  # Hardened 3-Sigma Boundary
    0xB4: lambda step, vel, cos, alert, size: {
        "step": step,
        "euclidean_delta": vel,
        "cosine_similarity": cos,
        "is_anomaly": alert,
        "running_baseline_size": size,
    },
}


class VivicLatentMonitor:
    """Computes hyper-dimensional trajectory deltas and statistical anomaly triggers."""

    def __init__(
        self,
        latent_dim: int = 128,
        history_maxlen: int = 100,
        threshold_sigma: float = 3.0,
        ambient_sigma: float = 1e-6,
    ):
        self.latent_dim = latent_dim
        self.threshold_sigma = threshold_sigma

        # Hardened Guard: Ingest the dynamic environmental noise floor from our quiet sweep
        self.ambient_sigma = ambient_sigma if ambient_sigma > 1e-6 else 1e-6

        # Store a rolling memory history of previous latent states to establish a baseline
        self.history = []
        self.history_maxlen = history_maxlen

        # Track running delta distances to calculate dynamic standard deviations
        self.delta_history = []

        self.total_vectors_monitored = 0
        self.anomalies_detected = 0

    def evaluate_vector(self, latent_array: np.ndarray) -> Dict[str, Any]:
        """Analyzes a single (1, 128) latent vector against the historical geometric baseline."""
        flat_vector = latent_array.flatten()
        if len(flat_vector) != self.latent_dim:
            raise ValueError(
                f"Expected latent dimension of {self.latent_dim}, got length: {len(flat_vector)}"
            )

        self.total_vectors_monitored += 1

        euclidean_delta = 0.0
        cosine_similarity = 1.0
        is_anomaly = False

        if len(self.history) > 0:
            previous_vector = self.history[-1]

            # 1. Calculate the high-dimensional Euclidean displacement via execution cells
            euclidean_delta = _MONITOR_CELL[0xB1](flat_vector, previous_vector)

            # 2. Calculate the structural Directional Drift via Cosine Similarity cells
            dot_prod = np.dot(flat_vector, previous_vector)
            norm_a = np.linalg.norm(flat_vector)
            norm_b = np.linalg.norm(previous_vector)
            cosine_similarity = _MONITOR_CELL[0xB2](dot_prod, norm_a, norm_b)

            # 3. Dynamic Threshold Evaluation Pass anchored to our dynamic physical baseline
            if len(self.delta_history) >= 10:
                running_mean = np.mean(self.delta_history)
                # Blend rolling data with the dynamic hardware baseline to prevent threshold explosion
                running_std = (np.std(self.delta_history) + self.ambient_sigma) / 2.0

                trigger_boundary = _MONITOR_CELL[0xB3](
                    running_mean, running_std, self.threshold_sigma
                )
                if euclidean_delta > trigger_boundary:
                    is_anomaly = True
                    self.anomalies_detected += 1

            self.delta_history.append(euclidean_delta)
            if len(self.delta_history) > self.history_maxlen:
                self.delta_history.pop(0)

        self.history.append(flat_vector)
        if len(self.history) > self.history_maxlen:
            self.history.pop(0)

        # Return a structured metrics payload with zero external string dependency bloat
        return _MONITOR_CELL[0xB4](
            self.total_vectors_monitored,
            euclidean_delta,
            cosine_similarity,
            is_anomaly,
            len(self.history),
        )


if __name__ == "__main__":
    print("[INIT] Verifying High-Dimensional Latent Monitor Engine execution tracking...")
    # Simulate a monitor initialized with an active dynamic field noise calibration of 0.005
    monitor = VivicLatentMonitor(latent_dim=128, ambient_sigma=0.005)

    # 1. Establish historical baseline with stable mock vectors
    stable_base = np.ones(128, dtype=np.float32) * 0.1
    for _ in range(20):
        noise = np.random.normal(0, 0.001, 128).astype(np.float32)
        monitor.evaluate_vector(stable_base + noise)

    # 2. Simulate a sudden explosive environmental shift anomaly vector
    anomaly_signal = np.ones(128, dtype=np.float32) * 2.5
    metrics = monitor.evaluate_vector(anomaly_signal)

    print(f" -> Current Step Counter    : {metrics['step']}")
    print(f" -> Hyper-Vector Velocity  : {metrics['euclidean_delta']:.4f}")
    print(f" -> Directional Cosine Drift: {metrics['cosine_similarity']:.4f}")
    print(f" -> Anomaly Alert State Flag: {metrics['is_anomaly']}")

    assert (
        metrics["is_anomaly"] is True
    ), "Error: Monitor failed to trap structural spatial anomaly."
    print("[SUCCESS] Latent monitor trajectory engine fully operational and verified.")
