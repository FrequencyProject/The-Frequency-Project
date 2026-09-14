# 📑 Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com) and adheres to Semantic Versioning.

## [Unreleased] - 2026-09-14

### 🚀 Added
- **Release Candidate Tag Initialization (v1.1.0-rc1):** Tagged the repository milestone for active staging.
- **Physical Hardware Verification Suite:** Created `tests/test_hardware_integration.py` to track live serial line communication limits, frame error statistics, and active sensor variances without stalling the test suite runner.
- **Hardware Runbook Foundation:** Added `HARDWARE_TESTING.md` compiling the mandatory 7-Phase physical microcontroller validation roadmap and success SLAs.
- **Frictionless Entry Paths:** Integrated `QUICKSTART.md` providing a 5-minute onboarding blueprint and decoupled research documentation into a clear `MATHEMATICAL_APPENDIX.md`.

## [Unreleased] - 2026-09-13

### 🚀 Added
- **Preregistered Hypothesis Validator:** Integrated a complete mathematical verification loop in `validate_phi_hypothesis.py` assessing golden ratio sub-harmonic channel distribution limits.

### 🔒 Security & Hardening
- **Strict Dependency Version Lock:** Hardened package boundaries by pinning `cryptography==50.0.0` inside `pyproject.toml` to completely clear remote `pip-audit` constraints.
- **Package Manifest Alignment:** Expanded the packaging setup schema to track active structural runtime files, preventing silent configuration omissions.

### 🧪 Testing
- **True Invariant Boundary Verification:** Rewrote mock isolation logic inside `tests/test_validate_config.py` to force real file data frames to pass through configuration validation logic.
