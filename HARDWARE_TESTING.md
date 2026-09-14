# 🎛️ Physical Hardware Verification Runbook & Phase SLAs

This document outlines the systematic 7-Phase testing protocol required to validate the multi-channel machine learning pipeline against physical bare-metal microcontrollers (ESP32-S3) running real analog telemetry inputs.

---

## 📅 1. Hardware Integration Lifecycle Timeline

```text
PHASE 1: Connectivity ➔ PHASE 2: Data Quality ➔ PHASE 3: Feature Sync ➔ PHASE 4: End-to-End Run
  (Days 1 - 2)             (Days 3 - 4)             (Day 5)                 (Days 6 - 7)
```

### 🔴 Phase 1: Basic Physical Connectivity & UART Handshakes
- **Objective:** Verify host kernel connection limits and line discovery.
- **Success Criteria:** Host successfully mounts `/dev/ttyACM0` (or target Windows `COM` line) and reads stable incoming byte sequences without timeout spikes.

### 🟡 Phase 2: Signal Data Quality & ADC Quantization Verification
- **Objective:** Confirm 24-bit integer sign-extensions and multi-precision scaling maps.
- **Success Criteria:** Telemetry arrays reflect raw voltage movements matching physical states. **Zero-variance flatlines must be absent** across active input streams.

### 🟢 Phase 3: Bit-Level CRC-8 Framing Integrity Assertions
- **Objective:** Calculate packet frame drop statistics under operational strain.
- **Success Criteria:** Running packet error tracking scores must confirm a **Frame Drop Rate < 0.1%** over a continuous 10,000-packet sweep.

---

## 🛠️ 2. How to Run the Physical Hardware Diagnostics

To sweep the validation engines out of local simulation targets and bind directly to your plugged-in USB micro-controller, modify the configuration properties as shown:

1. **Verify your physical port address** via terminal:
   ```bash
   ls /dev/ttyACM*
   ```
2. **Execute the dedicated hardware unit testing suite**:
   ```bash
   python3 -m pytest tests/test_hardware_integration.py
   ```
