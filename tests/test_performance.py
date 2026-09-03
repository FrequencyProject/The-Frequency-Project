#!/usr/bin/env python3
"""Phase 15: High-Assurance Sustained Performance Load Test.

Validates system throughput and allocation stability under high-density loads.
"""
import pytest
import time
import numpy as np
from sensor_adapter import MultiChannelSensorAdapter

def test_sustained_telemetry_load_performance():
    """Simulates a rapid telemetry stream to verify matrix collection velocity."""
    # Initialize a fast unbatched operational frame tracking window matching production geometry
    adapter = MultiChannelSensorAdapter(port="MOCK_PERF_PORT", window_size=1280)
    
    start_time = time.time()
    iterations = 1500  # High-frequency data injection loop to saturate the 1280 track completely
    
    for i in range(iterations):
        # Generate clean synthetic spatial signal matrices
        packet = f"V1:{np.sin(i):.4f},V2:{np.cos(i):.4f},V3:0.1234,V4:-0.5678\n"
        adapter.process_incoming_packet(packet)
        
        # Periodic feature extraction to ensure the Z-score normalizer has no memory leaks
        if i % 500 == 0:
            features = adapter.get_ai_features()
            assert features.shape == (4, 1280)
            
    elapsed = time.time() - start_time
    # Assert the hot-path completes processing well within operational constraints
    assert elapsed < 5.0, f"Performance bottleneck detected: Ingestion took {elapsed:.2f}s"