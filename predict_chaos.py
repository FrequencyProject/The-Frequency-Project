#!/usr/bin/env python3
"""Phase 6: Non-Linear Chaos Prediction & Trajectory Divergence Auditor.

Models chaotic state transitions using localized delay-coordinate lookahead parameters,
evaluating next-step trajectory variance under deterministic Lorenz attractor systems.
"""
import numpy as np
from reconstruct_attractor import simulate_lorenz_chaos, build_takens_embedding


def predict_next_chaotic_state(embedded_manifold: np.ndarray, current_idx: int, lookahead: int = 1) -> np.ndarray:
    """Predicts the next phase-space state by finding nearest neighbors in the historical manifold."""
    # Isolate the target trajectory point vector
    current_state = embedded_manifold[current_idx]

    # Slice the history excluding points close to the current index to prevent temporal correlation bias
    history_end = max(0, current_idx - 50)
    if history_end <= 10:
        return current_state # Fallback if history pool is too shallow

    historical_points = embedded_manifold[:history_end]

    # Calculate Euclidean distance vectors across all historical manifold trajectories
    distances = np.linalg.norm(historical_points - current_state, axis=1)

    # Extract the absolute nearest neighbor matching index
    nearest_neighbor_idx = np.argmin(distances)

    # Map the neighbor's historical forward progression to extrapolate the lookahead trajectory
    predicted_state = embedded_manifold[nearest_neighbor_idx + lookahead]
    return predicted_state


def execute_chaos_prediction_audit():
    print("[INIT] Loading Lorenz chaotic datasets and tracking trajectory lookaheads...")

    # Generate 5,000 steps of deterministic chaos
    raw_signal = simulate_lorenz_chaos(num_steps=5000, dt=0.01)
    # Reconstruct the 3D phase-space manifold (tau=10, dim=3)
    manifold = build_takens_embedding(raw_signal, delay=10, dimension=3)

    test_idx = 4000
    lookahead_steps = 5

    # Capture the actual future phase-space target vector
    actual_future_state = manifold[test_idx + lookahead_steps]

    # Compute the non-linear lookahead prediction vector
    predicted_future_state = predict_next_chaotic_state(manifold, test_idx, lookahead=lookahead_steps)

    # Compute the tracking error vector and absolute divergence variance
    prediction_error = np.linalg.norm(actual_future_state - predicted_future_state)

    # Establish a baseline reference by comparing against a native flatline/no-change model error
    naive_error = np.linalg.norm(actual_future_state - manifold[test_idx])

    print("\n" + "="*70)
    print("NON-LINEAR CHAOTIC TRAJECTORY PREDICTION LOGS")
    print("="*70)
    print(f" -> Actual Future State Vector (3D Map) : {actual_future_state}")
    print(f" -> Predicted Future State Vector (3D)  : {predicted_future_state}")

    print(f"\n -> Localized Extrapolated Prediction Error : {prediction_error:.6f}")
    print(f" -> Naive Persistence Baseline Model Error : {naive_error:.6f}")

    print("\nOperational Assurance Assertions:")
    # Confirm that local phase-space neighborhood projections outperform a static persistence model
    assert prediction_error < naive_error, "Error: Predictive lookahead layer failed to track local chaos dynamics!"
    print(" -> [PASSED] Non-linear lookahead tracking successfully minimizes local trajectory divergence.")
    print("="*70 + "\n")


if __name__ == "__main__":
    execute_chaos_prediction_audit()
