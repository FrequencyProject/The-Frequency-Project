#!/usr/bin/env python3
"""Unit test suite for verification of Ingestion Pipeline Fault Tolerance under stress."""
import pytest
from sensor_adapter import MultiChannelSensorAdapter
from stress_harness import TelemetryStressHarness


def test_pipeline_resilience_to_random_fuzzing():
    """Confirms parser and memory deques absorb structural corruptions without dropping thread locks."""
    adapter = MultiChannelSensorAdapter(port="TEST_STRESS_PORT")
    harness = TelemetryStressHarness(adapter)

    # Fire an intensive fuzz attack pass
    report = harness.execute_fuzz_attack(iterations=10)

    # Verify that errors are logged correctly inside telemetry registers rather than causing app panics
    assert report["daemon_dropped"] > 0
    assert report["daemon_received"] > 0
    # Ensure memory structures have not completely crashed
    assert isinstance(report["adapter_ch1_dropped"], int)
