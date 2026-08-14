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
