#!/usr/bin/env python3
"""Prototype Ingestion Validation Harness.

Generates realistic mock telemetry streams and validates end-to-end 
asymmetric tensor compilation and normalization constraints.
"""
import numpy as np
from spectral_processing import AsymmetricTensorPipeline


def run_simulation_smoke_test():
    """Validates unified pipeline behavior under standard multi-rate telemetry loads."""
    print("[INIT] Starting end-to-end signal ingestion simulation pass...")
    pipeline = AsymmetricTensorPipeline()
    rng = np.random.default_rng(seed=42)

    # 1. Standard Track Validation: Generate realistic multi-rate mock data signals
    ch1_mock = rng.normal(0, 1, 2560)
    ch2_mock = rng.normal(0, 1, 1280)
    ch3_mock = rng.normal(0, 1, 1280)
    ch4_mock = rng.normal(0, 1, 2560)

    # Compile directly through the production signal pipeline
    tensor = pipeline.compile_feature_tensor(ch1_mock, ch2_mock, ch3_mock, ch4_mock)

    # System invariants validation check assertions
    assert tensor.shape == (4, 1280), f"Error: Invalid shape {tensor.shape}"
    assert tensor.dtype == np.float32, f"Error: Invalid precision {tensor.dtype}"

    # Ensure row-independent scaling yields localized zero-means and unit-variance
    np.testing.assert_allclose(tensor.mean(axis=1), 0.0, atol=1e-5)
    np.testing.assert_allclose(tensor.std(axis=1), 1.0, atol=1e-4)
    print(" -> [PASSED] Standard Multi-Rate Compilation and Z-Score centering invariants.")

        # 2. Verify Epsilon Flatline Protection
    # Simulates a disconnected hardware sensor pin broadcasting pure static zeros
    flatline_ch = np.zeros(1280, dtype=np.float32)
    flatline_ch_double = np.zeros(2560, dtype=np.float32)

    tensor_flatline = pipeline.compile_feature_tensor(flatline_ch_double, flatline_ch, flatline_ch, flatline_ch_double)
    assert np.all(np.isfinite(tensor_flatline)), "Epsilon Guard Failed: Flatline signal caused division-by-zero NaNs."
    print(" -> [PASSED] Epsilon Flatline Protection Guard.")

    # 3. EXTREME HARDENING REMEDIATION: Extreme Hardware Clipping Rails Check
    # Simulates severe voltage over-saturation spikes across physical input channels (e.g., short circuit)
    clipping_ch_high = np.full(1280, 5000.0, dtype=np.float32) # Massive static voltage rail
    clipping_ch_double = rng.normal(0, 1, 2560)
    
    tensor_clipped = pipeline.compile_feature_tensor(clipping_ch_double, clipping_ch_high, ch3_mock, clipping_ch_double)
    assert np.all(np.isfinite(tensor_clipped)), "Extreme Rail Failed: Numerical over-saturation generated invalid numbers."
    print(" -> [PASSED] Extreme Hardware Clipping Voltage Rail Guard.")
    # === END OF NEW CODE ===

    print("[SUCCESS] Simulation pipeline fully validated. (4, 1280) Ingestion system is operational.")


if __name__ == "__main__":
    run_simulation_smoke_test()
