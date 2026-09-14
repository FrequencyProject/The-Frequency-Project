# ⚡ Microcontroller Firmware Specifications & Pin Maps

## 📌 Hardware Pin Definition Matrix
- **ADC_CS_PIN:** GPIO Pin 10 (Chip Select)
- **ADC_DRDY_PIN:** GPIO Pin 4 (Data Ready Hardware Interrupt Line)

## 🛠️ Bare-Metal Architecture
- **Concurrency Protections:** Flag verification and buffer pointer modifications are wrapped in `noInterrupts()` macro blocks to eliminate active telemetry data races.
- **Fixed-Point Math:** High-speed integer operations perform 24-bit sign extensions natively on bytes to maximize microcontroller processing cycles.
