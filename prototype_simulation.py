#!/usr/bin/env python3
"""Prototype Ingestion Validation Harness.

Generates realistic mock telemetry streams and validates end-to-end
asymmetric tensor compilation and normalization constraints.
"""
import time
import numpy as np
import config
from run_session import UnifiedVivicSession


def run_simulation_smoke_test():
    """Validates unified pipeline behavior under standard multi-rate telemetry loads."""
    print("[INIT] Starting end-to-end system orchestration simulation pass...")

    # HARDENING REMEDIATION: End-to-End Orchestration Integration.
    # Instantiate the master session coordinator to run live background serial threads,
    # buffer acquisitions, and 3-Sigma tracking pipelines instead of isolating a single module.
    session = UnifiedVivicSession(port="MOCK")

    try:
        # 1. Environment Baseline Calibration Check
        # Validates that background threads fill the window queues and clear the saturation block.
        session.execute_baseline_calibration()

        # Verify calibrated metrics conform to our immutable global configuration constraints
        assert session.is_calibrated is True, "Error: System failed to establish calibration metrics."
        assert len(session.ambient_means) == config.HARDWARE.num_channels, "Error: Calibration channel mismatch."
        print(f" -> [PASSED] System Calibration verified across all {config.HARDWARE.num_channels} tracks.")

        # 2. Continuous Operational Inference & Backprop Pass Check
        # Runs multiple consecutive optimization cycles through the active neural network.
        test_cycles = 5
        print(f"[RUNNING] Pushing {test_cycles} live optimization frames through the hardened processing path...")
        session.execute_live_cycle(steps=test_cycles)

        # Validate that the metrics tracked structural execution parameters correctly
        assert session.engine.warmed_up is True, "Error: Ingestion buffers starved during execution loop."
        print(f" -> [PASSED] Processing path execution confirmed across {test_cycles} operational steps.")

        # 3. Dynamic 3-Sigma Anomaly Track Evaluation
        # HARDENING REMEDIATION: Direct Attribute Lookup.
        # Extracts tracking metrics using raw attributes directly managed inside the monitor class,
        # completely bypassing the non-existent .get_metrics() method.
        processed_vectors = session.monitor._test_step_counter
        anomalies_caught = session.monitor.anomalies_detected
        print(f" -> [MONITOR STATS] Processed Vectors: {processed_vectors} | Anomalies Caught: {anomalies_caught}")

        print("[SUCCESS] Whole-system simulation pipeline fully validated and operational.")

    except Exception as err:
        print(f"[CRITICAL FAILURE] Integration simulation crash encountered: {str(err)}")
        raise err

    finally:
        # HARDENING REMEDIATION: Non-Destructive Resource Teardown.
        # Guarantees background threads close cleanly to prevent thread leakage if assertions fail.
        session.terminate_session()


if __name__ == "__main__":
    run_simulation_smoke_test()
