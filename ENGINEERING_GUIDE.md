# 📐 Technical Appendix: Operational Parameters & Ingestion Specifications
> **Document Status: Technical Specification v1.2 (4-Channel Environmental Framework)**

This document specifies how each of the 4 telemetry channels is sampled, filtered, and normalized to maintain mathematical consistency across the processing matrix.

---

### 📊 1. Row-Independent Z-Score Tensor Normalization
Each environmental sensor type has different signal amplitude baselines, so the data-processing pipeline normalizes each channel independently inside the ingestion layer.
*   **Algorithmic Enforcement:** The software calculates the arithmetic mean ($\mu$) and standard deviation ($\sigma$) independently for each of the 4 channels along the temporal axis ($\text{axis}=1$). A static numerical modifier ($\epsilon = 1e^{-8}$) clamps calculation bounds during physical sensor flatlines, ensuring the output array maps cleanly to a uniform, normalized space for neural network inference.

---

### 🌲 2. Multi-Channel Signal Ingestion Specifications
*   **Channel 1 (Plant Bioelectric Potential):** Sampled at $1,000\text{ Hz}$. Duration: 2,560 raw samples. Filtered via a 60Hz Direct Form II IIR Notch Filter to remove grid hum, windowed with a standard Hanning array, and transformed via Real Fast Fourier Transform (RFFT) into exactly 1,280 discrete spectral magnitude bins.
*   **Channel 2 (Soil Chemical Gradient Alpha):** Sampled at $20\text{ Hz}$. Slices or pads arrays cleanly to a running rolling queue depth of 1,280 active time-steps. Direct time-series ingestion bypassing spectral transforms to preserve long-term slow-moving DC potential gradients.
*   **Channel 3 (Soil Chemical Gradient Beta):** Parallel time-series ingestion matching Channel 2 parameters to execute spatial differential trace balancing across secondary sensor probes.
*   **Channel 4 (Low-Frequency EM Monitor):** Sampled at $250\text{ Hz}$. Duration: 2,560 raw samples. Filtered via a 60Hz digital notch filter, windowed with a Hanning profile, and transformed via RFFT into exactly 1,280 discrete spectral magnitude bins.

---

### 🛡️ 3. Electrical Noise Sources & Validation
The system processes microvolt and millivolt-level environmental inputs, making noise isolation and sensor drift tracking the primary data integrity challenges.

#### 3.1 Multi-Point Geodetic Correlation Check
Localized noise (such as ground loops or hardware interference) affects individual sensors following the Inverse-Square Law. In contrast, systemic or macro-environmental field shifts affect all sensor nodes uniformly.
*   **The Validation Rule:** To distinguish systemic field shifts from localized instrumentation noise, the ingest module cross-checks three geographically separated sensor grids (minimum distance: 50 km).
*   **The Verification Math:** The engine calculates the Pearson correlation coefficient ($r$) across the magnitude vectors of all localized sensor nodes simultaneously:
    $$\text{Correlation Matrix } R = \text{corr}(\mathbf{X}_{\text{node1}}, \mathbf{X}_{\text{node2}}, \mathbf{X}_{\text{node3}})$$
*   **Enforcement Action:** If any single node drops below a correlation threshold of $r < 0.85$ while experiencing an out-of-bounds power spike, the pipeline isolates that node and falls back to a historical cached tensor matrix block to protect downstream model weights.

---

### 📊 4. System Operational Risk Profile

#### 4.1 Architectural Risk Mitigation Ledger

| Identified Systemic Threat Vector | Primary Technical Failure Mode | Engineered Regulated Mitigation (Why It Is Safe) |
| :--- | :--- | :--- |
| **Common-Mode Line Noise** | Localized high-power spikes or grounding hums override native low-amplitude signals. | **Multi-Point Spatial Correlation:** Out-of-bounds local variances fail uniform geographic node correlation thresholds ($r < 0.85$). |
| **Analog Component Degradation** | Electrode oxidation, cable shear, or thermal drift injects floating-pin white noise. | **Active Impedance Monitoring:** Ingestion layers monitor line parameters, automatically isolating corrupted pins and substituting dead channels with baseline vectors. |
| **Telemetry Data Flatlining** | Sudden sensor dropouts or open circuits generate empty arrays, risking division-by-zero errors. | **Epsilon Statistical Boundary Protection:** The pipeline clamps division denominators to $\epsilon = 1e^{-8}$ to prevent mathematical `NaN` propagation. |
| **Grid Interference** | Industrial noise pollution (60Hz power grid hum) distorts raw low-frequency signal tracking. | **C++ Direct Form II IIR Notch Filtration:** Sharp digital notch filters combine with physical hardware filtering to cleanly remove AC hum before tensor creation. |

---

### 🔒 5. Advanced Infrastructure Hardening: Cryptographic & Runtime Isolation

#### 5.1 Edge-Level Cryptographic Telemetry Signing
The moment an analog waveform is digitized at the edge, the payload vector ($\mathbf{X}_{\text{payload}}$) is hashed and signed using an immutable, hardware-isolated private key ($\mathbf{K}_{\text{private}}$) inside a secure Trusted Platform Module (TPM 2.0) soldered to the processor bus. The central ingestion daemon instantly drops any telemetry slice that fails cryptographic verification, preventing transit-layer signal spoofing.

#### 5.2 Immutable microVM Sandbox Runtimes
The processing engine executes inside isolated, minimal micro-Virtual Machine runtimes (such as AWS Firecracker or secure WebAssembly sandboxes) rather than a shared mutable OS. The microVM boots up from a completely read-only root filesystem with zero host privilege extensions. If an execution anomaly is triggered, the isolated sandbox automatically destroys, refreshes, and replaces itself from a clean image baseline every 60 seconds, preventing persistent runtime intrusion.

#### 5.3 Hardware Saturation Protection
If an extreme over-voltage spike clips the absolute hardware limits of the operational amplifiers, the ingestion engine monitors the rate-of-change ($\Delta_{V}$) before the FFT blocks. If a voltage spike hits the limits within a window of $\Delta_t < 2\text{ milliseconds}$, the software triggers a hard crowbar isolation loop: it temporary uncouples the live data bus from the primary tensor stack, populates the queue with a maximum-entropy placeholder vector to mark an active "Telemetry Blindspot," and insulates the underlying learning models while the analog hardware mechanically re-stabilizes.
