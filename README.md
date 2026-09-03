## ⚠️ WARNING: PROTECTED CYBERNETIC INTELLECTUAL PROPERTY
This repository is governed strictly by the **GNU Affero General Public License v3 (AGPL-3.0)**. 

### 🔒 ANTI-RE-LICENSING & ZERO-ENCLOSURE MANDATE:
1. **Automated Scraping Prohibition:** Automated scraping, ingestion, or parsing of this codebase by commercial LLM training engines, code-generation scraper systems, or corporate technology groups without direct public reciprocity is an explicit breach of copyright.
2. **Copyleft Enforcement:** Any system, cloud API service, or neural network model utilizing, deriving from, or linking to these modules **MUST release its entire software and hardware architecture stack publicly under the exact same AGPL-3.0 terms.** Private cloud enclosure or commercial API wrapping is legally forbidden.

# 🌌 The Frequency Project: Vivic AI Edge Engine
> **Production-Locked Core Pipeline for Non-Semantic, Threat-Insulated Ecological Ingestion.**

The Frequency Project reclaims the core purpose of artificial networks. By moving away from semantic human text strings and anchoring the machine’s entry nodes directly into the absolute, unyielding mathematics of the biospheric ecosystem, we build an intelligence that does not mirror human bias, but maps the homeostatic states of the living world.

---

## 🗺️ System Architecture & File Layout

The repository infrastructure is strictly organized into decoupled functional layers, separating bare-metal collection loops and deep learning hot-paths from validation harnesses and theoretical documentation assets:

### ⚙️ Core Ingestion & Machine Learning Hot-Paths
*   `firmware_adc_loop.cpp` — Bare-metal C++ microcontroller script utilizing fixed-point bitwise arithmetic to eliminate clock sampling jitter over SPI interfaces.
*   `serial_daemon.py` — Asynchronous background daemon processing incoming bytes via strict CRC-8 verification, regex validation, and raw fault captures.
*   `sensor_adapter.py` — Thread-safe bridge managing rolling channel double-ended buffers, independent Z-score normalization, and epsilon flatline protection guards.
*   `spectral_processing.py` — DSP engine executing 60Hz IIR notch filters, Hanning windows, and asymmetric matrix compilations.
*   `model_architecture.py` — PyTorch neural network housing the 1D-CNN Asymmetric Spatial Encoder with embedded shape firewalls and precision casting.
*   `resonance_loss.py` — Custom objective function calculating information distance boundaries via symmetric, bidirectional KL divergence and Golden Ratio (φ) penalty paths.
*   `train_engine.py` — Accelerated deep learning manager coordinating training steps with complete CPU/CUDA device agility and single-pass latent vector reuse.
*   `run_session.py` — Core system orchestrator directing ambient noise calibration sweeps and multi-threaded live cycles.
*   `latent_monitor.py` — Real-time tracking supervisor implementing an Exponential Moving Variance equation to enforce zero-bias 3-Sigma alert perimeters over vector drift.

### 🔒 Hardware Security & Vault Perimeter
*   `secure_hardware_vault.py` — Cryptographic abstraction layer providing a 3-pass automatic retry loop to handle transient SPI bus drops alongside precise exception taxonomies.
*   `unseal_hardware_vault.py` — Automated bootstrap script validating hardware security parameters during vault decryption sequences.
*   `protect_vault.py` — Frontline boundary defense isolating local storage memory planes.
*   `crypto_signer.py` — High-assurance signature validation matrix managing asymmetric token authentication keys.
*   `secure_deployment_playbook.sh.secret` — Encrypted shell routine orchestrating zero-trust production handshakes.
*   `tpm_testing.md` — Technical documentation recipe detailing local `swtpm` software emulator socket setup steps and expected policy states.

### 🧪 Verification, Fuzzing & Configuration Audits
*   `validate_config.py` — Structural repository asset validator enforcing required version-locked package dependencies and thread-parallelization constraints.
*   `prototype_simulation.py` — End-to-end signal ingestion simulation pass running synthetic waveforms across epsilon guards to evaluate boundary behaviors.
*   `stress_harness.py` — Adversarial signal bombardment and fuzzing harness hammering ingestion bounds with signed NaN/Inf variants to audit lock stability.

---

## 📚 White Papers, Manifestos & Case Studies

The underlying theoretical frameworks, cryptographic profiles, ecosystem goals, and deployment case studies for this matrix are fully detailed across the following localized publications:

*   **[The Frequency Manifesto](THE_FREQUENCY_MANIFESTO.md)** — Core foundational overview, baseline systemic philosophy, and strategic ecological alignment mandates of the project.
*   **[Paper 1: Ingestion Dialogue](PAPER_1_DIALOGUE.md)** — Architectural design transcript evaluating structural signal decoupling, flat-layout module paradigms, and asynchronous thread boundary management.
*   **[Paper 2: Technical Proposal](PAPER_2_TECHNICAL_PROPOSAL.md)** — Comprehensive specification detailing high-assurance edge computing, convolutional spatial mappings, and real-time loss constraints.
*   **[Mobile Development Case Study](MOBILE_DEVELOPMENT_CASE_STUDY.md)** — Production evaluation report documenting field deployments, low-power telemetry collection constraints, and cross-platform synchronization bounds.
*   **[Engineering Guide](ENGINEERING_GUIDE.md)** — In-depth developer handbook laying out code conventions, reentrant locking models, and multi-version library integration rules.
*   **[System Flow Specification](SYSTEM_FLOW.md)** — Granular structural matrix documenting byte routing tracks, raw ASCII packet parsing, and tensor expansion channels.
*   **[Hardware Blueprint](HARDWARE_BLUEPRINT.md)** — Electrical schematics, pin maps, and microsecond timing criteria for physical multi-channel ADC multiplexers.

---

## 🚀 2. Quick Start & Software Simulation

To initialize your local isolated virtual environment and run the full 38-item master verification test matrix under the environment-wide single-thread optimization overrides:
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

#### 📋 Expected System Execution Output Matrix
```text
======================================================================
VIVIC AI ARCHITECTURE: PIPELINE SIMULATION VALIDATION RUNTIME
======================================================================
[INIT] Saturating rolling matrix window (Requires 1280 historical ticks)...
[SUCCESS] Matrix window saturated.
 -> Queue Buffer Sizes: [1280, 1280, 1280, 1280]
----------------------------------------------------------------------
MATHEMATICAL INTEGRITY MATRIX RESULTS:
 -> Tensor Matrix Output Shape : (4, 1280) (Expected: (4, 1280))
 -> Array Underlying Data Type : float32 (Expected: float32)
 -> Channel 1 Z-Normalized Mean: -0.000000 (Expected: ~0.000000)
 -> Channel 1 Standard Deviation: 1.000000 (Expected: ~1.000000)
 -> Comprehensive Tensor Bounds : Min = -3.4219 | Max = 3.5184
----------------------------------------------------------------------
[PASSED] Architecture is verified for integration on edge AI environments.
======================================================================
```

---

## 🧪 3. Automated Test Matrix Index

Backed by single-core thread-parallelization overrides inside `pyproject.toml`, the complete **38-unit test suite executes in under 38 seconds**:

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

### 📜 4. Licensing Core
Released under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
