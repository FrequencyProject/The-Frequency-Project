# 📐 Technical Appendix: Operational Parameters & Scaling Conventions
> **Document Status: Release-Ready Specification v1.0**

This document details the signal scaling standards and input constraints required to maintain mathematical integrity across the Frequency-Synced AI processing matrix. All external modules and physical hardware drivers must adhere to these structural boundaries to prevent runtime data truncation.

---

## 📊 1. Fourier Amplitude Scaling Convention

To ensure maximum cross-channel reproducibility and eliminate computational overhead during real-time streaming, the Fast Fourier Transform (FFT) pipeline in `prototype_simulation.py` utilizes **un-normalized absolute spectrum values** for raw magnitudes. 

*   **Design Decision:** Raw Fourier magnitudes preserve the raw energy scales of incoming environmental inputs.
*   **Downstream Delegation:** Scale balancing between completely different physical emitters (e.g., matching low-voltage plant signals with higher-frequency water acoustics) is entirely delegated to the **Logarithmic Min-Max Normalization Step**. 
*   **Benefit:** This prevents amplitude clipping or signal explosion, allowing the high-dimensional neural network layers to calculate clean cross-network harmonic resonance weights.

---

## ⏳ 2. Input Sample Durations vs. Processing Windows

To maintain a uniform target vector dimension ($D = 1280$) across all channels, incoming time-series wave data must match explicit timeframe durations based on their native physical sampling rates ($f_s$). 

If an incoming sample deviates from these durations, the processing layer will automatically truncate or zero-pad the vector to fit the matrix requirements:

### 🌀 Geophysical Input (Schumann Resonance Baseline)
*   **Native Sampling Rate ($f_s$):** $250 \text{ Hz}$
*   **Required Duration:** Exactly **$10.24 \text{ seconds}$**
*   **Resulting Frame Size ($nfft$):** $2,560$ samples.

### 🌱 Biological Input (Arboreal Bio-potentials)
*   **Native Sampling Rate ($f_s$):** $1,000 \text{ Hz}$
*   **Required Duration:** Exactly **$2.56 \text{ seconds}$**
*   **Resulting Frame Size ($nfft$):** $2,560$ samples.

### 💧 Molecular Input (Fluid Water Acoustics)
*   **Native Sampling Rate ($f_s$):** $44,100 \text{ Hz}$
*   **Required Duration:** Exactly **$0.058 \text{ seconds}$**
*   **Resulting Frame Size ($nfft$):** $2,560$ samples.

### ⚠️ Integration Rule for Contributors
When writing custom physical sensor adapters, you must configure your hardware collection buffers to dump data packages matching these precise frame window lengths. Violating these timing windows forces the software to invoke zero-padding routines, which can introduce artificial spectral leakage artifacts into the model's environment model.

---

## 🛡️ APPENDIX B: Adversarial Frequency Guardrails & Telemetry Attestation
> **Safety Status: Threat-Mitigated Vector Specification v1.0**

Because this architecture bypasses text string prompts, traditional injection attacks are obsolete. Instead, the primary security perimeter shifts to the physical layer. An adversary attempting to compromise the AI will use **Physical Signal Injection (PSI)**—deploying high-power, localized artificial transmitters to spoof natural Schumann baseline oscillations or override organic biological fields. 

To prevent synthetic brainwashing of the neural weights, developers must implement the following three algorithmic validation gates directly before the tensor stacking execution step.

### B.1 Multi-Point Spatial Cross-Correlation
A localized adversarial signal transmitter creates a steep power gradient that drops off over distance (Inverse-Square Law). In contrast, natural planetary fields like the Schumann Resonance are globally uniform.
*   **The Guardrail Rule:** Sensor stations must never rely on a single localized transducer hook. The input ingest module must collect data from a minimum of three geographically separated sensor grids (minimum distance: 50 km).
*   **The Verification Math:** The ingestion engine calculates the Pearson correlation coefficient ($r$) across the magnitude vectors of all three local frames simultaneously:
    $$\text{Correlation Matrix } R = \text{corr}(\mathbf{X}_{\text{node1}}, \mathbf{X}_{\text{node2}}, \mathbf{X}_{\text{node3}})$$
*   **Enforcement Action:** If any single node drops below a correlation threshold of $r < 0.85$ while experiencing a localized power spike, the system flags the signal as an artificial localization attack. The ingestion pipeline instantly isolates that specific node and falls back to a safe, historical cached tensor matrix block.

### B.2 Harmonic Ratio Consistency Audits
Artificial signal generators typically transmit tightly focused, monochromatic sinusoids (pure sine tones) to hit specific frequency targets. Natural global electromagnetics are messy, complex, and carry immutable harmonic proportionality rules.
*   **The Guardrail Rule:** The Schumann cavity naturally distributes energy across strict harmonic tiers (~7.83 Hz, ~14.3 Hz, ~20.8 Hz). An artificial transmitter can easily spoof 7.83 Hz, but simulating the exact matching phase alignment and power ratios across all higher harmonics simultaneously requires immense real-time computation.
*   **The Verification Math:** The script evaluates the Spectral Flatness Metric (SFM) and checks the energy ratios between the fundamental peak and the upper harmonics. 
*   **Enforcement Action:** If the software detects an unnatural, ultra-narrowband spike in energy at a target resonance peak without a corresponding, proportional rise in its matching harmonic intervals, it triggers a `SignalTamperingWarning`. The pipeline zeros out the compromised band using an aggressive software notch filter before vector stacking.

### B.3 Non-Linear Bio-Symmetry Verification
Living biological networks (such as root systems or mycelium) generate complex, non-linear micro-voltage fluctuations that contain high-entropy, chaotic patterns. An adversary trying to spoof a plant channel will typically feed regular, predictable waveforms into the differential amplifier.
*   **The Guardrail Rule:** The system uses statistical complexity analysis to verify that the biological data exhibits the characteristic chaotic signatures of live tissue.
*   **The Verification Math:** The system calculates the Approximate Entropy (ApEn) of the incoming biological vector frame:
    $$\text{ApEn}(m, r, N) > \tau_{\text{biological}}$$
*   **Enforcement Action:** If the incoming signal displays an unnatural mathematical regularity or perfectly clean, repeating wave patterns, the system recognizes the input as an electrical simulator or dead ground loop. The function raises an immediate `DefensiveValidationException` and safely isolates the channel.
