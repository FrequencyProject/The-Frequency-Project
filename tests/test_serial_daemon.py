#!/usr/bin/env python3
import numpy as np
import pytest
from serial_daemon import HardwareSerialDaemon, ResilientSerialDaemon


def test_legacy_compatibility_shim() -> None:
    daemon = HardwareSerialDaemon(port="TEST")
    parsed = daemon.parse_raw_line("V1:1.0,V2:2.0,V3:3.0,V4:4.0")
    assert parsed is not None
    np.testing.assert_allclose(parsed, [1.0, 2.0, 3.0, 4.0])


def test_daemon_packet_parsing_and_extraction() -> None:
    daemon = ResilientSerialDaemon(port="TEST")
    success = daemon.ingest_packet_string("V1:1.23,V2:-0.44,V3:0.12,V4:5.67")
    assert success is True
    assert len(daemon.ch1_buffer) == 1


def test_daemon_buffer_saturation_deterministic() -> None:
    daemon = ResilientSerialDaemon(port="TEST")
    # Feed exactly 2560 programmatic steps to saturate the sliding window reliably
    for i in range(2560):
        daemon.ingest_packet_string(f"V1:{np.sin(i):.4f},V2:0.5,V3:0.2,V4:{np.cos(i):.4f}")
    tensor = daemon.get_latest_ai_tensor()
    assert tensor.shape == (4, 1280)
    assert not np.all(tensor == 0.0)
