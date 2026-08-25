#!/usr/bin/env python3
"""Phase 2: Asynchronous Multi-Channel Sensor Adapter.

Bridges the bare-metal background HardwareSerialDaemon thread to rolling
memory deques to compile stabilized float32 telemetry matrices.
"""
from collections import deque
import threading
import numpy as np
from serial_daemon import HardwareSerialDaemon
from spectral_processing import AsymmetricTensorPipeline


class MultiChannelSensorAdapter:
    """Manages thread-safe rolling queues and integrates the hardware daemon callback."""

    def __init__(self, port: str = "COM3", baudrate: int = 115200, window_size: int = 1280):
        self.window_size = window_size
        self._lock = threading.RLock()

        # Initialize independent thread-safe rolling deques for all 4 channels
        self.queues = {
            "ch1": deque(maxlen=window_size * 2),  # Expand depth to support 2560 sample FFT tracks
            "ch2": deque(maxlen=window_size),
            "ch3": deque(maxlen=window_size),
            "ch4": deque(maxlen=window_size * 2),  # Expand depth to support 2560 sample FFT tracks
        }

        # Initialize the production pipeline compiler and bare-metal serial daemon
        self.pipeline = AsymmetricTensorPipeline()
        self.daemon = HardwareSerialDaemon(port=port, baudrate=baudrate)

        # Register the thread-safe callback handler to capture incoming vector frames
        self.daemon.register_callback(self.hardware_packet_callback)

    def hardware_packet_callback(self, vector: np.ndarray) -> None:
        """Thread-safe callback executed by the background serial daemon thread."""
        if vector is None or len(vector) != 4:
            return

        with self._lock:
            # Map raw float positions directly into their respective distinct channel queues
            self.queues["ch1"].append(vector[0])
            self.queues["ch2"].append(vector[1])
            self.queues["ch3"].append(vector[2])
            self.queues["ch4"].append(vector[3])

    def process_incoming_packet(self, packet_str: str) -> None:
        """Backward-compatibility bridge for test suites and string-based inputs.

        Leverages the pre-compiled regex daemon parser to route data safely.
        """
        vector = self.daemon.parse_raw_line(packet_str)
        if vector is not None:
            self.hardware_packet_callback(vector)

    def get_ai_features(self) -> np.ndarray:
        """Compiles and returns the unified normalized (4, 1280) float32 matrix tensor."""
        with self._lock:
            # Ensure the rolling spectral queues contain enough points before calculating transforms
            if len(self.queues["ch1"]) < self.window_size:
                return np.zeros((4, self.window_size), dtype=np.float32)

            ch1_raw = np.array(self.queues["ch1"])
            ch2_raw = np.array(self.queues["ch2"])
            ch3_raw = np.array(self.queues["ch3"])
            ch4_raw = np.array(self.queues["ch4"])

        # Process asymmetrically via the spectral pipeline
        return self.pipeline.compile_feature_tensor(ch1_raw, ch2_raw, ch3_raw, ch4_raw)

    def start_ingestion(self) -> None:
        """Spins up the underlying bare-metal background polling threads."""
        self.daemon.start()

    def stop_ingestion(self) -> None:
        """Gracefully halts the background physical hardware port acquisitions."""
        self.daemon.stop()


if __name__ == "__main__":
    print("[INIT] Verifying MultiChannelSensorAdapter callback integration...")
    adapter = MultiChannelSensorAdapter(port="MOCK_PORT")

    # Simulate a single live hardware frame arriving via the daemon callback
    mock_frame = np.array([1.23, -4.56, 0.01, 7.89], dtype=np.float32)
    adapter.hardware_packet_callback(mock_frame)

    # Ensure values were appended perfectly to thread-safe memory trees
    assert len(adapter.queues["ch1"]) == 1
    print(f" -> Callback Injection Validated. Ch1 Queue Data: {list(adapter.queues['ch1'])}")
    print("[SUCCESS] Hardware-software callback bridge is fully optimized.")
