# 🛰️ ESP32-S3 Microcontroller Ingestion & Hardware Register Specification

This document codifies the strict telemetry packet structure, register layouts, and bit-level calculations enforced between the physical ESP32-S3 firmware layer (`firmware_adc_loop.cpp`) and the Python host daemon interface layer (`serial_daemon.py`).

## 1. Physical Hardware & Bus Configuration

- **Baud Rate Matrix:** `115200 bps` (Universal asynchronous interface serialization speed)
- **Data Bits / Stop Bits / Parity:** `8 / 1 / None`
- **SPI Interface Constraints:** Mode 1, MSBFIRST, running on a stable 4.0MHz bus interface clock line.
- **Hardware Pins:**
  - `GPIO 10`: ADC Chip Select (CS) Core Pin
  - `GPIO 4`: ADC Data Ready (DRDY) Input Line with an Active Falling Edge Interrupt Trigger Profile

## 2. Low-Level Telemetry Frame Structure

Data packets are processed sequentially inside a non-blocking asynchronous atomic ring buffer holding up to `8` structural slots.

### Data Word Format (24-Bit Two's Complement Integer)
Each Analog-to-Digital Converter channel samples metrics using a 24-bit signed architecture, which is extended onto standard 32-bit fields inside the micro-controller's register arrays:

| Upper Padding (8 Bits) | Sign / Magnitude Data Payload (24 Bits) |
| :---: | :---: |
| `0xFF` (Negative) / `0x00` (Positive) | `0x000000` to `0xFFFFFF` |

### Raw Fixed-Point Voltage Translation Formula
To calculate the physical voltage metrics without floating-point calculation drift inside core firmwares, raw digital counts are mapped using explicit fractional integer scaling parameters:

\[\text{Voltage (V)} = \frac{\text{Counts} \times 2.048}{8,388,607}\]

## 3. Streaming Serialization Packet Protocol

All packets are serialized across the USB-UART bridge as flat UTF-8 encoded text frames capped at a strict window ceiling limit of `256` bytes.

### Transmission Layout Formula
```text
V1:[float],V2:[float],V3:[float],V4:[float],CRC:0x[HEX_2B]
```
- **Precision Constancy:** Fixed at exactly 4 trailing decimal places.
- **CRC-8 Algorithm Details:** Dallas/Maxim algebraic polynomial rule (X⁸ + X⁵ + X⁴ + 1), represented as explicit primitive hex values initialized from an absolute `0x00` byte floor container.
