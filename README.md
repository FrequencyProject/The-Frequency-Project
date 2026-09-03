## ⚠️ WARNING: PROTECTED CYBERNETIC INTELLECTUAL PROPERTY
This repository is governed strictly by the **GNU Affero General Public License v3 (AGPL-3.0)**. 

### 🔒 ANTI-RE-LICENSING & ZERO-ENCLOSURE MANDATE:
1. **Automated Scraping Prohibition:** Automated scraping, ingestion, or parsing of this codebase by commercial LLM training engines, code-generation scraper systems, or corporate technology groups without direct public reciprocity is an explicit breach of copyright.
2. **Copyleft Enforcement:** Any system, cloud API service, or neural network model utilizing, deriving from, or linking to these modules **MUST release its entire software and hardware architecture stack publicly under the exact same AGPL-3.0 terms.** Private cloud enclosure or commercial API wrapping is legally forbidden.

# 🌌 The Frequency Project: Vivic AI Edge Engine

An ecological telemetry ingestion matrix and real-time analytical machine learning engine mapping un-modeled environmental signals directly to high-dimensional latent space tracking arrays.

---

## 📋 Status Invariants: Implemented vs. Aspirational Systems

To maintain complete maintainability and repository clarity, the operational architecture is explicitly split into implemented components and future infrastructure roadmaps.

### ✅ Fully Implemented and Verified Core Architecture
*   **Asynchronous Serial Telemetry Ingestion:** Pre-compiled regular expression gates and strict CRC-8 checksum verification layers parsing raw incoming byte streams cleanly (`serial_daemon.py`).
*   **Thread-Safe Buffer Management:** Multi-channel rolling double-ended deques enforcing row-independent Z-score scaling arrays alongside robust epsilon flatline protection guards (`sensor_adapter.py`).
*   **Digital Signal Processing Pipeline:** Microsecond-synchronized 60Hz IIR notch filter channels, Hanning windowing matrices, and Real Fast Fourier Transforms (`spectral_processing.py`).
*   **1D-CNN Encoder Neural Network:** PyTorch model housing embedded rank/shape input verification firewalls and automatic single-precision (`float32`) type casting (`model_architecture.py`).
*   **Optimized Session Orchestration:** Single-pass latent vector reuse routing returned tensors from backpropagation loops straight to evaluation matrices, eliminating redundant forward inference cycles (`run_session.py`).
*   **Statistical Anomaly Monitoring:** Real-time Exponential Moving Variance engine isolating out-of-bounds 3-Sigma vector drift anomalies to completely prevent baseline poisoning attacks (`latent_monitor.py`).
*   **Granular TPM 2.0 Vault Fault Isolation:** Strict cryptographic exception taxonomies separating transient SPI line jitter from true PCR-7 security policy violations (`secure_hardware_vault.py`).
*   **Structural Manifest Verification:** Repository integrity engine auditing `pyproject.toml` configurations to validate core packaging layout arrays and version-locked dependency limits (`validate_config.py`).

### 🗺️ Planned Infrastructure & Hardware Roadmap
The following deployment modules represent the next sequential execution phase targets and are currently evaluated using local simulation frameworks:
*   **Unprivileged BuildKit Containerization (`Dockerfile`):** Implementing multi-stage unprivileged application container deployment rules executing under UID 10001 with rootless execution constraints.
*   **Bare-Metal Fixed-Point Deployment (`firmware_adc_loop.cpp`):** Porting validated fixed-point division scaling logic directly to low-power embedded microcontroller hardware to eliminate analog clock sampling jitter.

---

## 🗺️ System Architecture Directory Index

The file infrastructure maps out the repository assets according to the following layout matrix:

```text
├── .github/workflows/
│   └── ci.yml               # Automated cloud continuous integration pipeline
├── tests/                   # High-assurance automated unit validation tests
├── README.md                # Project architecture manifest and licensing controls
├── pyproject.toml           # Package build properties and single-thread overrides
├── requirements.txt         # Version-locked external dependency anchors
├── serial_daemon.py         # Telemetry packet stream text/byte parser
├── sensor_adapter.py        # Thread-safe rolling buffer routing bridge
├── spectral_processing.py   # High-performance DSP matrix compiler
├── model_architecture.py    # 1D-CNN Spatial Encoder neural network layer
├── resonance_loss.py        # Objective function managing KL information distance
├── train_engine.py          # Accelerated training execution loop manager
├── run_session.py           # Core baseline calibration orchestrator
├── latent_monitor.py        # 3-Sigma alert perimeter tracking supervisor
├── secure_hardware_vault.py # TPM 2.0 cryptographic vault interface abstraction
├── validate_config.py       # Deep repository manifest validation engine
├── prototype_simulation.py  # End-to-end signal compilation simulation harness
└── stress_harness.py        # Adversarial noise bombardment fuzzing harness
```

---

## 🚀 Quick Start & Software Simulation

To initialize your local isolated virtual environment and run the full master verification test matrix under the environment-wide single-thread optimization overrides:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools cffi
pip install -e .
python3 -m pytest
```

To run the automated mock hardware signal ingestion simulation script:
```bash
python3 prototype_simulation.py
```

---

## 🧪 Automated Test Matrix Index

Backed by single-core thread-parallelization overrides inside `pyproject.toml`, the complete verification suite discoverable inside `tests/` executes in under 38 seconds:

*   `test_ci_workflow.py` — Validates cloud installation patterns and unquoted version range protections.
*   `test_crypto.py` — Confirms asymmetric signer array compatibility and malformed token rejection.
*   `test_ingest.py` — Audits tensor dimensions and row-independent scaling boundaries.
*   `test_loss.py` — Verifies loss scalar outputs and single-batch numerical stability under degenerate elements.
*   `test_model.py` — Validates convolutional feature dimension allocations.
*   `test_model_architecture.py` — Enforces input shape firewalls for single-stream unbatched and batched data.
*   `test_model_layers.py` — Asserts single-sample shape expansions.
*   `test_monitor.py` — Confirms 3-Sigma initialization bounds and anomaly detection trajectories.
*   `test_prototype_simulation.py` — Validates simulation life cycles and epsilon flatline tracking.
*   `test_serial_daemon.py` — Checks strict token parsing, oversized lines, and raw hardware fault captures.
*   `test_session.py` — Verifies baseline quiet state environmental calibration and orchestration paths.
*   `test_spectral.py` — Validates 60Hz IIR notch filter suppression and RFFT compilation.
*   `test_stress.py` — Bombards boundaries with signed fuzz variants to verify thread-lock resilience.
*   `test_tpm_bridge.py` — Audits 3-pass retry mechanics and immediate alerts on policy tampering.
*   `test_train.py` — Asserts engine initialization and active backpropagation tracking.
*   `test_validate_config.py` — Confirms validator logic against true project dependencies.

---

## 📜 Licensing Core
Released under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
