# 📊 Advanced Analytical Research & Mathematical Proofs

This document preserves the non-linear metrics, convergence loops, and information flow calculations driving our edge tracking models.

## 🌀 1. Chaos Dynamics Reconstruction
- **Lorenz Attractor Equations:** Modeled via differential calculation loops inside `reconstruct_attractor.py`.
- **Takens Embedding Theorem:** Delay-coordinate time-series embedding utilizes parameter sets ($\tau=10, d=3$).
- **Phase-Space Trajectory Forecaster:** Localized nearest-neighbor neighborhood checks in `predict_chaos.py` map trajectory divergence variance limits.

## 🧠 2. Information Theory Firewalls
- **Shannon Entropy (H):** Quantifies discrete state uncertainty vectors inside `analyze_information_flow.py`.
- **Kullback-Leibler (KL) Divergence:** Measures empirical information drift relative to pure uniform reference points.
- **Wasserstein Manifold Jitter:** Calculates Earth Mover's Distance ($W_1$) in `track_wasserstein.py` to evaluate distribution displacement acceleration.
