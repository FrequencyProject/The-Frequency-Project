#!/usr/bin/env python3
import os
import sys
import pytest
import numpy as np

# Adjust execution path so tests can run natively from the repository root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import classes directly from our repository ingestion engine modules
from sensor_adapter import MultiChannelSensorAdapter


# ==============================================================================
# FIXTURES AND SETUP LAYER
# ==============================================================================
@pytest.fixture
def clean_adapter() -> MultiChannelSensorAdapter:
    """Provides a fresh, isolated 4-channel sensor adapter instance before every test."""
    return MultiChannelSensorAdapter(
        port="MOCK_PORT", baudrate=115200, window_size=1280
    )


# ==============================================================================
# CORE ARCHITECTURAL MATRIX ASSERTIONS
# ==============================================================================
def test_tensor_dimension_compliance(
    clean_adapter: MultiChannelSensorAdapter,
) -> None:
    """Asserts that the compiled tensor strictly outputs a 4 x 1280 shape array

    and remains zero-saturated until the sliding window is fully populated.
    """
    # 1. Verify cold startup matrix is absolutely zero-filled (un-saturated queue)
    cold_tensor = clean_adapter.get_ai_features()
    assert cold_tensor.shape == (
        4,
        1280,
    ), "Tensor boundary matrix shape must remain constant."
    assert np.all(
        cold_tensor == 0.0
    ), "Cold buffer must return absolute zeros prior to saturation."

    # 2. Feed exactly 1,280 synchronized historical data packet frames
    for _ in range(1280):
        mock_packet = "V1:10.0,V2:20.0,V3:-5.0,V4:1.2\n"
        clean_adapter.process_incoming_packet(mock_packet)

    # 3. Verify hot post-saturation matrix dimension compliance
    saturated_tensor = clean_adapter.get_ai_features()
    assert saturated_tensor.shape == (
        4,
        1280,
    ), "Saturated matrix dimension mutated from 4x1280 target."
    assert (
        saturated_tensor.dtype == np.float32
    ), "Memory contiguity constraint failed: data must compile as float32."


def test_row_independent_zscore_normalization(
    clean_adapter: MultiChannelSensorAdapter,
) -> None:
    """Verifies that the Z-Score transform scales each channel independently along axis=1,

    forcing each individual vector row to have a mean of 0 and a standard deviation of 1.
    """
    # Generate random, independent varying tracking matrices across the 4 nodes
    # np.random.default_rng provides version-stable, isolated math seeding across 3.10-3.12
    rng = np.random.default_rng(seed=42)
    mock_signals = rng.normal(
        loc=[50.0, -10.0, 0.5, 12.0],
        scale=[15.0, 2.0, 0.05, 1.1],
        size=(1280, 4),
    )

    # Multi-Version Fix: Explicitly unpack float indices to handle NumPy array string casting rules smoothly
    for frame in mock_signals:
        packet = (
            f"V1:{frame[0]:.4f},V2:{frame[1]:.4f},V3:{frame[2]:.4f},V4:{frame[3]:.4f}\n"
        )
        clean_adapter.process_incoming_packet(packet)

    normalized_tensor = clean_adapter.get_ai_features()

    # Enforce row-independent scaling validations across all 4 channels
    for ch_idx in range(4):
        ch_mean = np.mean(normalized_tensor[ch_idx, :])
        ch_std = np.std(normalized_tensor[ch_idx, :])

        # Z-Score mathematical bounds validation hooks
        assert (
            abs(ch_mean) < 1e-5
        ), f"Channel {ch_idx+1} mean shifted away from 0.0 baseline."
        assert (
            abs(ch_std - 1.0) < 1e-5
        ), f"Channel {ch_idx+1} standard deviation scaled away from unity."


# ==============================================================================
# DEFENSIVE SECURITY AND BOUNDARY PROTECTION AUDITS
# ==============================================================================
def test_malformed_string_packet_rejection(
    clean_adapter: MultiChannelSensorAdapter,
) -> None:
    """Ensures that the string parsing logic caught inside exception gates completely discards

    malformed lines or partial data dropouts without crashing or corrupting existing memory queues.
    """
    # 1. Pre-fill queue with baseline data frames
    for _ in range(1279):
        clean_adapter.process_incoming_packet("V1:1.0,V2:1.0,V3:1.0,V4:1.0\n")

    # 2. Inject adversarial malformed string packets (Simulating line cuts or serial parsing interference)
    corrupted_inputs = [
        "V1:1.0,V2:1.0,V3:1.0\n",  # Missing channel 4 vector drop
        "V1:1.0,V2:1.0,V3:BAD_DATA,V4:1.0\n",  # Text injection corruption attack
        "V1:1.0,,V3:1.0,V4:1.0\n",  # Demarcation token break split fault
        "MALFORMED HEAVY INJECTION LINE STRING\n",  # Radical out-of-bounds structure drop
    ]

    for malicious_packet in corrupted_inputs:
        clean_adapter.process_incoming_packet(malicious_packet)

    # 3. Ingestion engine must decline partial matrix state mutations
    tensor = clean_adapter.get_ai_features()
    assert np.all(
        tensor == 0.0
    ), "Corrupted inputs must be filtered at boundary and denied execution entry."


def test_epsilon_flatline_protection(
    clean_adapter: MultiChannelSensorAdapter,
) -> None:
    """Simulates a comprehensive hardware flatline/sensor dead state where variance drops to absolute zero,

    verifying that epsilon modifiers block division-by-zero exceptions across 3.10, 3.11, and 3.12 runtimes.
    """
    # Force absolute flatline array state values across all 4 sensors simultaneously
    for _ in range(1280):
        clean_adapter.process_incoming_packet("V1:0.0,V2:0.0,V3:0.0,V4:0.0\n")

    flat_tensor = clean_adapter.get_ai_features()

    assert flat_tensor.shape == (
        4,
        1280,
    ), "Flatline matrix shape must remain constant."

    # Verify that no cell contains NaN or Infinite artifacts caused by division-by-zero
    assert not np.isnan(
        flat_tensor
    ).any(), "Epsilon safety bound guard failed: NaN detected inside tensor."
    assert not np.isinf(
        flat_tensor
    ).any(), "Epsilon safety bound guard failed: Infinity detected inside tensor."
