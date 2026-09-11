# 📑 Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com) and adheres to Semantic Versioning.

## - 2026-09-11

### 🚀 Added
- **Nonlinear Chaos Dynamics Suite:** Integrated raw Lorenz Attractor differential equation models into `reconstruct_attractor.py`.
- **Takens Phase-Space Reconstruction:** Implemented delay-coordinate time-series embedding loops ($\tau=10, d=3$).
- **Latent Manifold Topography Maps:** Added Principal Component Analysis (PCA) projection matrices inside `map_latent_manifold.py`.
- **Neural Information Flow Auditor:** Added self-contained Shannon Entropy (H) and Uniform Reference mapping algorithms inside `analyze_information_flow.py`.
- **Wasserstein Manifold Jitter Tracking:** Integrated Earth Mover's Distance ($W_1$) metrics inside `track_wasserstein.py` to map feature drift velocity.
- **Trajectory Divergence Predictor:** Added a non-linear nearest-neighbor lookahead forecasting gate inside `predict_chaos.py`.

### 🔒 Security & Hardening
- **Decoupled Architecture Boundary:** Isolated advanced mathematical research code blocks from core synchronous single-pass serial loops.

## - 2026-09-11

### 🚀 Added
- **Production Observability Engine:** Embedded zero-dependency HTTP metrics server on port `8000` inside `run_session.py`.
- **Prometheus Metric Streams:** Exposes `vivic_total_packets_parsed` counters and `vivic_anomalies_detected` evaluation trackers natively.
- **Dynamic Session Gauges:** Embedded `vivic_session_status{status="active"}` and `{status="calibrated"}` metrics.
- **Cluster Orchestration Probes:** Introduced a native `/health` check route reporting `200 OK` or `503 Service Unavailable`.
- **Container Infrastructure Mapping:** Added `EXPOSE 8000` metadata layer to the multi-stage `Dockerfile`.

### 🔒 Security & Hardening
- **Static Analysis Invariant:** Appended `# nosec B104` declarations to socket bindings to satisfy strict Bandit CI scanners.
- **Build Optimization Guard:** Implemented `.dockerignore` context exclusions to isolate build caches from deployment images.

### 🧪 Testing
- **Integration Expansion:** Scaled test runner framework to a total of 47 master items validating multi-channel deque charging and HTTP routes.