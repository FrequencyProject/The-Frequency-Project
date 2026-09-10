# 🔧 The Frequency Project: Bare-Metal Hardware Triage Runbook

This document details the diagnostic steps, warning symptoms, and corrective workflows required to troubleshoot physical hardware integrations when deploying the telemetry engine onto live edge equipment.

---

## ⚡ 1. Physical Bus Line Ringing & Data Corruption
### 🔍 Symptoms
- High rate of logs displaying: `[WARNING] Byte-level CRC verification mismatch. Dropping frame.`
- Telemetry values show rapid, unrealistic value spikes or sporadic text truncations.
### 🛠️ Technical Root Cause
High-speed SPI communication (4MHz) across long, unshielded jumper wires introduces parasitic capacitance and signal line reflection (ringing), causing bits to flip mid-transmission before the CRC-8 byte is calculated.
### 🩹 Corrective Action Patch
1. **Shorten Interconnects:** Ensure SPI bus cables between the microcontroller and the ADC chip are under **10cm (4 inches)**.
2. **Add Guard Trace Delay:** If noise persists, increase the settling guard time inside `firmware_adc_loop.cpp` slightly from 5 to 10 microseconds:
   ```cpp
   int32_t read_adc_channel(uint8_cmd) {
       SPI.transfer(channel_cmd);
       delayMicroseconds(10); // Elevated guard trace settling time
   ```

---

## 🎛️ 2. Buffer Starvation Fallbacks
### 🔍 Symptoms
- Orchestrator log prints: `{"event": "BUFFER_STARVATION", "level": "WARNING", "message": "Cycle X/Y buffer starvation fallback triggered. Waiting for data..."}`
- Optimization iterations stall or drop below the target 60Hz threshold.
### 🛠️ Technical Root Cause
The downstream Python processing engine is consuming feature tensors faster than the background `HardwareSerialDaemon` thread can read, strip, and parse raw text frames from the system’s serial buffer.
### 🩹 Corrective Action Patch
1. **Verify Serial Port Availability:** Ensure no other application (like the Arduino Serial Monitor or a rogue python process) has a lock on the target port (`COM3` or `/dev/ttyUSB0`).
2. **Tune Processing Delays:** Confirm that your `run_session.py` processing loop speed stays matched to the physical input flow by checking that your single-thread configuration constraints are fully active in your environment variables.

---

## 🔒 3. Platform Configuration Register (PCR-7) Session Breaches
### 🔍 Symptoms
- Session crashes instantly on launch with an explicit: `TPMSecurityBreachError: TPM Security Breach: PCR-7 verification failed or session compromised.`
- Host logs register a critical exit code mapping directly to value `0x9A`.
### 🛠️ Technical Root Cause
The internal state configuration of the machine has shifted out of sequence. Firmware modifications, boot order adjustments, or unauthorized system updates alter the PCR hashes, causing an immediate mismatch during the security unseal phase.
### 🩹 Corrective Action Patch
1. **Bypass with Local Emulator:** For offline development or pre-hardware isolation testing, switch your instantiation profile back to the software socket layer by setting `tcti_profile = "none"` or starting up your background `swtpm` mock proxy daemon.
2. **Re-seal the Platform Keys:** If executing on live production hardware, clear out your volatile storage partitions (`/tmp/mytpm`), boot into a secure unified state, and re-extend the expected firmware configuration signatures back to the physical TPM 2.0 register.
