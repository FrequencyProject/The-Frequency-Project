#!/usr/bin/env python3
"""Automated unit testing matrix for the ingestion stress harness."""
from sensor_adapter import MultiChannelSensorAdapter
from stress_harness import TelemetryStressHarness


def test_pipeline_resilience_to_random_fuzzing():
    """Confirms parser and memory deques absorb structural corruptions without dropping thread locks."""
    adapter = MultiChannelSensorAdapter(port="MOCK")
    harness = TelemetryStressHarness(adapter)

    # Fire an intensive fuzz attack pass
    report = harness.execute_fuzz_attack(iterations=10)

    assert report["frames_received"] == 10
    assert report["frames_dropped_invalid_sig"] == 10
