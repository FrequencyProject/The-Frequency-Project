# 🌿 The Frequency Project

Real-time edge machine learning framework for high-assurance environmental telemetry anomaly detection. The system ingests 4-channel analog inputs at 60Hz, maps raw time-series data into single-precision latent space arrays, and flags structural variations via a zero-trust 3-Sigma monitor.

## 🎯 Primary Use Cases
- **Precision Agriculture:** Tracking plant bio-potentials to predict crop dehydration.
- **Industrial IoT:** Monitoring micro-vibrations to forecast equipment failure.
- **Ecological Sentinel Networks:** Edge monitoring of environmental background fields.

## 🚀 Get Started (5 Minutes)
All onboarding, installation, and environment initialization steps have been streamlined into a single document:
👉 **See [QUICKSTART.md](QUICKSTART.md) for 5-minute local installation and verification.**

## 📖 Project Documentation Index
Detailed technical blueprints and operational guides are decoupled across dedicated tracks:
- **[QUICKSTART.md](QUICKSTART.md):** Frictionless local setup and validation test execution steps.
- **[FIRMWARE_GUIDE.md](FIRMWARE_GUIDE.md):** ESP32-S3 microcontroller pin maps, FSPI configurations, and bare-metal protection architectures.
- **[HARDWARE_TESTING.md](HARDWARE_TESTING.md):** The mandatory 7-Phase physical validation roadmap and connectivity SLAs.
- **[MATHEMATICAL_APPENDIX.md](MATHEMATICAL_APPENDIX.md):** Technical deep-dives into Lorenz chaos tracking, Wasserstein drift velocity, and informational entropy metrics.
- **[DEPLOYMENT.md](DEPLOYMENT.md):** Hardened multi-stage container optimization and Prometheus exposition setup profiles.

## 📊 Automated Verification Baseline
- **Test Matrix Status:** 61 automated tests passing completely green (`python3 -m pytest`) ✅
- **Security Hardening:** Strictly pinned to audited packages (`cryptography==50.0.0`) clearing local `pip-audit` scans ✅
- **Execution Overhead:** Single-threaded design constraints occupy < 15% core capacity on target edge processor nodes ✅

## ⚖️ Licensing
This repository is licensed under the terms of the **GNU Affero General Public License v3.0 (AGPL-3.0)**. Downstream integrations or modifications must release their source code under identical copyleft constraints. See `LICENSE` for details.
