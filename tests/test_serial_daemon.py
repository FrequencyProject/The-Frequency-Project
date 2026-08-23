#!/usr/bin/env python3
"""Unit tests verifying Serial Ingestion Daemon threading, parsing, and data retention."""
import time
import numpy as np
import pytest
from serial_daemon import ResilientSerialDaemon

def test_daemon_packet_parsing_and_extraction() -> None:
    daemon = ResilientSerialDaemon(port="TEST_PORT_HOOK")
    
    # Ingest a clean, valid streaming package packet string directly
    daemon._process_packet_string("V1:1.23,V2:-0.44,V3:0.12,V4:5.67")
    
    assert len(daemon.ch1_buffer) == 1
    assert daemon.ch1_buffer[0] == 1.23
    assert daemon.ch4_buffer[0] == 5.67

def test_daemon_window_saturation_and_tensor_generation() -> None:
    # Use MOCK mode execution to verify background calculations
    daemon = ResilientSerialDaemon(port="MOCK")
    daemon.start()
    
    try:
        # Give the background daemon loop ample time to fill buffer bounds
        time.sleep(0.5)
        tensor = daemon.get_latest_ai_tensor()
        
        assert tensor.shape == (4, 1280)
        assert tensor.dtype == np.float32
    finally:
        daemon.stop()
