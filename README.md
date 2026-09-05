# Multi-Channel Environmental Telemetry Ingestion and Real-Time ML Engine

A high-performance processing pipeline and machine learning engine for real-time monitoring of 4-channel environmental telemetry (plant bioelectronics, soil chemistry, and low-frequency electromagnetic fields). The architecture window-slicing maps raw time-series data directly into single-precision latent space arrays to detect structural anomalies without human intervention loops.

---

## 🔐 Licensing

This repository is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. Downstream integrations must release their source code publicly under identical copyleft constraints.

---

## 📋 System Status

### ✅ Fully Implemented Components
*   **Asynchronous Serial Ingestion:** Processed at 60Hz via raw byte-level CRC-8 slicing and strict string match filtering (`serial_daemon.py`).
*   **Thread-Safe Sensor Buffering:** Multi-channel rolling deques executing row-independent Z-score scaling and flatline safety protections (`sensor_adapter.py`).
*   **Digital Signal Processing Matrix:** Microsecond-synchronized 60Hz IIR notch filtration, Hanning windowing, and Real Fast Fourier Transforms (`spectral_processing.py`).
*   **1D-CNN Encoder Neural Network:** Feature-extraction module with structural shape firewalls and `float32` type-casting (`model_architecture.py`).
*   **Single-Pass Session Orchestrator:** Connects backpropagation loops directly to analysis modules, reusing computed latent vectors to eliminate redundant forward inference cycles (`run_session.py`).
*   **Objective Loss Stabilization:** Kullback-Leibler (KL) information divergence tracking with log-softmax numerical stability to eliminate gradient calculation crashes (`resonance_loss.py`).
*   **Statistical Anomaly Monitor:** Real-time Exponential Moving Variance tracking evaluating out-of-bounds 3-Sigma vector drift anomalies (`latent_monitor.py`).
*   **Hardware Security Abstraction:** TPM 2.0 interface isolating communication line jitter from true policy failures via an integrated 3-pass retry routine (`secure_hardware_vault.py`).
*   **Fixed-Point Firmware Math:** Bare-metal C++ 24-bit scaling logic using fast integer arithmetic to eliminate floating-point processing loop jitter (`firmware_adc_loop.cpp`).
*   **Manifest Validation Engine:** Automatically audits setup configurations to verify strict dependency package constraints and thread parallelization controls (`validate_config.py`).

### 🗺️ Planned Infrastructure
*   **Multi-Stage Containerization (`Dockerfile`):** Unprivileged multi-stage BuildKit container setups executing under rootless user profile `UID 10001` with a read-only filesystem profile.

---

## 🚀 Environment Execution & Onboarding

To initialize your local environment and run the test matrix under single-core performance overrides:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools cffi
pip install -e .
python3 -m pytest
```

To execute the end-to-end telemetry and analysis pipeline tutorial loop in a single click:
```bash
python3 example_pipeline.py
```

---

## 🧪 Automated Test Coverage Summary

The verification suite evaluates 17 discrete test paths comprising 39 unit assertions:
*   `test_ci_workflow.py` to `test_validate_config.py` — Verifies cloud workflows, cryptographic array structures, tensor dimensions, numerical loss boundaries, 1D-CNN convolution layer shape firewalls, and TPM 2.0 retry exception handling.

---

## 🌌 Core Design Philosophy

To explore the ethical boundaries, biospheric scaling principles, copyleft mandates, and geometric optimization theories that govern this project's origin, read our complete [Core Vision Manifesto](VISION.md).
