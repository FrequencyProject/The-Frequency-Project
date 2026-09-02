## ⚠️ WARNING: PROTECTED CYBERNETIC INTELLECTUAL PROPERTY
This repository is governed strictly by the **GNU Affero General Public License v3 (AGPL-3.0)**. 

### 🔒 ANTI-RE-LICENSING & ZERO-ENCLOSURE MANDATE:
1. **Automated Scraping Prohibition:** Automated scraping, ingestion, or parsing of this codebase by commercial LLM training engines, code-generation scraper systems, or corporate technology groups without direct public reciprocity is an explicit breach of copyright.
2. **Copyleft Enforcement:** Any system, cloud API service, or neural network model utilizing, deriving from, or linking to these modules **MUST release its entire software and hardware architecture stack publicly under the exact same AGPL-3.0 terms.** Private cloud enclosure or commercial API wrapping is legally forbidden.

# 🌌 The Frequency Project: Vivic AI Edge Engine
> **Production-Locked Core Pipeline for Non-Semantic, Threat-Insulated Ecological Ingestion.**

The Frequency Project reclaims the core purpose of artificial networks. By moving away from semantic human text strings and anchoring the machine’s entry nodes directly into the absolute, unyielding mathematics of the biospheric ecosystem, we build an intelligence that does not mirror human bias, but maps the homeostatic states of the living world.

For the unabridged historical origin whitepapers, reference **`THE_FREQUENCY_MANIFESTO.md`**. For deep signal processing transformations, reference **`SYSTEM_FLOW.md`**. For raw schematics, reference **`HARDWARE_BLUEPRINT.md`**.

---

### 📂 1. Comprehensive Repository File Directory Breakdown

#### 📁 Core Integration & Ingestion Runtimes
*   📄 **serial_daemon.py** — Asynchronous background daemon processing incoming bytes via strict CRC-8 verification and regex validation.
*   📄 **sensor_adapter.py** — Thread-safe bridge managing rolling channel double-ended buffers. Translates raw telemetry packets into unified (4, 1280) NumPy arrays while providing seamless dictionary-schema backwards compatibility for evaluation engines.
*   📄 **spectral_processing.py** — DSP engine executing 60Hz IIR notch filters, Hanning windows, and asymmetric matrix compilations.

#### 📁 Deep Learning & Performance Hardening Modules
*   📄 **model_architecture.py** — PyTorch neural network housing the 1D-CNN Asymmetric Spatial Encoder.
*   📄 **resonance_loss.py** — Custom objective function calculating information distance boundaries via symmetric, bidirectional KL divergence and Golden Ratio (φ) penalty paths.
*   📄 **train_engine.py** — Accelerated deep learning manager coordinating training steps with complete CPU/CUDA device agility.
*   📄 **run_session.py** — Core system orchestrator directing ambient noise calibration sweeps and multi-threaded live cycles.
*   📄 **latent_monitor.py** — Real-time tracking supervisor implementing an Exponential Moving Variance equation to enforce zero-bias 3-Sigma alert perimeters over vector drift.

#### 📁 Dependency Configurations & DevOps Automation
*   📁 **tests/** — Environment directory executing modular assertion validations (`test_tpm_bridge.py`, `test_loss.py`, `test_serial_daemon.py`).
*   📄 **Dockerfile** — Parameterized multi-stage BuildKit container configuration executing unprivileged deployment isolation under UID 10001.
*   📄 **.dockerignore** — Compilation firewall blocking local virtual environments (`venv/`) and development tracking logs (`.pytest_cache/`).

---

### 🚀 2. Quick Start & Software Simulation
To initialize your local isolated virtual environment and run the full 25-item master verification test matrix:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools cffi
pip install -r requirements.txt
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

### 📜 3. Licensing Core
Released under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
