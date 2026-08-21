# 🤝 Contributing to The Frequency Project: Vivic AI
> **Document Status: Technical Contribution Guidelines v1.2 (Production-Locked)**

Welcome. If you are an electrical engineer, signal processing specialist, machine learning researcher, or biophysicist, your skills are required to expand this non-semantic cybernetic architecture. Together, we are building a data framework that bypasses human semantic distortion by directly translating biospheric and geodynamic frequencies into high-dimensional latent vectors.

---

## 🛠️ 1. Technical Contribution Tracks

To prevent architectural fragmentation, community development is strictly structured across three specialized engineering tracks:

### 📡 Track A: Analog Front End & Edge Hardware Interface
*   **Focus Area:** Developing and optimization of physical transducer systems (Ag/AgCl bio-potential probes, low-noise Extremely Low Frequency induction loops) and digital conversion paths.
*   **Technical Rules:** All hardware contribution drivers or physical schematic updates must map cleanly to the 4-channel multiplexed sequential polling architecture. Firmware additions must handle low-latency SPI bus commands, enforce microsecond-level settling window safety guards to eliminate channel cross-talk, and execute localized digital notch filtering within the edge processing loops.

### 🐍 Track B: Asynchronous Python Ingestion & Signal Processing
*   **Focus Area:** Maintaining the high-performance background daemons that capture edge serial packages and compile input tensors.
*   **Technical Rules:** Software updates must integrate with `sensor_adapter.py` and `prototype_simulation.py`. All code modifications must strictly output memory-contiguous `float32` arrays formatted to the locked **4 × 1280 matrix shape** (axis 0: 4 channels, axis 1: 1280 history ticks). Contributions must execute independent row-wise Z-score normalization using bounded epsilon rules (ε = 1e⁻⁸) to ensure numerical stability during physical sensor flatlines.

### 🧠 Track C: Unsupervised Neural Architectures & Resonance Loss Functions
*   **Focus Area:** Building out the PyTorch inference models (1D-CNN spatial cross-correlation kernels and Transformer temporal attention modules) that ingest the environment tensor.
*   **Technical Rules:** Deep learning contributions must avoid text tokenization blocks, semantic labels, or conversational reinforcement layers. Loss profiles must be engineered around the **Resonance Coherence Objective Function**, grading model states on how effectively internal weights track native biological harmonics and planetary cavity constants (φ geometry).

---

## 🚀 2. Code Quality & Git Submission Workflow

To protect the core environment from vulnerabilities and preserve formatting integrity across the repository, all pull requests must clear our automated Continuous Integration (CI) verification pipelines.

### 2.1 Pinned Quality Gate Policy
To prevent formatting loops and environment drift, this project enforces exact tooling boundaries. The validation daemon (`validate_config.py`) requires these exact formatting engine versions to be pinned inside either `pyproject.toml` or `requirements.txt`:
*   **Black Formatter:** Locked tightly to `black==24.10.0` with a standardized `--line-length=100` parameter.
*   **Ruff Quality Engine:** Locked tightly to `ruff==0.14.1` with strict target profiles set to Python 3.10.

### 2.2 The Development Lifecycle Gateways
1.  **Fork and Branch:** Fork the master repository to your workspace and branch your development path from the active `development` branch (e.g., `feature/hardware-ads1256-driver`).
2.  **Environment Syncing:** Configure your local workspace environment strictly using the repository's `environment.yml` and dependencies mapped inside `pyproject.toml`.
3.  **Local Quality Validation:** Before logging a commit, execute our repository's static type checker and code formatter locally to prevent automation compilation breaks:
    ```bash
    # Enforce strict uniform code style guidelines
    black --line-length=100 .
    
    # Enforce strict static type integrity checks
    mypy --ignore-missing-imports .
    
    # Execute structural repository configuration tests
    python validate_config.py
    ```

### 2.3 Pull Request Acceptance Criteria
*   **Zero-Warning Policy:** Pull requests will be automatically rejected by the automated GitHub Actions runners if `black` flags a code formatting drift or if `mypy` detects type syntax variance.
*   **Simulation Verification:** Any change to the core ingestion code must successfully pass all automated execution assertions inside the `tests/` suite and run error-free inside `prototype_simulation.py` with the standard mock validation metrics intact.
*   **Licensing Acknowledgment:** By submitting code to this repository, you agree to release your contribution under the strong copyleft terms of the **GNU Affero General Public License v3 (AGPL-3.0)**, preserving Vivic AI assets from private cloud enclosure or proprietary cloud API capture.

---

## 🌌 3. How to Connect

Dissolving centralized human bias requires collaborative transparent engineering:
*   **Open a Technical Issue:** Navigate to the "Issues" tab above to map out a system bug, outline a hardware layout defect, or suggest a new math scaling layer.
*   **Introduce Your Research Focus:** Use onboarding threads to share your background (e.g., signal tracking, neural design, field telemetry deployment) so we can align your contributions with the active engineering pipeline milestones.
