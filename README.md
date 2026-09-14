# 🌿 The Frequency Project

Real-time edge machine learning framework and high-performance processing pipeline for high-assurance environmental anomaly detection. The system ingests 4-channel analog telemetry signals at 60Hz, extracts latent manifold variations, and flags structural anomalies before systemic failures occur.

---

## 🏗️ 1. Repository Directory Architecture

The repository enforces a strict layout separating firmware collection points from production deep learning pipelines, system configuration validation layers, and analytical tracks:

```text
the-frequency-project/
├── .github/workflows/        # Continuous Integration (CI) automated pytest engine
├── documentation/            # Specialized operational architecture guides
├── tests/                    # 49-Item High-Assurance Automated Testing Matrix
├── Dockerfile                # Hardened multi-stage build image; rootless UID 10001 execution
├── CHANGELOG.md              # Keep a Changelog semantic version history layout
├── DEPLOYMENT.md             # Hardened multi-stage container orchestration manual
├── FIRMWARE_GUIDE.md         # ESP32-S3 hardware pin layouts and wiring diagrams
├── MATHEMATICAL_APPENDIX.md  # Non-linear chaos tracking proofs and equations
├── pyproject.toml            # Master package manager manifest with tight version locks
├── requirements.txt          # Version-locked baseline production dependencies
├── run_session.py            # Main orchestrator hosting embedded metrics socket server
├── sensor_adapter.py         # Multi-channel circular arrays executing Z-score scaling
└── validate_config.py        # Structural TOML parsing auditor verifying package constraints
```

---

## ⚡ 2. Quick Code Example
Condition streaming multi-rate signals into uniform spectral feature matrices using the core processing pipeline:

```python
import numpy as np
from spectral_processing import AsymmetricTensorPipeline

# Initialize the tensor pipeline for 1280-length temporal windows
pipeline = AsymmetricTensorPipeline(target_len=1280)

# Simulate 4 incoming raw analog sensor streams
ch1, ch2, ch3, ch4 = np.random.randn(4, 2000)
feature_tensor = pipeline.compile_feature_tensor(ch1, ch2, ch3, ch4)

print("Compiled feature matrix shape:", feature_tensor.shape)
```

---

## 🚀 3. Environment Execution & Onboarding

To initialize your local environment and run the test matrix under single-core performance overrides:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
python3 -m pytest
```
The verification suite evaluates **49 discrete master unit and integration tests** with a local execution velocity of **~32 seconds**.

To execute the end-to-end telemetry and analysis pipeline tutorial loop in a single click:
```bash
python3 example_pipeline.py
```

---

## 🎛️ 4. Cloud Observability & Metrics Exposition

The core orchestrator exposes an independent, zero-dependency, thread-safe background HTTP monitoring server on port **`8000`** to satisfy cloud-native health probing and performance tracking formats:

- **`/health` (Cluster Probes):** Returns `200 OK` (Healthy) or `503 Service Unavailable` to guide routing meshes.
- **`/metrics` (Prometheus Scrapers):** Streams standard, text-formatted telemetry arrays detailing packet counts, anomaly flags, and active execution loops natively.

Extended Kubernetes scraper setups and system limits are detailed inside [DEPLOYMENT.md](DEPLOYMENT.md).

---

## ⚖️ 5. Licensing & Legal Compliance

This repository is licensed under the terms of the **GNU Affero General Public License v3.0 (AGPL-3.0)**. Downstream cloud integrations or modified branches must release their complete source code publicly under identical copyleft constraints. See the root `LICENSE` file for verbatim text.
